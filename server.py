#  coding: utf-8 

import socketserver, os
# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Sanjeev Kotha
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

ENCODING = 'utf-8'
class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):

        self.data = self.request.recv(1024).strip()
        self.data = self.data.decode(ENCODING)
        self.requestHeader = self.data.split(" ")
        requestType = self.requestHeader[0]
        
        if requestType.upper() == "GET":

            path = self.get_path()

            # incorrect path or input
            if path == False:
                self.respond_404()
                return
        
            # it's a file
            elif path != "301":
                self.respond_200(path)
                return

        # probably any other request that is not GET
        else:
            self.respond_405()
            return

    def get_path(self):

        hasAccess = self.handle_www('www' + self.requestHeader[1])
        isFile = os.path.isfile('www' + self.requestHeader[1])
        isDir = os.path.isdir('www' + self.requestHeader[1])

        if not isFile and not isDir:
            return False

        elif not hasAccess:
            return False

        elif isDir:
            path = self.requestHeader[1]

            if path[-1] != "/":
                self.respond_301(path+'/')
                return '301'

            return 'www' + self.requestHeader[1] + "index.html"

        elif isFile:
            return 'www' + self.requestHeader[1]

        else:
            return False

    def respond_404(self):

        header = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/plain; charset={}\r\n\r\n'.format(ENCODING)
        self.request.sendall(bytearray(header,ENCODING))

    def respond_200(self,path):

        header = 'HTTP/1.1 200 OK\r\nContent-Type: text/{}; charset={}\r\n\r\n'.format(path.split(".")[1],ENCODING)
        file = open(path,'r')
        data = [line for line in file]
        data = "".join(data)
        self.request.sendall(bytearray(header+data,ENCODING))

    def respond_405(self):

        header = 'HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/plain; charset={}\r\n\r\n'.format(ENCODING)
        self.request.sendall(bytearray(header,ENCODING))

    def respond_301(self,url):

        header = 'HTTP/1.1 301 Moved Permanently\r\nLocation: {}\r\nContent-Type: text/plain; charset={}\r\n\r\n'.format(url,ENCODING)
        self.request.sendall(bytearray(header,ENCODING))

    # handler for ./www
    def handle_www(self,path):

        current = os.path.realpath("www")
        subDirs = []

        for dir in os.walk(current):
            subDirs.append(dir[0])

        actualPath = os.path.realpath(path)

        if os.path.isfile(path):
            directory = os.path.dirname(actualPath)

            if directory not in subDirs:
                return False
        
        if os.path.isdir(path):
            
            if actualPath not in subDirs:
                return False

        return True

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
