#!/usr/bin/env python

import httplib2
import json
import datetime
import base64
import sys
import os
import getpass
import errno

from urllib2 import urlopen
from json import dumps

from socket import error as socket_error
import socket

def get_token():
    apiMethod="https://"
    apiVersion="/v22"
    apiServer="api.weaved.com"
    apiKey="WeavedDemoKey$2015"

    httplib2.debuglevel     = 0
    http                    = httplib2.Http()
    content_type_header     = "application/json"

    userName = 'jrh2192@columbia.edu'
    password = 'honuclearblue'
        
    loginURL = apiMethod + apiServer + apiVersion + "/api/user/login"

    loginHeaders = {
                'Content-Type': content_type_header,
                'apikey': apiKey
            }
    try:        
        response, content = http.request( loginURL + "/" + userName + "/" + password,
                                          'GET',
                                          headers=loginHeaders)
    except:
        print "Server not found.  Possible connection problem!"
        exit()                                          
    #print (response)
    #print "============================================================"
    #print (content)
    print

    try: 
        data = json.loads(content)
        if(data["status"] != "true"):
            print "Can't connect to Weaved server!"
            print data["reason"]
            exit()

        token = data["token"]
    except KeyError:
        print "Comnnection failed!"
        exit()
        
    #print "Token = " +  token

    return token


def get_ip():
    token = get_token()
    apiMethod="https://"
    apiServer="api.weaved.com"
    apiVersion= "/v22"
    apiKey="WeavedDemoKey$2015"
    # add the token here which you got from the /user/login API call
    deviceListURL = apiMethod + apiServer + apiVersion + "/api/device/list/all"
    content_type_header     = "application/json"

    deviceListHeaders = {
                    'Content-Type': content_type_header,
                    'apikey': apiKey,
                    # you need to get token from a call to /user/login
                    'token': token,
                }

               
    httplib2.debuglevel     = 0
    http                    = httplib2.Http()

    response, content = http.request( deviceListURL,
                                          'GET',
                                          headers=deviceListHeaders)
    struct = json.loads(content)
    devices = struct['devices']
    output = []
    for device in devices:
        alias = device['devicealias']
        address = device['lastinternalip']
        status = device['devicestate']
        info = (alias, address, status)
        output.append(info)
    test = ('localhost', '000.00.000.000', 'testing')
    output.append(test)
    return output