#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import json
import os
import traceback
import urllib, urllib.parse, urllib.request, urllib.response
import requests
import sys
#from requests_toolbelt import MultipartEncoder

import tornado.gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
import tornado.ioloop
import tornado.web

from kibana import KibanaRequester
from requester import Requester
from settings import KibanaSettings


# Global parameters
bearer = '<BOT_ACCESS_TOKEN>'
bot_email = 'logapp@webex.bot'
bot_name = 'Logapp'
url = 'https://api.ciscospark.com/v1'

headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/json;charset=UTF-8",
            "authorization": "Bearer " + bearer}


class MainHandler(tornado.web.RequestHandler):

    def handle_text(self, text):
        result = None
        if text.lower().startswith('help'):
            result = self.help_me()
        if text.lower().startswith('logapphelp'):
            result = self.help_me()
        if text.lower().startswith('trackingid'):
            result = self.trackingId()
        if text.lower().startswith('logapptrackingid'):
            result = self.trackingId()
        if result == None:
            result = "I didn't follow. Please enter `help`."
        return result

    def help_me(self):
        return "Enter `TrackingID` to get the logs."

    def trackingId(self):
        return "TrackingID: "

    @tornado.gen.coroutine
    def post(self):
        http_client = AsyncHTTPClient()
        webhook = json.loads(self.request.body.decode('utf-8')) # https://stackoverflow.com/questions/26716972/tornado-application-json-support

        senders_email = webhook['data']['personEmail']
        room_id = webhook['data']['roomId']

        if senders_email != bot_email:
            temp_url = url + '/messages/{0}'.format(webhook['data']['id'])
            response = requests.get(temp_url, headers=headers).json()
            in_message = response.get('text', '')
            text_trackingId = self.request.headers
            post_trackingId = text_trackingId['TrackingID']

            #Post TrackingID to Webex Space
            msg = self.handle_text(in_message)
            if msg != None:
                requests.post(url + "/messages", json={"roomId": room_id, "markdown": msg}, headers=headers)
                if 'trackingid' in msg.lower():
                    requests.post(url + "/messages",json={"roomId": room_id, "markdown": post_trackingId}, headers=headers)
                    query_trackingId = text_trackingId['TrackingID']
                    track = KibanaRequester(Requester)
                    print(track)

"""
THE PROJECT IS NOT CONCLUDED YET !!!
"""