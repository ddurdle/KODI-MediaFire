'''
    MediaFire XBMC Plugin
    Copyright (C) 2013-2014 ddurdle

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



import xbmc, xbmcgui, xbmcplugin, xbmcaddon


import sys
import urllib
import cgi
import re

# global variables
PLUGIN_NAME = 'mediafire'



#helper methods
def log(msg, err=False):
    if err:
        xbmc.log(addon.getAddonInfo('name') + ': ' + msg, xbmc.LOGERROR)
    else:
        xbmc.log(addon.getAddonInfo('name') + ': ' + msg, xbmc.LOGDEBUG)

def parse_query(query):
    queries = cgi.parse_qs(query)
    q = {}
    for key, value in queries.items():
        q[key] = value[0]
    q['mode'] = q.get('mode', 'main')
    return q

def addMediaFile(service, isQuickLink, playbackType, package):

    listitem = xbmcgui.ListItem(package.file.title, iconImage=package.file.thumbnail,
                                thumbnailImage=package.file.thumbnail)

    if package.file.type == package.file.AUDIO:
        infolabels = decode_dict({ 'title' : package.file.title })
        listitem.setInfo('Music', infolabels)
        playbackURL = '?mode=audio'
    elif package.file.type == package.file.VIDEO:
        infolabels = decode_dict({ 'title' : package.file.title , 'plot' : package.file.plot })
        listitem.setInfo('Video', infolabels)
        playbackURL = '?mode=video'
    else:
        infolabels = decode_dict({ 'title' : package.file.title , 'plot' : package.file.plot })
        listitem.setInfo('Video', infolabels)
        playbackURL = '?mode=video'

    listitem.setProperty('IsPlayable', 'true')
    listitem.setProperty('fanart_image', package.file.fanart)
    cm=[]

    url = package.getMediaURL()
    cleanURL = re.sub('---', '', url)
    cleanURL = re.sub('&', '---', cleanURL)
    url = PLUGIN_URL+'?mode=streamurl&title='+package.file.title+'&url='+cleanURL



#    cm.append(( addon.getLocalizedString(30042), 'XBMC.RunPlugin('+PLUGIN_URL+'?mode=buildstrm&title='+package.file.title+'&streamurl='+cleanURL+')', ))
#    cm.append(( addon.getLocalizedString(30046), 'XBMC.PlayMedia('+playbackURL+'&title='+ package.file.title + '&directory='+ package.folder.id + '&filename='+ package.file.id +'&playback=0)', ))
#    cm.append(( addon.getLocalizedString(30047), 'XBMC.PlayMedia('+playbackURL+'&title='+ package.file.title + '&directory='+ package.folder.id + '&filename='+ package.file.id +'&playback=1)', ))
#    cm.append(( addon.getLocalizedString(30048), 'XBMC.PlayMedia('+playbackURL+'&title='+ package.file.title + '&directory='+ package.folder.id + '&filename='+ package.file.id +'&playback=2)', ))
    #cm.append(( addon.getLocalizedString(30032), 'XBMC.RunPlugin('+PLUGIN_URL+'?mode=download&title='+package.file.title+'&filename='+package.file.id+')', ))

#    listitem.addContextMenuItems( commands )
    if cm:
        listitem.addContextMenuItems(cm, False)
    xbmcplugin.addDirectoryItem(plugin_handle, url, listitem,
                                isFolder=False, totalItems=0)

def addDirectory(service, folder):
    listitem = xbmcgui.ListItem(decode(folder.title), iconImage='', thumbnailImage='')
    fanart = addon.getAddonInfo('path') + '/fanart.jpg'

    if folder.id != '':
        cm=[]
#        cm.append(( addon.getLocalizedString(30042), 'XBMC.RunPlugin('+PLUGIN_URL+'?mode=buildstrm&title='+folder.title+'&instanceName='+str(service.instanceName)+'&folderID='+str(folder.id)+')', ))
        listitem.addContextMenuItems(cm, False)
    listitem.setProperty('fanart_image', fanart)
    xbmcplugin.addDirectoryItem(plugin_handle, service.getDirectoryCall(folder), listitem,
                                isFolder=True, totalItems=0)

def addMenu(url,title):
    listitem = xbmcgui.ListItem(decode(title), iconImage='', thumbnailImage='')
    fanart = addon.getAddonInfo('path') + '/fanart.jpg'

    listitem.setProperty('fanart_image', fanart)
    xbmcplugin.addDirectoryItem(plugin_handle, url, listitem,
                                isFolder=True, totalItems=0)


#http://stackoverflow.com/questions/1208916/decoding-html-entities-with-python/1208931#1208931
def _callback(matches):
    id = matches.group(1)
    try:
        return unichr(int(id))
    except:
        return id

def decode(data):
    return re.sub("&#(\d+)(;|(?=\s))", _callback, data).strip()

def decode_dict(data):
    for k, v in data.items():
        if type(v) is str or type(v) is unicode:
            data[k] = decode(v)
    return data


def numberOfAccounts(accountType):

    count = 1
    max_count = int(addon.getSetting(accountType+'_numaccounts'))
    actualCount = 0
    while True:
        try:
            if addon.getSetting(accountType+str(count)+'_username') != '':
                actualCount = actualCount + 1
        except:
            break
        if count == max_count:
            break
        count = count + 1
    return actualCount


#global variables
PLUGIN_URL = sys.argv[0]
plugin_handle = int(sys.argv[1])
plugin_queries = parse_query(sys.argv[2][1:])

addon = xbmcaddon.Addon(id='plugin.video.mediafire')

addon_dir = xbmc.translatePath( addon.getAddonInfo('path') )

import os
sys.path.append(os.path.join( addon_dir, 'resources', 'lib' ) )

import mediafire
import cloudservice
import folder
import file
import package
import mediaurl
import authorization


#from resources.lib import mediafire
#from resources.lib import gPlayer
#from resources.lib import tvWindow
#from resources.lib import cloudservice
#from resources.lib import folder
#from resources.lib import file
#from resources.lib import package
#from resources.lib import mediaurl



#debugging
try:

    remote_debugger = addon.getSetting('remote_debugger')
    remote_debugger_host = addon.getSetting('remote_debugger_host')

    # append pydev remote debugger
    if remote_debugger == 'true':
        # Make pydev debugger works for auto reload.
        # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
        import pysrc.pydevd as pydevd
        # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
        pydevd.settrace(remote_debugger_host, stdoutToServer=True, stderrToServer=True)
except ImportError:
    log(addon.getLocalizedString(30016), True)
    sys.exit(1)
except :
    pass


# retrieve settings
user_agent = addon.getSetting('user_agent')


mode = plugin_queries['mode']

# make mode case-insensitive
mode = mode.lower()


log('plugin url: ' + PLUGIN_URL)
log('plugin queries: ' + str(plugin_queries))
log('plugin handle: ' + str(plugin_handle))

#if mode == 'main':
#    addMenu(PLUGIN_URL+'?mode=options','<<'+addon.getLocalizedString(30043)+'>>')


#dump a list of videos available to play
if mode == 'main' or mode == 'folder':

    cacheType = int(addon.getSetting('playback_type'))

    folderName=''

    if (mode == 'folder'):
        folderName = plugin_queries['directory']
    else:
        pass

    try:
        isQuickLink = addon.getSetting('playback_type')
        if isQuickLink == 'true':
            isQuickLink = True
        else:
            isQuickLink = False
    except:
        isQuickLink = False

    instanceName = ''
    try:
        instanceName = (plugin_queries['instance']).lower()
    except:
        pass

    numberOfAccounts = numberOfAccounts(PLUGIN_NAME)

    # show list of services
    if numberOfAccounts > 1 and instanceName == '':
        count = 1
        max_count = int(addon.getSetting(PLUGIN_NAME+'_numaccounts'))
        while True:
            instanceName = PLUGIN_NAME+str(count)
            try:
                username = addon.getSetting(instanceName+'_username')
                if username != '':
                    addMenu(PLUGIN_URL+'?mode=main&instance='+instanceName,username)
            except:
                break
            if count == max_count:
                break
            count = count + 1

    else:
        # show index of accounts
        if instanceName == '' and numberOfAccounts == 1:

                count = 1
                max_count = int(addon.getSetting(PLUGIN_NAME+'_numaccounts'))
                loop = True
                while loop:
                    instanceName = PLUGIN_NAME+str(count)
                    try:
                        username = addon.getSetting(instanceName+'_username')
                        if username != '':

                            #let's log in
                            service = mediafire.mediafire(PLUGIN_URL,addon,instanceName, user_agent)
                            loop = False
                    except:
                        break

                    if count == max_count:
                        break
                    count = count + 1

        # no accounts defined
        elif numberOfAccounts == 0:

            #legacy account conversion
            try:
                username = addon.getSetting('username')

                if username != '':
                    addon.setSetting(PLUGIN_NAME+'1_username', username)
                    addon.setSetting(PLUGIN_NAME+'1_password', addon.getSetting('password'))
                    addon.setSetting(PLUGIN_NAME+'1_auth_token', addon.getSetting('auth_token'))
                    addon.setSetting(PLUGIN_NAME+'1_auth_session', addon.getSetting('auth_session'))
                    addon.setSetting('username', '')
                    addon.setSetting('password', '')
                    addon.setSetting('auth_token', '')
                    addon.setSetting('auth_session', '')
                else:
                    xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30015))
                    log(addon.getLocalizedString(30015), True)
                    xbmcplugin.endOfDirectory(plugin_handle)
            except :
                    xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30015))
                    log(addon.getLocalizedString(30015), True)
                    xbmcplugin.endOfDirectory(plugin_handle)

            #let's log in
            service = mediafire.mediafire(PLUGIN_URL,addon,instanceName, user_agent)


        # show entries of a single account (such as folder)
        elif instanceName != '':

            service = mediafire.mediafire(PLUGIN_URL,addon,instanceName, user_agent)

        try:
            service
        except NameError:
            xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30051), addon.getLocalizedString(30052), addon.getLocalizedString(30053))
            log(aaddon.getLocalizedString(30050)+ 'mediafire-login', True)
            xbmcplugin.endOfDirectory(plugin_handle)


        mediaItems = service.getMediaList(folderName,0)

        if mediaItems:
            for item in sorted(mediaItems):

                try:
                    if item.file == 0:
                        addDirectory(service, item.folder)
                    else:
                        addMediaFile(service, isQuickLink, cacheType, item)
                except:
                        addMediaFile(service, isQuickLink, cacheType, item)

        service.updateAuthorization(addon)


#play a video given its exact-title
elif mode == 'video' or mode == 'audio':

    filename = plugin_queries['filename']
    try:
        directory = plugin_queries['directory']
    except:
        directory = ''

    try:
        title = plugin_queries['title']
    except:
        title = ''

    try:
        cacheType = plugin_queries['playback']
    except:
        try:
            cacheType = int(addon.getSetting('playback_type'))
        except:
            cacheType = 0


    instanceName = ''
    try:
        instanceName = plugin_queries['instance']
    except:
        pass

    # show index of accounts
    if instanceName == '':

                count = 1
                max_count = int(addon.getSetting(PLUGIN_NAME+'_numaccounts'))
                while True:
                    instanceName = PLUGIN_NAME+str(count)
                    try:
                        username = addon.getSetting(instanceName+'_username')
                        if username != '':

                            #let's log in
                            service = mediafire.mediafire(PLUGIN_URL,addon,instanceName, user_agent)

                    except:
                        break

                    if count == max_count:
                        break
                    count = count + 1

    elif instanceName != '':

            service = mediafire.mediafire(PLUGIN_URL,addon,instanceName, user_agent)

    try:
            service
    except NameError:
            xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30051), addon.getLocalizedString(30052), addon.getLocalizedString(30053))
            log(aaddon.getLocalizedString(30050)+ 'mediafire-login', True)
            xbmcplugin.endOfDirectory(plugin_handle)


    mediaFile = file.file(filename, title, '', 0, '','')
    mediaFolder = folder.folder(directory,directory)
    url = service.getPlaybackCall(cacheType,package.package(mediaFile,mediaFolder ))

    item = xbmcgui.ListItem(path=url)
    item.setInfo( type="Video", infoLabels={ "Title": title , "Plot" : title } )
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
#play a video given its exact-title
elif mode == 'streamurl':

    url = plugin_queries['url']

    try:
        title = plugin_queries['title']
    except:
        title = ''


    instanceName = ''
    try:
        instanceName = plugin_queries['instance']
    except:
        pass

    # show index of accounts
    if instanceName == '':

                count = 1
                max_count = int(addon.getSetting(PLUGIN_NAME+'_numaccounts'))
                loop = True
                while loop:
                    instanceName = PLUGIN_NAME+str(count)
                    try:
                        username = addon.getSetting(instanceName+'_username')
                        if username != '':

                            #let's log in
                            service = mediafire.mediafire(PLUGIN_URL,addon,instanceName, user_agent)
                            loop = False
                    except:
                        break

                    if count == max_count:
                        break
                    count = count + 1

    elif instanceName != '':

            service = mediafire.mediafire(PLUGIN_URL,addon,instanceName, user_agent)

    try:
            service
    except NameError:
            xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30051), addon.getLocalizedString(30052), addon.getLocalizedString(30053))
            log(aaddon.getLocalizedString(30050)+ 'mediafire-login', True)
            xbmcplugin.endOfDirectory(plugin_handle)


    mediaFile = file.file('', '', '', 0, '','')
    mediaFolder = folder.folder('','')
    media = package.package(mediaFile,mediaFolder)
    cleanURL = re.sub('---', '&', url)
#    cleanURL = re.sub('_', '+', cleanURL)

    media.setMediaURL(mediaurl.mediaurl(cleanURL,'','',''))
    url = service.getPlaybackCall(0,media)

    item = xbmcgui.ListItem(path=url)
    item.setInfo( type="Video", infoLabels={ "Title": title , "Plot" : title } )
#    item.setInfo( type="Music", infoLabels={ "Title": title , "Plot" : title } )

    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)


if mode == 'options' or mode == 'buildstrm' or mode == 'clearauth':
    addMenu(PLUGIN_URL+'?mode=clearauth','<<'+addon.getLocalizedString(30018)+'>>')
    addMenu(PLUGIN_URL+'?mode=buildstrm','<<'+addon.getLocalizedString(30025)+'>>')



xbmcplugin.endOfDirectory(plugin_handle)

