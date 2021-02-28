# Flask iMessage Server

![Lint + Test (Python)](https://github.com/nolanbconaway/flask-imessage/workflows/Lint%20+%20Test%20(Python)/badge.svg?event=push)
[![codecov](https://codecov.io/gh/nolanbconaway/flask-imessage/branch/main/graph/badge.svg?token=G053KV5WHB)](https://codecov.io/gh/nolanbconaway/flask-imessage)

> **NOTE**: This is a work in progress. A _lot_ does not work. I am _bad_ at software engineering. See the issues page for a subset of things that I know about and that bother me. If you're here, you should contribute!

This repo contains a flask webapp that allows users to send + receive iMessages over HTTP. Use it if you like to text on your apple computer but have another machine on which you cannot log into iCloud (i.e., a linux/windows desktop, a corporate computer that locks you out).

**Here's the idea**: You run an HTTP server on a computer that is logged in to iCloud, and hit the service address on your non-iMessage machine. Apple maintains an internal SQLite3 database (`~/Library/Messages/chat.db`). The webapp reads that database to render all known messages, and uses applescripts to send messages.

> For security reasons, the iMessage computer should be on your home network and should not be exposed to the public internet. Otherwise, _anyone can access your messages_.

## User guide


Before you begin, know that `flask_imessage` requires _a lot_ of permissions. This application is doing a lot of stuff that Apple (rightfully) wants to prevent applications from doing, such as reading/sending your messages and controlling your computer via applescripts.

You'll need to set up permissions for each of these cases in your Security + privacy settings. The following shell commands can help verify that everything is correctly permissioned:

- Accessing the SQLite data:

```sh
$ sqlite3 ~/Library/Messages/chat.db
```

A SQLite command prompt should open up in your terminal. You'll definitely get a permissions error the first try; see [this SO post](https://apple.stackexchange.com/questions/208478) if granting full disk access doesn't do the trick.

- Checking contacts access via applescript:

```sh
$ osascript src/flask_imessage/osascript/get_contacts.applescript
```

This'll take a minute or two, but if everything's good to go then a TSV file should print to the console.

### Setup

1. **Set up a Python 3.8 venv**, however you like.
2. **Install the application** by cloning it: `git clone https://github.com/nolanbconaway/flask-imessage.git`.
3. **`cd`** into the project.
4. **Install the python requirements** via `pip install -e .`. This'll install flask and some flask extensions.
5. **Seed the cached contacts data** via `osascript src/flask_imessage/osascript/get_contacts.applescript > src/flask_imessage/.cache/contacts.tsv`.
6. **Run the HTTP server** via `python -m flask_socketio.serve`. The application should be serving on port 5000.
7. **Open a web browser on the server** to `http://localhost:5000` and make sure it's running. 
8. **Send yourself a message from the server** so that Apple prompts you to allow scripts to send messages.
9.  **Open a web browser on the client** to `http://<server_address>:5000` and enjoy!


### Hangups, sharp parts, and everything else that can go wrong

I'll add items here as they are surfaced. Right now this section only contains what I remember.

#### I don't see all my messages!

The application by default will serve the last 365 days of messages _that are known to your computer's iMessage application_. If you want older messages, you'll need to edit the source code (it's not hard!). If you can't see newer messages, then probably you _also_ cannot see them in your iMessage application. If you can't see messages in the webapp that _do_ exist in iMessage, **file an issue on github**!

#### My address book information isn't complete!

I know. Right now the best I've got is an applescript that maps names to phone numbers. It takes too long to run and I have no way of verifying that it is complete. In real life, contact entity resolution is a very complicated thing. Sorry.

Also, the way I have set up contact resolution is NOT GOOD, so there are fixable reasons this might not be a good experience. PR's welcome y'all.

#### My messages are not syncing when the server is headless

It looks like Apple does not check for new messages on Macbooks when the lid is closed. I am working on some solutions but for now it looks like the best option is to keep the lid open. LMK if you know of a fix!
