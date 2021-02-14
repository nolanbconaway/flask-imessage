# Flask iMessage Server

> **NOTE**: This is a work in progress. A _lot_ does not work. I am _bad_ at software engineering.

This repo contains a flask webapp that allows users to send + receive iMessages over HTTP. Use it if you like to text on your apple computer but have another machine on which you cannot log into iCloud (i.e., a linux/windows desktop, a corporate computer that locks you out).

**Here's the idea**: You run an HTTP server on a computer that is logged in to iCloud, and hit the service address on your non-iMessage machine. The webapp reads Apple's internal SQLite database to render all known messages, and uses applescripts to send messages.

> For security reasons, the iMessage computer should be on your home network and should not be exposed to the public internet. Otherwise, _anyone can access your messages_.

## User guide

> TODO

## What works

- Sending messages to a single phone number, over iMessage or SMS.
- Receiving messages from all chats.

### Todo

In descending order of how much I care:

- [ ] docs
- [ ] unit testing for the python infra
- [ ] unit testing for the web infra
- [ ] Set up production uwsgi server that is compatible with socketio
- [ ] better grouping of chat IDs to human-readable identifiers, via contacts lookups.
- [ ] better styling generally, as of right now this is at 0% styling.
- [ ] more context on messages (delivered vs not, me vs not, read vs not, etc)
- [ ] display error messages to users (mostly after sending messages but should be general)
- [ ] Photo, video, audio attachments
- [ ] new message notifications.
- [ ] testing for sending messages to non-phone numbers (emails, etc)
- [ ] support for group chats (only at the bottom bc i do not think it is possible with applescript)
- [ ] option for password security

## Gotchas to document

- Problems with accessing the database
- How to set up clamshell/headless mode