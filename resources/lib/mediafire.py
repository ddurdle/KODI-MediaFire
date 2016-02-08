'''
    MediaFire for KODI / XBMC Plugin
    Copyright (C) 2013-2016 ddurdle


    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


'''

import os
import re
import urllib, urllib2
import cookielib
#from resources.lib import authorization
from cloudservice import cloudservice
#from resources.lib import folder
#from resources.lib import file
#from resources.lib import package
#from resources.lib import mediaurl
import unicodedata


import xbmc, xbmcaddon, xbmcgui, xbmcplugin

addon = xbmcaddon.Addon(id='plugin.video.mediafire')
addon_dir = xbmc.translatePath( addon.getAddonInfo('path') )

import os
import sys

sys.path.append(os.path.join( addon_dir, 'resources', 'lib' ) )

import authorization
#import cloudservice
import folder
import file
import package
import mediaurl
import crashreport

#
#
#
class mediafire(cloudservice):


    AUDIO = 1
    VIDEO = 2
    PICTURE = 3

    MEDIA_TYPE_MUSIC = 1
    MEDIA_TYPE_VIDEO = 2
    MEDIA_TYPE_PICTURE = 3

    MEDIA_TYPE_FOLDER = 0

    CACHE_TYPE_MEMORY = 0
    CACHE_TYPE_DISK = 1
    CACHE_TYPE_AJAX = 2

    ##
    # initialize (save addon, instance name, user agent)
    ##
    def __init__(self, PLUGIN_URL, addon, instanceName, user_agent):
        self.PLUGIN_URL = PLUGIN_URL
        self.addon = addon
        self.instanceName = instanceName

        self.crashreport = crashreport.crashreport(self.addon)

        try:
            username = self.addon.getSetting(self.instanceName+'_username')
        except:
            username = ''
        self.authorization = authorization.authorization(username)


        self.cookiejar = cookielib.CookieJar()

        self.user_agent = user_agent

        self.login();



    ##
    # perform login
    ##
    def login(self):

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar), MyHTTPErrorProcessor)
        opener.addheaders = [('User-Agent', self.user_agent),('X-Requested-With' ,'XMLHttpRequest')]

        url = 'https://www.mediafire.com/dynamic/client_login/mediafire.php'

        request = urllib2.Request(url)
        request.add_header('Referer', 'https://www.mediafire.com/templates/login_signup/login_signup.php?dc=loginPath&_dzpbx=4460')

        self.cookiejar.add_cookie_header(request)

        # try login
        try:
            response = opener.open(request)

        except urllib2.URLError, e:
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
            return
        response_data = response.read()
        self.cookiejar.extract_cookies(response, request)
        response.close()


        url = 'https://www.mediafire.com/templates/login_signup/login_signup.php?dc=loginPath&_dzpbx=4460'

        request = urllib2.Request(url)
        self.cookiejar.add_cookie_header(request)

        # try login
        try:
            response = opener.open(request)

        except urllib2.URLError, e:
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
            return
        response_data = response.read()
        self.cookiejar.extract_cookies(response, request)

        response.close()

        securityValue=''
        for r in re.finditer('name="(security)\" value=\"([^\"]+)\"' ,response_data, re.DOTALL):
            sessionName,securityValue = r.groups()
            #self.authorization.setToken('session_token',securityValue)


        url = 'https://www.mediafire.com/dynamic/client_login/mediafire.php'

        request = urllib2.Request(url)
        request.add_header('Referer', 'https://www.mediafire.com/templates/login_signup/login_signup.php?dc=loginPath&_dzpbx=4460')

        self.cookiejar.add_cookie_header(request)

        # try login
        try:
            response = opener.open(request,'security='+securityValue+'&login_email='+self.authorization.username+'&login_pass='+self.addon.getSetting(self.instanceName+'_password')+'&login_remember=on')

        except urllib2.URLError, e:
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
            return
        response_data = response.read()
        response.close()
#        self.crashreport.sendError('test',response_data)

        for cookie in self.cookiejar:
            for r in re.finditer(' ([^\=]+)\=([^\s]+)\s',
                        str(cookie), re.DOTALL):
                cookieType,cookieValue = r.groups()
                if cookieType == 'session':
                    self.authorization.setToken('session_token',cookieValue)


        sessionValue=''
        for r in re.finditer('(parent)\.bqx\(\"([^\"]+)\"' ,response_data, re.DOTALL):
            sessionName,sessionValue = r.groups()
            self.authorization.setToken('session_token',sessionValue)


        return


    ##
    # return the appropriate "headers" for onedrive requests that include 1) user agent, 2) authorization cookie
    #   returns: list containing the header
    ##
    def getHeadersList(self):
        auth = self.authorization.getToken('auth_token')
        session = self.authorization.getToken('auth_session')
        if (auth != '' or session != ''):
            return [('User-Agent', self.user_agent), ('Cookie', session+'; oc_username='+self.authorization.username+'; oc_token='+auth+'; oc_remember_login=1')]
        else:
            return [('User-Agent', self.user_agent )]



    ##
    # return the appropriate "headers" for onedrive requests that include 1) user agent, 2) authorization cookie
    #   returns: URL-encoded header string
    ##
    def getHeadersEncoded(self):
        auth = self.authorization.getToken('auth_token')
        session = self.authorization.getToken('auth_session')

        if (auth != '' or session != ''):
            return urllib.urlencode({ 'User-Agent' : self.user_agent, 'Cookie' : session+'; oc_username='+self.authorization.username+'; oc_token='+auth+'; oc_remember_login=1' })
        else:
            return urllib.urlencode({ 'User-Agent' : self.user_agent })

    ##
    # retrieve a list of videos, using playback type stream
    #   parameters: prompt for video quality (optional), cache type (optional)
    #   returns: list of videos
    ##
    def getMediaList(self, folderName='', cacheType=CACHE_TYPE_MEMORY):

        if folderName == '':
            folderName = 'myfiles'



        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar), MyHTTPErrorProcessor)
        opener.addheaders = [('User-Agent', self.user_agent),('X-Requested-With' ,'XMLHttpRequest')]



        sessionValue = self.authorization.getToken('session_token')
        if (sessionValue == ''):
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049), self.addon.getLocalizedString(30050),'sessionValue')
            self.crashreport.sendError('getMediaList:sessionValue','not set')
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30050)+ 'sessionValue', xbmc.LOGERROR)
            return

        if folderName == 'FOLLOWING':
            url = 'https://www.mediafire.com/api/1.4/device/get_foreign_resources.php?r=sfrv&session_token='+sessionValue+'&response_format=json'

            request = urllib2.Request(url)
            self.cookiejar.add_cookie_header(request)

            # try login
            try:
                response = opener.open(request)

            except urllib2.URLError, e:
                xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                return
            response_data = response.read()
            response.close()


            mediaFiles = []
            # parsing page for files
            for r in re.finditer('\"folders\"\:\[\{.*?\}\]' ,response_data, re.DOTALL):
                    entry = r.group()
                    for q in re.finditer('\"name\"\:\"([^\"]+)\"\,.*?\"folderkey\"\:\"([^\"]+)\"' ,entry, re.DOTALL):
                        subfolderName,subfolderID = q.groups()

                        media = package.package(0,folder.folder(subfolderID,subfolderName))
                        mediaFiles.append(media)
        else:
            url = 'https://www.mediafire.com/api/folder/get_content.php?r=mvbn&content_type=folders&filter=all&order_by=name&order_direction=asc&chunk=1&version=1.2&folder_key='+folderName+'&session_token='+sessionValue+'&response_format=json'


            request = urllib2.Request(url)
            self.cookiejar.add_cookie_header(request)

            # try login
            try:
                response = opener.open(request)

            except urllib2.URLError, e:
                xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                return
            response_data = response.read()
            response.close()


            mediaFiles = []
            # parsing page for files
            for r in re.finditer('\{\"folderkey\"\:.*?\"dropbox_enabled\"\:\"[^\"]+\"\}' ,response_data, re.DOTALL):
                    entry = r.group()
                    for q in re.finditer('\"folderkey\"\:\"([^\"]+)\"\,\"name\"\:\"([^\"]+)\"' ,entry, re.DOTALL):
                        subfolderID,subfolderName = q.groups()

                        media = package.package(0,folder.folder(subfolderID,subfolderName))
                        mediaFiles.append(media)

            url = 'https://www.mediafire.com/api/folder/get_content.php?r=mvbn&content_type=files&filter=all&order_by=name&order_direction=asc&chunk=1&version=1.2&folder_key='+folderName+'&session_token='+sessionValue+'&response_format=json'

            request = urllib2.Request(url)
            self.cookiejar.add_cookie_header(request)

            # try login
            try:
                response = opener.open(request)

            except urllib2.URLError, e:
                xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                return
            response_data = response.read()
            response.close()


            # parsing page for files
            for r in re.finditer('\{\"quickkey\"\:.*?\"links\"\:\{[^\}]+\}\}' ,response_data, re.DOTALL):
                    entry = r.group()
                    for q in re.finditer('\"quickkey\"\:\"([^\"]+)\"\,.*?\"filename\"\:\"([^\"]+)\".*?\"normal_download\"\:\"([^\"]+)\"' ,entry, re.DOTALL):
                        fileID,fileName,downloadURL = q.groups()
                        downloadURL = re.sub('\\\\', '', downloadURL)

                        media = package.package(file.file(fileID, fileName, fileName, self.VIDEO, '', ''),folder.folder('',''))
                        media.setMediaURL(mediaurl.mediaurl(downloadURL, '','',''))
                        mediaFiles.append(media)


        return mediaFiles


    ##
    # retrieve a playback url
    #   returns: url
    ##
    def getPlaybackCall(self, playbackType, package):

        downloadURL = package.getMediaURL()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar), MyHTTPErrorProcessor)
        opener.addheaders = [('User-Agent', self.user_agent),('X-Requested-With' ,'XMLHttpRequest')]

        sessionValue = self.authorization.getToken('session_token')
        if (sessionValue == ''):
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049), self.addon.getLocalizedString(30050),'sessionValue')
            self.crashreport.sendError('getPlaybackCall:sessionValue','not set')
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30050)+'sessionValue', xbmc.LOGERROR)
            return

        request = urllib2.Request(downloadURL)

        # if action fails, validate login

        try:
            response = opener.open(request)

        except urllib2.URLError, e:
                xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                return

        response_data = response.read()
        response.close()

        for r in re.finditer('(id)\=\"(form_captcha)\"' ,response_data, re.DOTALL):
            captcha,downloadURL = r.groups()
            xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30054),addon.getLocalizedString(30055), addon.getLocalizedString(30056))
            return None


        downloadURL=''
        for r in re.finditer('(kNO) \= \"([^\"]+)\"\;' ,response_data, re.DOTALL):
            urlName,downloadURL = r.groups()

        if downloadURL == '':
            try:
                if response.info().getheader('Location') != '':
                    return response.info().getheader('Location')
            except:
                pass


        if (downloadURL == ''):
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049), self.addon.getLocalizedString(30050), 'downloadURL')
            self.crashreport.sendError('getPlaybackCall:downloadURL',response_data)
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30050)+ 'downloadURL', xbmc.LOGERROR)
            return
        return downloadURL


    ##
    # retrieve a media url
    #   returns: url
    ##
    def getMediaCall(self, package):
        return #not implemented

    ##
    # retrieve a directory url
    #   returns: url
    ##
    def getDirectoryCall(self, folder):
        return self.PLUGIN_URL+'?mode=folder&instance='+self.instanceName+'&directory='+folder.id



class MyHTTPErrorProcessor(urllib2.HTTPErrorProcessor):

    def http_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.info()

        # only add this line to stop 302 redirection.
        if code == 302: return response
        if code == 303: return response

        if not (200 <= code < 300):
            response = self.parent.error(
                'http', request, response, code, msg, hdrs)
        return response

    https_response = http_response

