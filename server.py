#!/usr/bin/env python

import base64
import json
import os
import time
import traceback
import urllib.parse

from settings import KibanaSettings, TokenManager
from kibana import KibanaRequester
from base import BaseHandler
from apprascunho import MainHandler

from tornado.options import define, options, parse_command_line
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.web

define("port", default=16180, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")

def main():
    try:
        tornado.options.parse_command_line()
        application = tornado.web.Application(
            [
                (r"/", MainHandler),
                #(r"/kibana", KibanaHandler),
                #(r"/request", RequestsHandler),
                ],
            cookie_secret="s3cr3t154g00ds3cr3t",
            xsrf_cookies=False,
            debug=options.debug,
            )
        application.settings['kibana'] = KibanaRequester(TokenManager(KibanaSettings.TOKEN_FILE,
                                                        KibanaSettings.OAUTH_CLIENT_ID,
                                                        KibanaSettings.OAUTH_CLIENT_SECRET,
                                                        KibanaSettings.SCOPES,
                                                        KibanaSettings.COMMANDS))

        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(options.port)
        print("Serving on port {0}".format(options.port))
        tornado.ioloop.IOLoop.current().start()
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    main()
