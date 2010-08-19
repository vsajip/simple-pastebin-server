#!/usr/bin/python
#-*- coding: utf8 -*-

#
# Author: xumingming64398966
# License: GPL
# Version: 0.1
#
# How to run:
# 1. mkdir data
# 2. python pastebin-server.py
#

import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

import uuid
import os
import urllib
import cgi

FORM = """
<html>
    <head>
        <link rel="stylesheet" type="text/css" href="http://fonts.googleapis.com/css?family=Cantarell">
        <style>
        body {
              font-family: 'Cantarell', serif;
              font-size: 48px;
              text-shadow: 4px 4px 4px #aaa;
        }
        a {
              text-decoration: none;
        }

        .content {
            width: 80%;
            height: 80%;
            margin-left: 10%;
            margin-top: 1%;
            display: block;
            background-color:#dfd;
            border: solid 1px dotted;
        }
        .button {
            display:block;
            width:100px;
            height:50px;
            margin-left:45%;
        }
        </style>
    </head>
    <body style="font-size: 50">
        <form action="/pasteit" method="POST">
            <textarea name="content" class="content"></textarea>
            <a href="javascript:document.forms[0].submit()" class="button">Paste</a>
        </form>
    </body>
</html>
"""

CONTENT_TEMPLATE = """
<html>
    <head>
        <link rel="stylesheet" type="text/css" href="http://fonts.googleapis.com/css?family=Droid+Sans+Mono">
        <style>
        body {
              font-family: 'Droid Sans Mono', serif;
              font-size: 15px;
        }
        a {
              text-decoration: none;
        }
        </style>
    </head>
    <body>
	<pre>%s</pre>
    </body>
</html>
"""
class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/data/":
            self.log_request()
            self.send_response(200)
            self.send_header("Content-Type", "text/html;charset=utf8")
            self.end_headers()

            if self.path == "/":
                self.wfile.write(FORM)
            else:
                filename = "./data" + self.path
                if self.path.find("/data/") == 0:
                    filename = "." + self.path

                f = open(filename)
                content = f.read()
                f.close()
                self.wfile.write(CONTENT_TEMPLATE % cgi.escape(content))
        else:
            return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/pasteit":
            filename = str(uuid.uuid1())
            f = open("./data/" + filename, "w")
            clength = int(self.headers.dict['content-length'])
            content = self.rfile.read(clength)
            content = urllib.unquote_plus(content)
            f.write(content[8:])
            f.close()
            self.send_response(302)
            self.send_header("Location", "/" + filename)
            self.end_headers()

httpd = BaseHTTPServer.HTTPServer(('', 80), MyHandler)
httpd.serve_forever()
