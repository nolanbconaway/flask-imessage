function userInputPoll(event) {
    // Handle input to the message textarea.
    let areaValue = document.getElementById("userMessage").value
    let submitButton = document.getElementById('submitMessage')

    // disable submit if a group message or no text
    if (currentChat.isGroup || areaValue.trim() === "") {
        submitButton.disabled = true
        submitButton.classList = 'btn btn-sm btn-secondary'
        return
    }

    // otherwise, undisable submit
    if (submitButton.disabled) {
        submitButton.disabled = false
        submitButton.classList = 'btn btn-sm btn-primary'
    }

    // nothing left to do if this function was manually called (i.e., no event passed)
    if (event === undefined) return

    // submit if enter key event without modifier
    if (event.which === 13 && !(event.ctrlKey || event.shiftKey)) {
        submitButton.click()
    }
}

class Message {
    constructor(data) {
        this.messageId = data.message_id
        this.senderId = data.sender_id
        this.senderName = data.sender_name || data.sender_id
        this.dateUTC = new Date(data.date_unix * 1000)
        this.isFromMe = data.is_from_me
        this.accountGuid = data.account_guid
        this.text = data.message_text
    }

    get dateUnix() { return this.dateUTC.getTime() / 1000 }
    minutesAgo() { return (new Date() - this.dateUTC) / 1000 / 60 }
    relativeTime() {
        let mins = this.minutesAgo()
        if (mins < 60) return `${Math.round(mins)}m`
        if (mins <= 1440) return `${Math.round(mins / 60)}h`
        return `${Math.round(mins / (60 * 24))}d`
    }

    render() {
        let container = document.createElement('div')
        container.classList.add('d-table-row')

        let div = document.createElement('div')
        div.classList.add('d-table-cell')
        div.classList.add('messageContainer')

        let messageElement = document.createElement('span')
        messageElement.classList.add('messageText')
        messageElement.title = this.relativeTime() + ' ago'

        messageElement.classList.add(this.isFromMe ? "messageFromSelf" : "messageFromOther")
        messageElement.classList.add(`float-${this.isFromMe ? "right" : "left"}`)
        messageElement.classList.add(`text-${this.isFromMe ? "right" : "left"}`)

        messageElement.innerHTML = this.text

        div.appendChild(messageElement)
        container.appendChild(div)
        return container
    }
}

class Chat {
    constructor(chat_id, messages) {
        this.chatId = chat_id
        this.participantPhones = this.chatId.split(',')
        this.messages = messages.map(m => new Message(m))
        this.sortMessages()
    }

    getParticipantInfo(key) {
        // get a mapping of numbers to key values for all participants. values will be
        // null if the participant has not sent a message or does not have that value 
        // assigned.
        let result = {}
        let messages = this.sortMessages()
        function f(p) {
            let lastMessage = messages.find(m =>
                !m.isFromMe
                && m.senderId === p
                && m[key] !== undefined && m[key] !== null
            )
            result[p] = lastMessage === undefined ? null : lastMessage[key]
        }
        this.participantPhones.forEach(f)
        return result
    }

    get messageIds() { return new Set(this.messages.map((({ messageId }) => messageId))) }
    get isGroup() { return this.participantPhones.length > 1 }
    get replyTo() { return this.lastNotFromMeMessage().senderId }

    lastNotFromMeMessage() {
        this.sortMessages()
        let notMe = this.messages.filter(x => !x.isFromMe).slice(-1)
        return notMe.length > 0 ? notMe[0] : null
    }

    lastMessage() {
        this.sortMessages()
        return this.messages.slice(-1)[0]
    }

    sortMessages() {
        // sort in order of time.
        this.messages.sort((a, b) => a.dateUnix - b.dateUnix)
        return this.messages
    }

    sidebarElement() {
        // make the internal HTML of a chat sidebar element
        let senderNames = this.getParticipantInfo('senderName')
        let participantNames = this.participantPhones.map(x => senderNames[x] || x)
        let div = document.createElement('div')
        div.title = this.lastMessage().relativeTime() + ' ago'
        div.innerHTML = `
        <span class="float-left font-weight-bold">${participantNames.join(', ')}</span>
        <br>
        <span class="sidebarChatMessage">${this.lastMessage().text}</span>
        `
        return div
    }

    renderMessages() {
        // Render this chat's messages in the main area
        let messageList = document.getElementById('messageList')
        messageList.innerHTML = ''

        this.sortMessages().forEach(function (message) {
            messageList.appendChild(message.render())

        })

        // enable or disable the user input
        let textArea = document.getElementById('userMessage')
        let submitButton = document.getElementById('submitMessage')

        // handle text area contents
        // if a group chat: disable
        //  -- else if was previously disabled: enable and clear
        //  -- else if chat focus has changed: clear
        if (this.isGroup) {
            textArea.disabled = true
            textArea.value = "This application does not support group chats!"
            submitButton.disabled = true
            submitButton.classList = 'btn btn-sm btn-secondary'
        } else if (textArea.disabled) {
            textArea.disabled = false
            submitButton.disabled = true
            submitButton.classList = 'btn btn-sm btn-secondary'
            textArea.value = ""
        } else if (currentChat === null || this.chatId != currentChat.chatId) {
            textArea.value = ""
            submitButton.disabled = true
            submitButton.classList = 'btn btn-sm btn-secondary'
        }

        // auto scroll to bottom
        let right = document.getElementById('right')
        right.scrollTop = right.scrollHeight - right.clientHeight
        currentChat = this // make sure to update global state

        // rerender the chats to highlight the current chat
        renderChats()
    }
}

function mergeChats(data) {
    // Merge a set of new chat objects into the existing data. 
    // Uses global variable `chats`
    const newChats = Object.entries(data).map(e => new Chat(...e))
    const isFirstUpdate = Object.keys(chats).length === 0
    let recievedMessages = []  // messages not from me that are new

    // find the right spot for each new chat in the existing data.
    newChats.forEach(function (chat) {
        const chatId = chat.chatId
        if (chatId in chats) {
            let newMessages = chat.messages.filter(m => !chats[chatId].messageIds.has(m.messageId))
            chats[chatId].messages.push(...newMessages)
            recievedMessages.push(...newMessages.filter(m => !m.isFromMe))
        } else {
            chats[chatId] = chat
            recievedMessages.push(...chat.messages.filter(m => !m.isFromMe))
        }
        chats[chatId].sortMessages()
    })

    // notify if new messages
    if (recievedMessages.length > 0) {
        console.log(`Received ${Object.keys(newChats).length} message(s)!`)
        if (!isFirstUpdate) playNotificationSound()
    }

    return chats
}

function renderChats() {
    // Render the left-sidebar chat's list
    // Uses global variable `chats`
    let chatList = document.getElementById('chatList')
    chatList.innerHTML = ''

    let sortedChats = Object.values(chats).sort(
        (a, b) => b.lastMessage().dateUnix - a.lastMessage().dateUnix
    )

    let div = document.createElement('div')
    sortedChats.forEach(function (chat) {
        let row = document.createElement('div')
        row.appendChild(chat.sidebarElement())
        row.onclick = function () {
            chat.renderMessages()
            setCookie('lastChatViewed', chat.chatId)
        }
        if (currentChat !== null && currentChat.chatId === chat.chatId) {
            row.id = 'currentSideBarChat'
        }
        div.appendChild(row)
    })
    chatList.appendChild(div)
}
