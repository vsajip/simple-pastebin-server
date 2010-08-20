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
<html class="html">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <link rel="stylesheet" type="text/css" href="http://fonts.googleapis.com/css?family=Cantarell">
        <link rel="stylesheet" type="text/css" href="http://fonts.googleapis.com/css?family=Reenie+Beanie">
        <link rel="stylesheet" type="text/css" href="%(CONTEXT_PATH)s/style.css">
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
        <link rel="stylesheet" type="text/css" href="%(CONTEXT_PATH)s/style.css">

        <script src="http://shjs.sourceforge.net/sh_main.min.js" type="text/javascript"></script>
        <script type="text/javascript" src="http://shjs.sourceforge.net/lang/sh_%(LANG)s.js"></script>
    </head>
    <body onload="sh_highlightDocument();">
        <div id="ul_parent">
            <ul id="lang_list_%(LANG)s">
                <li><a class="lang_java" href="%(CONTEXT_PATH)s/java/%(PASTEBIN_FILE_NAME)s">java</a></li>
                <li><a class="lang_python" href="%(CONTEXT_PATH)s/python/%(PASTEBIN_FILE_NAME)s">python</a></li>
                <li><a class="lang_javascript" class="" href="%(CONTEXT_PATH)s/javascript/%(PASTEBIN_FILE_NAME)s">javascript</a></li>
                <li><a class="lang_css" href="%(CONTEXT_PATH)s/css/%(PASTEBIN_FILE_NAME)s">css</a></li>
                <li><a class="lang_html" href="%(CONTEXT_PATH)s/html/%(PASTEBIN_FILE_NAME)s">html</a></li>
                <li><a class="lang_cpp" href="%(CONTEXT_PATH)s/cpp/%(PASTEBIN_FILE_NAME)s">cpp</a></li>
                <li><a class="plain" href="%(CONTEXT_PATH)s/plain/%(PASTEBIN_FILE_NAME)s">plain</a></li>
            </ul>
        </div>
	    <pre class="sh_%(LANG)s">%(CONTENT)s</pre>
    </body>
</html>
"""

STYLE_CSS = """
.html {
    background: url(http://emotionslive.co.uk/img/shadow.jpg) repeat;
}
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
a:hover {
}
ul {
    display: block;
    font-family: 'Cantarell', serif;
    font-size: 20px;
    text-shadow: none;
    border: 1px solid dotted;
    height: 100px;
    width: 80%;
    margin-top: 2%;
    margin-left: 2%;
    position: relative;
}
li {
    display: inline;
    margin-left: 5px;
}

pre {
    font-family: 'Cantarell', serif;
    font-size: 16px;
    text-shadow: none;
    background-color: white;
    margin-left: 5%;
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
    font-family: 'Reenie Beanie';
    font-weight: bold;
}

.ul_parent {
    position: absolute;
}

#lang_list_java .lang_java {
    font-weight: bold;
}
#lang_list_python .lang_python {
    font-weight: bold;
}
#lang_list_javascript .lang_javascript {
    font-weight: bold;
}
#lang_list_html .lang_html {
    font-weight: bold;
}
#lang_list_css .lang_css {
    font-weight: bold;
}
#lang_list_cpp .lang_cpp {
    font-weight: bold;
}
#lang_list_plain .lang_plain {
    font-weight: bold;
}
"""

DATA_FOLDER_NAME = "data"
DATA_FOLDER_PATH = "./" + DATA_FOLDER_NAME
URL_DATA_FOLDER = "/" + DATA_FOLDER_NAME + "/"

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.init_params()

        if self.path not in ["/favicon.ico", "/style.css", URL_DATA_FOLDER]:
            self.log_request()
            self.send_response(200)
            self.send_header("Content-Type", "text/html;charset=UTF-8")
            self.end_headers()

            if self.path == "/":
                self.wfile.write(FORM % {"CONTEXT_PATH": self.get_context_path()})

            # get the clean content: no html
            elif self.path.find("/plain/") == 0:
                filename = DATA_FOLDER_PATH + self.path[6:]
                content = self.read_file(filename)
                self.wfile.write(cgi.escape(content))

            # language(java, css) is specified
            elif len(self.path.split("/")) > 2:
                splits = self.path.split("/")
                lang = splits[1]
                self.pastebin_file_name = splits[2]
                filename = DATA_FOLDER_PATH + self.path[len(lang) + 1:]
                content = self.read_file(filename)
                self.wfile.write(CONTENT_TEMPLATE % {"LANG": lang,
                    "CONTENT":cgi.escape(content),
                    "CONTEXT_PATH": self.get_context_path(),
                    "PASTEBIN_FILE_NAME": self.pastebin_file_name})

            # no language is specified
            else:
                self.pastebin_file_name = self.path[1:]
                filename = DATA_FOLDER_PATH + self.path
                if self.path.find(URL_DATA_FOLDER) == 0:
                    filename = "." + self.path

                content = self.read_file(filename)
                self.wfile.write(CONTENT_TEMPLATE % {"LANG": "java",
                    "CONTENT":cgi.escape(content),
                    "CONTEXT_PATH": self.get_context_path(),
                    "PASTEBIN_FILE_NAME": self.pastebin_file_name})
        else:
            if self.path == "/style.css":
                self.log_request()
                self.send_response(200)
                self.send_header("Content-Type", "text/css;charset=UTF-8")
                self.end_headers()
                self.wfile.write(STYLE_CSS)
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

    def get_context_path(self):
        return "http://" + self.headers['host']

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
