#!/usr/bin/env python
# By: Kelcey Damage, 2012 & Kraig Amador, 2012
 
 
import hashlib, hmac, string, base64, urllib
import json, urllib
 
class SignedAPICall(object):
    def __init__(self):
        self.api_url = "" ## Cloudstack URL 
        self.apiKey = ""  ## API key
        self.secret = ""  ## Secret key
 
    def request(self, args):
        args['apiKey'] = self.apiKey
 
        self.params = []
        self._sort_request(args)
        self._create_signature()
        self._build_post_request()
 
    def _sort_request(self, args):
        keys = sorted(args.keys())
 
        for key in keys:
            self.params.append(key + '=' + urllib.quote_plus(args[key]))
 
    def _create_signature(self):
        self.query = '&'.join(self.params)
        digest = hmac.new(
            self.secret,
            msg=self.query.lower(),
            digestmod=hashlib.sha1).digest()
 
        self.signature = base64.b64encode(digest)
 
    def _build_post_request(self):
        self.query += '&signature=' + urllib.quote_plus(self.signature)
        self.value = self.api_url + '?' + self.query
 
class CloudStack(SignedAPICall):
    def __getattr__(self, name):
        def handlerFunction(*args, **kwargs):
            if kwargs:
                return self._make_request(name, kwargs)
            return self._make_request(name, args[0])
        return handlerFunction
 
    def _http_get(self, url):
        #response = urllib.urlopen(url,timeout=60)
        response = urllib.urlopen(url)
        return response.read()
 
    def _make_request(self, command, args):
        args['response'] = 'json'
        args['command'] = command
        try:
            self.request(args)
            data = self._http_get(self.value)
            # The response is of the format {commandresponse: actual-data}
            key = command.lower() + "response"
            return json.loads(data)[key]
        except:
            return
 
