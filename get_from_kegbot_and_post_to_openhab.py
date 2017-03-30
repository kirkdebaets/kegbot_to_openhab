#!/usr/bin/python

import glob
import json
import os
import time
import urllib2
import yaml

# class for handling the posting
# I stole this from somewhere but cannot remember where for attribution
class MethodRequest(urllib2.Request):
    def __init__(self, *args, **kwargs):
        if 'method' in kwargs:
            self._method = kwargs['method']
            del kwargs['method']
        else:
            self._method = None
        return urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self, *args, **kwargs):
        if self._method is not None:
            return self._method
        return urllib2.Request.get_method(self, *args, **kwargs)

def getConfig():
    # read the kegbot.yaml file from my .config directory
    # doing this in multiple steps because there is no way I'll remember this
    # after I have put the code away for a while and I don't want to spend time
    # in the future to untangle this
    thisScript = os.path.abspath(__file__)
    cwd = os.path.dirname(thisScript)
    parentDirectory = os.path.split(cwd)[0]
    configFile = os.path.join(parentDirectory, '.config', 'kegbot.yaml')

    with open(configFile, 'r') as f:
        settings = yaml.load(f)

    return settings

def getKegbotTemp(Turl):
    request = MethodRequest(Turl, method='GET')
    request.add_header('X-Kegbot-Api-Key', kegbotApiKey)

    try:
        response = urllib2.urlopen(request)
    except urllib2.URLError as e:
        if hasattr(e,'reason'):
            print "There was an URL error: " + str(e.reason)
            return
        elif hasattr(e,'code'):
            print "There was an HTTP error: " + str(e.code)
            return
    pyresponse = json.load(response)
    results = pyresponse['objects']
    timestamp = results[0]['time']
    celsius = results[0]['temperature_c']
    fahrenheit = celsius * 9 / 5 + 32

    return fahrenheit

def postToOpenhab(Turl,payload):
    #need a PUT instead of a POST
    request = MethodRequest(Turl, method='PUT')
    request.add_header('Content-Type', 'text/plain')
    request.add_data(payload)

    try:
        response = urllib2.urlopen(request)
    except urllib2.URLError as e:
        if hasattr(e,'reason'):
            print "There was an URL error: " + str(e.reason)
            return
        elif hasattr(e,'code'):
            print "There was an HTTP error: " + str(e.code)
            return

#------------------------------------------------------
# Mainline
#------------------------------------------------------
if __name__ == '__main__':
    #get the settings for this machine
    setting = getConfig()
    baseUrl = setting["base_url"]
    temperatureItem = setting["temperature_item_name"]
    temperatureUrl = baseUrl + '/rest/items/' + temperatureItem + '/state'
    kegbotUrl = setting["kegbot_url"]
    kegbotApiKey = setting["kegbot_api_key"]
    kegbotThermName = setting["thermo_sensor_name"]
    kegbotThermUrl = kegbotUrl + "/api/thermo-sensors/" + kegbotThermName + "/logs"

    # do the work
    tempF = getKegbotTemp(kegbotThermUrl)
    print tempF

    packedTempF = json.dumps(tempF)

    postToOpenhab(temperatureUrl,packedTempF)
