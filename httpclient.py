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

    # if specified then the port in the parse otherwise 80
    def get_port(self, parse):
        if parse.port == None:
            return 80
        return parse.port

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    # get the code from response
    def get_code(self, data):
        status = data.split("\r\n")[0].split()
        code = status[1]
        return int(code)

    # get the header from response
    def get_headers(self,data):
        header = data.split("\r\n\r\n", 1)[0]
        return header

    # get the body from response
    def get_body(self, data):
        body = data.split("\r\n\r\n", 1)[-1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # encode the post data
    def get_post_data(self, args):
        if args == None:
            return 0, ''
        else:
            post_data = urllib.parse.urlencode(args)
            return len(post_data), post_data

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

    # get method
    def GET(self, url, args=None):
        parse = urllib.parse.urlparse(url)
        host = socket.gethostbyname(parse.netloc.split(":")[0])
        self.connect(host, self.get_port(parse))
        path = parse.path
        if path == '':
            path = '/'
        request = "GET "+ path + " HTTP/1.1\r\n"+"Host: "+parse.netloc+"\r\n"
        request += "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0\r\nConnection: close\r\n"

        request += "Accept: */*\r\n\r\n"
        self.sendall(request)

        self.socket.shutdown(socket.SHUT_WR)
        response = self.recvall(self.socket)

        self.close()

        code = self.get_code(response)

        body = self.get_body(response)
        return HTTPResponse(code, body)

    # post method
    def POST(self, url, args=None):
        parse = urllib.parse.urlparse(url)
        host = socket.gethostbyname(parse.netloc.split(":")[0])
        self.connect(host, self.get_port(parse))

        length, post_data = self.get_post_data(args)
        path = parse.path
        if path == '':
            path = '/'
        request = "POST "+ path + " HTTP/1.1\r\n"+"Host: "+parse.netloc+"\r\n"
        request += "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0\r\nConnection: close\r\n"
        request += "Content-Type: application/x-www-form-urlencoded\r\n"
        request += "Content-Length: " + str(length) + "\r\nAccept: */*\r\n\r\n" + post_data
        self.sendall(request)

        self.socket.shutdown(socket.SHUT_WR)
        response = self.recvall(self.socket)

        self.close()

        code = self.get_code(response)

        body = self.get_body(response)
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
