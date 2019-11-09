import json
import time
import traceback

import tornado.gen

from requester import *
from settings import KibanaSettings

class KibanaRequester(Requester):
    def initialize(self):
        pass

    def get_headers(self):
        headers = {
                   "Origin": "https://kibana-achm4.wbx2.com",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "en-GB,en;q=0.9",
                   "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.16 Safari/537.36",
                   "Content-Type":"application/json;charset=UTF-8",
                   "Accept": "application/json, text/plain, */*",
                   "Referer": "https://kibana-achm4.wbx2.com/app/kibana",
                   "Cookie": "access_token={0}".format(self.token_manager.token.strip("\n")),
                   "kbn-xsrf": "anything",
                   "Connection": "keep-alive"
                   }
        return headers

    @tornado.gen.coroutine
    def get_logs(self, query, from_timestamp, to_timestamp):
        url = "https://logs-noram.wbx2.com/elasticsearch/_msearch"
        preference = time.time() * 1000
        data = {"index":"logs6achm4-es-access:log*","ignore_unavailable":True,"timeout":30000,"preference":int(preference)}
        data2 = {"version":True,
                 "size":"2000",
                 "sort":[{"@timestamp":{"order":"desc","unmapped_type":"boolean"}}],
                 "_source":{"excludes":[]},
                 "aggs":{"2":{"date_histogram":{"field":"@timestamp","interval":"1h","time_zone":"UTC","min_doc_count":1}}},
                 "stored_fields":["*"],
                 "script_fields":{},
                 "docvalue_fields":["@timestamp","csb.signUpDate","csb.timestamp",
                                    "meta.created","meta.headers.x-scheduled-for",
                                    "meta.lastUpdated","meta.upstreamServices.lastUpdated","timestamp"],
                 "query":{"bool":{"must":[{"query_string":{"query":query,"analyze_wildcard":True,"default_field":"*"}},
                                          {"range":{"@timestamp":{"gte":from_timestamp,"lte":to_timestamp,"format":"epoch_millis"}}}],
                                  "filter":[],"should":[],"must_not":[]}}
                }
        return_data = None
        print('send request to {0}'.format(url))
        start_time = time.time()
        response = yield self.request(url, json.dumps(data)+"\n"+json.dumps(data2)+"\n")
        print('received response: {0}'.format(response)[:1000])#:1000 should limit to 1000 characters
        success = False
        if len(response.get('data',{}).get('responses',[])) > 0:
            if response.get('data',{}).get('responses')[0].get('hits',{}).get('total',0) > 0:
                return_data = response.get('data',{}).get('responses')[0].get('hits',{}).get('hits',[])
                print("Found data!")
                success = True
        elif response.get('success') == False:
            return_data = response
        print("DATA: {0}".format(return_data)[:1000])
        print('request took: {0} seconds.'.format(time.time()-start_time))
        raise tornado.gen.Return((success, return_data))
