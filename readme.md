# Flask iMessage Server

![Lint + Test (Python)](https://github.com/nolanbconaway/flask-imessage/workflows/Lint%20+%20Test%20(Python)/badge.svg?event=push)
[![codecov](https://codecov.io/gh/nolanbconaway/flask-imessage/branch/main/graph/badge.svg?token=G053KV5WHB)](https://codecov.io/gh/nolanbconaway/flask-imessage)

> **NOTE**: This is a work in progress. A _lot_ does not work. I am _bad_ at software engineering.

This repo contains a flask webapp that allows users to send + receive iMessages over HTTP. Use it if you like to text on your apple computer but have another machine on which you cannot log into iCloud (i.e., a linux/windows desktop, a corporate computer that locks you out).

**Here's the idea**: You run an HTTP server on a computer that is logged in to iCloud, and hit the service address on your non-iMessage machine. Apple maintains an internal SQLite3 database (`~/Library/Messages/chat.db`). The webapp reads that database to render all known messages, and uses applescripts to send messages.

> For security reasons, the iMessage computer should be on your home network and should not be exposed to the public internet. Otherwise, _anyone can access your messages_.

## User guide

This is the bare minimum setup flow:

1. **Set up a Python 3.8 venv**, however you like.
2. **Install the application** by cloning it: `git clone https://github.com/nolanbconaway/flask-imessage.git`.
3. **`cd`** into the project.
4. **Install the python requirements** via `pip install -e .`. This'll install flask and some flask extensions.
5. **Seed the cached contacts data** via `osascript src/flask_imessage/osascript/get_contacts.applescript > src/flask_imessage/.cache/contacts.tsv`. This takes a minute and will also prompt you for permissions. 
6. **Run the HTTP server** via `python -m flask_socketio.serve`. The application should be serving on port 5000.
7. **Open a web browser on the server** to `http://localhost:5000` and make sure it's running. 
8. **Send yourself a message from the server** so that Apple prompts you to allow scripts to send messages.
9.  **Open a web browser on the client** to `http://<server_address>:5000` and enjoy!


### Hangups, sharp parts, and everything else that can go wrong

I'll add items here as they are surfaced. Right now this section only contains what I remember.

#### Permission denied to `~/Library/Messages/chat.db`

This is very common. `~/Library/Messages/chat.db` is a database that apple maintains to store all historical messages. For good reason, they keep this file guarded! 

You may only need to go to System Preferences > Security + Privacy, and give Full Disk Access permissions to Python and your Terminal application. But that didn't end up working for me. I had to 
disable System Integrity protection via `csrutil disable`. See [this SO post](https://apple.stackexchange.com/questions/208478).

The easiest way to check you can access the file is via:

```sh
sqlite3 ~/Library/Messages/chat.db
```

#### I don't see all my messages!

The application by default will serve the last 365 days of messages _that are known to your computer's iMessage application_. If you want older messages, you'll need to edit the source code (it's not hard!). If you can't see newer messages, then probably you _also_ cannot see them in your iMessage application. If you can't see messages in the webapp that _do_ exist in iMessage, **file an issue on github**!

#### My address book information isn't complete!

I know. Right now the best I've got is an applescript that maps names to phone numbers. It takes too long to run and I have no way of verifying that it is complete. In real life, contact entity resolution is a very complicated thing. Sorry.

Also, the way I have set up contact resolution is NOT GOOD, so there are fixable reasons this might not be a good experience. PR's welcome y'all.

## What works

- Sending messages to a single phone number, over iMessage or SMS.
- Receiving messages from all chats.

### Todo

In descending order of how much I care:

- [x] docs
- [x] unit testing for the python infra
- [ ] unit testing for the web infra (is selenium really the only option?)
- [x] better grouping of chat IDs to human-readable identifiers, via contacts lookups.
- [ ] better styling generally, as of right now this is at 0% styling.
- [ ] more context on messages 
  - [x] self vs other sent
  - [ ] delivered vs not
  - [ ] read vs not
  - [ ] imessage vs sms
  - [ ] who sent it (in case of group chat)
- [ ] display error messages to users (mostly after sending messages but should be general)
- [ ] Photo, video, audio attachments
- [ ] new message notifications.
- [ ] testing for sending messages to non-phone numbers (emails, etc)
- [ ] support for group chats
- [ ] option for password security
- [ ] save user chat selection across sessions or something.
- [x] Set up production wsgi server that is compatible with socketio
- [ ] mark messages as read when they are read
- [ ] read contacts faster via internal SQLite db.
- [ ] set up chat metadata layer so that contact info can be resolved better
- [ ] clickable links.


## Gotchas to document

- How to set up clamshell/headless mode