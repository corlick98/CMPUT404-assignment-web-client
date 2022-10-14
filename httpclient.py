#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def extract_url_parts(self, url):
        """
        Extract the host, port, and path from the url
        """
        parsed = urllib.parse.urlparse(url)
        port = parsed.port if parsed.port else 80
        path = parsed.path if parsed.path else "/"
        host = parsed.hostname
        if host is None:
            if path.find("/") == -1:
                path += "/"
            host = path[0:path.find("/")]
            path = path[path.find("/"):]
        return host, port, path

    def get_code(self, data):
        # split at spaces and extract code
        return int(data.split()[1])

    def get_headers(self,data):
        # remove body
        headers = data.split("\r\n\r\n")[0]
        # remove status line
        headers = headers.splitlines()[1:]
        headers_dict = {}
        for line in headers:
            split = line.split(":")
            headers_dict[split[0]] = ':'.join(split[1:])
        return headers_dict

    def get_body(self, data):
        # remove status line and headers
        body = data.split("\r\n\r\n")[1:]
        return "\r\n\r\n".join(body)
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        host, port, path = self.extract_url_parts(url)
        self.connect(host, port)
        # create status line and headers
        body = "GET {path} HTTP/1.1\r\n".format(path=path)
        body += "Host: {host}:{port}\r\n".format(host=host, port=port)
        body += "Connection: close\r\n"
        body += "Accept: */*\r\n\r\n"

        # send the request
        self.sendall(body)
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port, path = self.extract_url_parts(url)
        self.connect(host, port)
        # create status line and headers
        body = "POST {path} HTTP/1.1\r\n".format(path=path)
        body += "Host: {host}:{port}\r\n".format(host=host, port=port)
        body += "Connection: close\r\n"
        form_body = ""
        if args != None:
            form_body = urllib.parse.urlencode(args)
            body += "Content-Type: application/x-www-form-urlencoded\r\n"
        body += "Content-Length: {}\r\n\r\n".format(len(form_body))
        body += form_body

        # send the request
        self.sendall(body)
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
