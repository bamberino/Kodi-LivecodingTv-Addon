# -*- coding: utf-8 -*-

import xbmc, xbmcaddon
import json
import models


class Logger:
    def __init__(self, filename):
        self.filename = filename

    def __log(self, message, level):
        message = '{m} [module: {n}]'.format(m=message, n=self.filename)
        xbmc.log(message, level)

    def debug(self, message):
        self.__log(message, xbmc.LOGDEBUG)

    def error(self, message):
        self.__log(message, xbmc.LOGERROR)

    def info(self, message):
        self.__log(message, xbmc.LOGNOTICE)


__addon = xbmcaddon.Addon()


def get_mainmenu():
    # livestreams entry
    livestreams_info = LivestreamDataProvider()
    livestreams_info.get(1, 8)
    livestreams_label = __addon.getLocalizedString(30010)
    livestreams_item = models.MenuItem(livestreams_label, \
        'livestreams', livestreams_info.total, \
        livestreams_info.thumbnail)
    # videos entry
    videos_info = VideoDataProvider()
    videos_info.get(1, 8)
    videos_label = __addon.getLocalizedString(30011)
    videos_item = models.MenuItem(videos_label, 'videos', \
        videos_info.total, videos_info.thumbnail)
    # settings entry
    settings_label = __addon.getLocalizedString(30019)
    settings_item = models.MenuItem(settings_label, 'settings')
    # set all created entries to menu_items array
    menu_items = [livestreams_item, videos_item, settings_item]
    return menu_items


def _request_json(uri):
    # authentification with oauth2 needed for that currently:
    #data = requests.get(uri)
    #data_json = data.json()
    log = Logger(__name__)
    addon_path = __addon.getAddonInfo('path')
    data_path = '{p}/testdata/{f}.json'.format(p=addon_path, f=uri)
    log.debug('Requesting document from {p}' \
        .format(p=data_path))
    fp = open(data_path, mode='r')
    data_json = json.load(fp)
    fp.close()
    log.debug('Answer to request from {path}: {answer}' \
        .format(path=data_path, answer=data_json))
    return data_json


class StreamDataProvider:
    def __init__(self):
        self.__log = Logger(__name__)
        self.thumbnail = ''
        self.total = 0

    def get(self, stream_type, limit, offset):
        # TODO: request Livecoding's API with limit and offset
        streams_json = _request_json(stream_type)
        self.total = int(streams_json['count'])

        # range() - workaround for not requesting Livecoding's API
        streams = []
        for stream_json in streams_json['results'][offset:(offset+limit)]:
            if stream_type == 'livestreams':
                stream = models.Livestream(stream_json)
            elif stream_type == 'videos':
                stream = models.Video(stream_json)
            streams.append(stream)

        if len(streams) > 0:
            self.thumbnail = streams[int(len(streams)/2)].thumbnail
        message = '{num} {stream_type} returned while limit={limit}, ' \
            'offset={offset}'.format(num=len(streams), \
            stream_type=stream_type, limit=limit, offset=offset)
        self.__log.debug(message)
        return streams


class LivestreamDataProvider(StreamDataProvider):
    def __init__(self):
        StreamDataProvider.__init__(self)

    def get(self, limit = 20, offset = 0):
        lss = StreamDataProvider.get(self, 'livestreams', limit, offset)
        return lss


class VideoDataProvider(StreamDataProvider):
    def __init__(self):
        StreamDataProvider.__init__(self)

    def get(self, limit = 20, offset = 0):
        # TODO: should be dependend on coding_category / broadcaster
        vs = StreamDataProvider.get(self, 'videos', limit, offset)
        vs = sorted(vs, key=lambda v: v.creation_date, reverse=True)
        return vs
