# System & Program Design

For the server, we implemented a RESTful API interface based on Tornado web
server framework, written in Python 3. With such interface, clients can simply
use HTTP GET and POST requests to access the API, making client implementation
easier, especially for Javascript-based clients. The database tables are simply
in-memory Python dictionaries, which are loaded/saved to `db.json` on server
start/exit. Access to the chatrooms are authenticated by tokens and room ids
which are random SHA-256 hashes, so basic safety is guaranteed.

For the client, we provide two versions, the web-based (HTML/CSS/JS) client and
a Python client. With the server's RESTful API, communication to the server is
easily implemented either natively (Javascript AJAX) or with built-in libraries
(Python's `http.client`).

# Protocol Specification

| Method |    URI    |      Request      | Response | Description |
| ------ | --------- | ----------------- | -------- | ----------- |
|  POST  | /login    | user=aaa&pass=bbb | {token: xxx} | Login with provided username & password. Returns token for identification. |
|  POST  | /register | user=aaa&pass=bbb | {} | Register with provided username & password. |
|  GET   | /refresh  | token=xxx         | {userlist: [{username:meow, online:true/false}, ...], rooms:[{"id": room_id, "users":["aaa", ...]}, ...]} | Refresh user status, get user list and room list (user will be logged out without refreshing in 15 secs) |
|  POST  | /mkroom   | token=xxx&user=aaa&user=bbb&... | {room_id: hash} | Create a room with provided users. Must contain the user logged in itself. |
|  GET   | /getmsg   | token=xxx&room=room_id&last=last_msg_time | {msgs: [{time: 1421053100, from: "meow", msg: "OAO"}, ...]} | Get message since last_msg_time, returns immediately if message available, or wait until new message arrives (long polling). |
|  POST  | /sendmsg  | token=xxx&room=room_id&msg=OAO | {} | Send message to given room. |
|  GET   | /getfile  | token=xxx&file=file_id | binary file | Retrieves the file identified by file_id (hash). |
|  POST  | /sendfile | token=xxx&room=room_id&file=..... | {} | Uploads file in `form/multipart` MIME format, then sends the download link to given room. |

Each response includes a additional field "result: true/false" to indicate if the command is executed correctly.

If result == False, there will be another field "msg" telling the user what went wrong.

# User & Operator Guide

## Server usage

* Requirments: Python3, tornado (pip3 install tornado)

```./server.py``` (with exec privileges) to start server.

## Web-based UI

Web-based UI uses javascript (jQuery) AJAX calls to access server APIs.

Usage: open `login.html` with your browser.

## Commandline UI

### Documented commands (type `help <topic>`):

help

### Undocumented commands:

avaliable_rooms, getmsg, login, mkroom, register, sendmsg, userlist

* avaliable_rooms: Show the rooms you are in and show who is in these room.

* getmsg [room_idx]: Given the index of the room showed in the command
  "avaliable_rooms", get the messages in that room since last time call
  "getmsg". Note that if there is no previous message in that room, it will
  block until any message appear in that room.

* login [username] [password]

* mkroom [users ...]: Create a room that will include the users you want to have
  conversation with.

* register [username] [password]

* sendmsg [room_idx] [message]: Send message to index of the room showed in the
  command "avaliable_rooms".

* userlist: Show all the avaliable users in the server.