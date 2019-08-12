#!/usr/bin/env python3.7

import asyncio
import iterm2
import json
from http.server import BaseHTTPRequestHandler,HTTPServer

PORT_NUMBER = 28082

loop = asyncio.get_event_loop()

connection = None

async def invoke(invocation):
    global connection
    if connection == None:
        connection = await iterm2.Connection.async_create()
    return await iterm2.async_invoke_function(connection, invocation)

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
