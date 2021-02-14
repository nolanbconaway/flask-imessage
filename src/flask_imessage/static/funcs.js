function getUnixTime(...subtractions) {
    let utcnow = moment.utc()
    subtractions.forEach(s => utcnow.subtract(...s))
    return utcnow.valueOf() / 1000;
}

function makeLi(text) {
    let internal_li = document.createElement('li')
    internal_li.innerHTML = text
    return internal_li
}

class Message {
    constructor(data) {
        this.messageId = data.message_id
        this.senderId = data.sender_id
        this.dateUTC = new Date(data.date_unix * 1000)
        this.isFromMe = data.is_from_me
        this.text = data.message_text
    }

    get dateUnix() { return this.dateUTC.getTime() / 1000 }
    get dateLocalString() { return moment(this.dateUTC).local().format() }

    render() {
        let ul = document.createElement('ul')
        ul.appendChild(makeLi(this.text))
        ul.appendChild(makeLi('At: ' + this.dateLocalString))
        if (!this.isFromMe) ul.appendChild(makeLi('From: ' + this.senderId))
        return ul
    }
}

class Chat {
    constructor(chat_id, messages) {
        this.chatId = chat_id
        this.messages = messages.map(m => new Message(m))
        this.sortMessages()
    }

    get messageIDs() { return new Set(this.messages.map((({ messageId }) => messageId))) }
    get senderIDs() { return new Set(this.messages.map((({ senderId }) => senderId))) }
    get isGroup() { return this.senderIDs.size > 1 }
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
        let ul = document.createElement('ul')
        document.createElement('ul')
        ul.appendChild(makeLi(`Chat: ${this.chatId}`))
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
                m => !chats[chatId].messageIDs.has(m.messageId)
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
