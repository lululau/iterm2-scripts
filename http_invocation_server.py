#!/usr/bin/env python3.7

import pathlib
import os
import signal
import asyncio
import iterm2
import json
from http.server import BaseHTTPRequestHandler,HTTPServer

PID_FILE = str(pathlib.Path("~/Library/ApplicationSupport/iTerm2/http_invocation_server.pid").expanduser())

PORT_NUMBER = 28082

loop = asyncio.get_event_loop()

connection = None

async def invoke(invocation):
    global connection
    if connection == None:
        connection = await iterm2.Connection.async_create()
    return await iterm2.async_invoke_function(connection, invocation)

def save_pid():
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

def get_previous_pid():
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as f:
            pid_str = f.readline()
            return int(pid_str)
    else:
        return None

def kill_previous_process():
    pid = get_previous_pid()
    if pid != None:
        os.kill(pid, signal.SIGKILL)

kill_previous_process()
save_pid()

class InvocationHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        global loop
        self.send_response(200)
        self.send_header('Content-type','application/json; charset=UTF-8')
        self.end_headers()

        content_length = int(self.headers['Content-Length'])
        invocation = self.rfile.read(content_length)
        return_value = loop.run_until_complete(invoke(invocation))

        self.wfile.write(bytes(json.dumps(return_value), "UTF-8"))
        return

server = HTTPServer(('127.0.0.1', PORT_NUMBER), InvocationHandler)

server.serve_forever()
