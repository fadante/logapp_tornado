import base64
import json
import traceback

import tornado.gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError

from settings import KibanaSettings

class Requester(object):
    def __init__(self, token_manager):
        self.token_manager = token_manager
        self.initialize()

    @tornado.gen.coroutine
    def request(self, url, data=None, method="GET", tried=False, full_response=False):
        #print("Token: {0}".format(self.token_manager.token))
        if self.token_manager.token in [None, ""]:
            yield self.get_token()
            tried = True
        headers=self.get_headers()
        #print("Headers:{0}".format(headers))
        if data != None:
            if method in [None, "GET"]:
                method = "POST"
            print("building request: {0}, {1}, {2}".format(method, url, data))
            request = HTTPRequest(url, method=method, headers=headers, body=data)
        else:
            request = HTTPRequest(url, method=method, headers=headers)
        http_client = AsyncHTTPClient()
        try:
            response = yield http_client.fetch(request)
            if not full_response:
                message = json.loads(response.body.decode("utf-8"))
                response = {"success":True, "code":response.code, "data":message, "headers":response.headers._dict}
        except HTTPError as he:
            print("Requester.request HTTPError Code: {0}, {1}".format(he.code, he.message))
            try:
                print(he.response.body)
            except Exception as e:
                pass
            if not full_response:
                try:
                    response = {"success":False, "code":he.code, "message":he.message, "headers":he.response.headers._dict}
                except Exception as ex:
                    response = {"success":False, "code":he.code, "message":he.message}
            else:
                response = he.response
            if not tried:
                if he.code == 401:
                    print("Token may have expired, regenerating")
                    yield self.get_token()
                    response = yield self.request(url, data, method, True, full_response)
                elif he.code == 400:
                    try:
                        print("request error he.response.body:{0}".format(he.response.body))
                        jval = json.loads(he.response.body.decode('utf-8'))
                        if "Invalid access token" in jval['error']['message']['error_description']:
                            yield self.get_token()
                            response = yield self.request(url, data, method, True, full_response)
                    except Exception as ex:
                        print(ex)
                elif he.code == 429:
                    print("SHOULD DO SOMETHING HERE FOR 429")
                else:
                    print("SOME OTHER CODE: {0}".format(he.code))
                    #response = yield self.request(url, data, method, True, full_response)
            else:
                print("Failed on second attempt.")
        except Exception as e:
            traceback.print_exc()
            message = "{0}".format(e)
            if not full_response:
                response = {"success":False, "code":500, "message":message, "headers":{}}
            else:
                response = None
        raise tornado.gen.Return(response)

    @tornado.gen.coroutine
    def get_bearer(self):
        bearer = None
        try:
            org_id="6078fba4-49d9-4291-9f7b-80116aab6974"
            url = "https://idbroker.webex.com/idb/token/{0}/v2/actions/GetBearerToken/invoke".format(org_id)
            headers={"Content-Type":"application/json"}
            data = {"name":Settings.SERVICE_ACCOUNT, "password":Settings.SERVICE_ACCOUNT_PASSWD}
            http_request = HTTPRequest(url, method="POST", headers=headers, body=json.dumps(data))
            http_client = AsyncHTTPClient()
            response = yield http_client.fetch(http_request)
            #print(response.body)
            jresp = json.loads(response.body.decode("utf-8"))
            #print(jresp)
            #print("Bearer Account Expiration? {0}".format(jresp["AccountExpiration"]))
            bearer = jresp["BearerToken"]
        except Exception as e:
            traceback.print_exc()
        raise tornado.gen.Return(bearer)

    @tornado.gen.coroutine
    def get_token(self):
        token = None
        try:
            bearer = yield self.get_bearer()
            url = "https://idbroker.webex.com/idb/oauth2/v1/access_token"
            data = "grant_type=urn:ietf:params:oauth:grant-type:saml2-bearer&"
            data += "scope={0}".format(self.token_manager.scopes)
            data += "&assertion='{0}'".format(bearer)
            auth_encoded = base64.encodestring(('%s:%s' % (self.token_manager.oauth_client_id,
                                                           self.token_manager.oauth_client_secret)
                                                ).encode()).decode().replace('\n', '')
            headers = {'Authorization':'Basic %s' % auth_encoded}
            print("get_token data: {0}".format(data))
            http_request = HTTPRequest(url, method="POST", headers=headers, body=data)
            http_client = AsyncHTTPClient()
            response = yield http_client.fetch(http_request)
            #print(response.body)
            jresp = json.loads(response.body.decode("utf-8"))
            print("Token Account Expiration? {0}".format(jresp["accountExpiration"]))
            token = jresp["access_token"]
        except Exception as e:
            #traceback.print_exc()
            print("Requester.get_token HTTPError Code {0}, {1}".format(e.code, e.message))
            print(e.response.body)
        self.token_manager.set_token(token)
        raise tornado.gen.Return(token)
