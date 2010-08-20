#!/usr/bin/python
#-*- coding: utf8 -*-

#
# Author: xumingming64398966
# License: GPL
# Version: 0.1
# Homepage: http://code.google.com/p/simple-pastebin-server/
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


# the port to listen on
HTTP_PORT = 80

FORM = """
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <link rel="stylesheet" type="text/css" href="http://fonts.googleapis.com/css?family=Cantarell">
        <style>
        body {
              font-family: 'Cantarell', serif;
              font-size: 48px;
              text-shadow: 4px 4px 4px #aaa;
        }
        textarea {
              font-family: 'Cantarell', serif;
              font-size: 16px;
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
            background-color:#eef;
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
            <textarea name="content" rows="20" class="content"></textarea>
            <a href="javascript:document.forms[0].submit()" class="button">Paste</a>
        </form>
    </body>
</html>
"""

CONTENT_TEMPLATE = """
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <link rel="stylesheet" type="text/css" href="http://fonts.googleapis.com/css?family=Droid+Sans+Mono">
        <link rel="stylesheet" type="text/css" href="http://shjs.sourceforge.net/sh_style.css">
        <script src="http://shjs.sourceforge.net/sh_main.min.js" type="text/javascript"></script>
        <script type="text/javascript" src="http://shjs.sourceforge.net/lang/sh_%(LANG)s.js"></script>
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
    <body onload="sh_highlightDocument();">
	    <pre class="sh_%(LANG)s">%(CONTENT)s</pre>
    </body>
</html>
"""

DATA_FOLDER_NAME = "data"
DATA_FOLDER_PATH = "./" + DATA_FOLDER_NAME
URL_DATA_FOLDER = "/" + DATA_FOLDER_NAME + "/"

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.init_params()

        if self.path not in ["/favicon.ico", URL_DATA_FOLDER]:
            self.log_request()
            self.send_response(200)
            self.send_header("Content-Type", "text/html;charset=UTF-8")
            self.end_headers()

            if self.path == "/":
                self.wfile.write(FORM)

            # get the clean content: no html
            elif self.path.find("/plain/") == 0:
                filename = DATA_FOLDER_PATH + self.path[6:]
                content = self.read_file(filename)
                self.wfile.write(cgi.escape(content))
            elif len(self.path.split("/")) > 2:
                splits = self.path.split("/")
                lang = splits[1]
                filename = DATA_FOLDER_PATH + self.path[len(lang) + 1:]
                content = self.read_file(filename)
                self.wfile.write(CONTENT_TEMPLATE % {"LANG": lang, "CONTENT":cgi.escape(content)})
            else:
                filename = DATA_FOLDER_PATH + self.path
                if self.path.find(URL_DATA_FOLDER) == 0:
                    filename = "." + self.path

                content = self.read_file(filename)
                self.wfile.write(CONTENT_TEMPLATE % {"LANG": "java", "CONTENT":cgi.escape(content)})
        else:
            return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        self.init_params()

        if self.path == "/pasteit":
            filename = str(uuid.uuid1())
            f = open(DATA_FOLDER_PATH + "/" + filename, "w")
            f.write(self.params["content"])
            f.close()

            self.send_response(302)
            self.send_header("Location", "/" + filename)
            self.end_headers()


    def read_file(self, filename):
        f = open(filename)
        content = f.read()
        f.close()

        return content

    def init_params(self):
        """Get the params from url and request body
        """

        # init the params
        self.params = {}

        # get the params in query string
        if self.path.find('?') != -1:
            self.path, qs = self.path.split("?", 1)

            for pair in qs.split("&"):
                key, value = pair.split("=")
                self.params[key] = value

        if self.command == "POST":

            clength = int(self.headers.dict['content-length'])
            content = self.rfile.read(clength)

            for pair in content.split("&"):
                key, value = pair.split("=")
                self.params[key] = urllib.unquote_plus(value)


httpd = BaseHTTPServer.HTTPServer(('', HTTP_PORT), MyHandler)
httpd.serve_forever()
