function makeLi(text) {
    let internal_li = document.createElement('li')
    internal_li.innerHTML = text
    return internal_li
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
    get dateLocalString() { return moment(this.dateUTC).local().format() }

    render() {
        let ul = document.createElement('ul')
        ul.appendChild(makeLi(this.text))
        ul.appendChild(makeLi('At: ' + this.dateLocalString))
        if (!this.isFromMe) ul.appendChild(makeLi('From: ' + this.senderName))
        return ul
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
    get isGroup() { return this.participant_names.size > 1 }
    get replyTo() { return this.lastNotFromMeMessage.senderId }

    get lastNotFromMeMessage() {
        this.sortMessages()
        let notMe = this.messages.filter(x => !x.isFromMe).slice(-1)
        return notMe.length > 0 ? notMe[0] : null
    }

    get lastMessage() {
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
        let participantNames = Object.values(this.getParticipantInfo('senderName'))
        console.log(participantNames)
        let ul = document.createElement('ul')
        document.createElement('ul')
        ul.appendChild(makeLi(`Chat: ${participantNames.join(', ')}`))
        ul.appendChild(makeLi(`Message: ${this.lastMessage.text}`))
        ul.appendChild(makeLi(`As of: ${this.lastMessage.dateLocalString}`))
        return ul
    }

    renderMessages() {
        // Render this chat's messages in the main area
        let messageList = document.getElementById('messageList')
        messageList.innerHTML = ''

        let table = document.createElement('table')
        this.sortMessages().forEach(function (message) {
            let tr = document.createElement('tr')
            tr.appendChild(message.render())
            table.appendChild(tr)
        })
        messageList.appendChild(table)

        // auto scroll to bottom
        let right = document.getElementById('right')
        right.scrollTop = right.scrollHeight - right.clientHeight

        currentChat = this // make sure to update global state
    }
}

function mergeChats(data) {
    // Merge a set of new chat objects into the existing data. 
    // Uses global variable `chats`
    let newChats = Object.entries(data).map(e => new Chat(...e))

    newChats.forEach(function (chat) {
        let chatId = chat.chatId
        if (chatId in chats) {
            chats[chatId].messages.push(...chat.messages.filter(
                m => !chats[chatId].messageIds.has(m.messageId)
            ))
        } else {
            chats[chatId] = chat
        }
        chats[chatId].sortMessages()
    })
    return chats
}

function renderChats() {
    let chatList = document.getElementById('chatList')
    chatList.innerHTML = ''

    let sortedChats = Object.values(chats).sort(
        (a, b) => b.lastMessage.dateUnix - a.lastMessage.dateUnix
    )

    let table = document.createElement('table')
    sortedChats.forEach(function (chat) {
        let tr = document.createElement('tr')
        tr.appendChild(chat.sidebarElement())
        tr.onclick = function () { chat.renderMessages() }
        table.appendChild(tr)
    })
    chatList.appendChild(table)
}
