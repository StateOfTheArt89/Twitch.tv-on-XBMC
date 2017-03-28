# -*- coding: utf-8 -*-
"""

    Copyright (C) 2016 Twitch-on-Kodi

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import menu_items
from common import kodi
from utils import the_art, TitleBuilder, i18n, get_oauth_token
from constants import Keys, Images, MODES


class PlaylistConverter(object):
    @staticmethod
    def convert_to_kodi_playlist(input_playlist, title='', image=''):
        # Create playlist in Kodi, return dict {'initial_item': {listitem dict}, 'playlist': playlist}
        playlist = kodi.PlayList(kodi.PLAYLIST_VIDEO)
        playlist.clear()
        initial_item = None
        for (url, details) in input_playlist:
            if url:
                if details != ():
                    (title, image) = details
                playback_item = kodi.ListItem(label=title, path=url)
                playback_item.setArt(the_art({'poster': image, 'thumb': image, 'icon': image}))
                playback_item.setProperty('IsPlayable', 'true')
                playlist.add(url, playback_item)
                if not initial_item and url:
                    initial_item = {'label': title, 'thumbnail': image, 'path': url, 'is_playable': True}

        if playlist and initial_item:

            return {'initial_item': initial_item, 'playlist': playlist}
        else:
            return {'initial_item': None, 'playlist': None}


class JsonListItemConverter(object):
    def __init__(self, title_length):
        self.title_builder = TitleBuilder(title_length)
        self.has_token = True if get_oauth_token() else False

    @staticmethod
    def game_to_listitem(game):
        name = game[Keys.NAME].encode('utf-8')
        if not name:
            name = i18n('unknown_game')
        image = Images.BOXART
        if game.get(Keys.BOX):
            image = game[Keys.BOX].get(Keys.LARGE) if game[Keys.BOX].get(Keys.LARGE) else image
        context_menu = list()
        context_menu.extend(menu_items.refresh())
        context_menu.extend(menu_items.clear_previews())
        context_menu.extend(menu_items.edit_follow_game(name))
        context_menu.extend(menu_items.add_blacklist(game[Keys.ID], name, list_type='game'))
        return {'label': name,
                'path': kodi.get_plugin_url({'mode': MODES.GAMESTREAMS, 'game': name}),
                'art': the_art({'poster': image, 'thumb': image, 'icon': image}),
                'context_menu': context_menu}

    @staticmethod
    def community_to_listitem(community):
        name = community[Keys.NAME].encode('utf-8')
        _id = community[Keys.ID]
        image = community.get(Keys.AVATAR_IMAGE, Images.THUMB)
        context_menu = list()
        context_menu.extend(menu_items.refresh())
        context_menu.extend(menu_items.clear_previews())
        return {'label': name,
                'path': kodi.get_plugin_url({'mode': MODES.COMMUNITYSTREAMS, 'community_id': _id}),
                'art': the_art({'poster': image, 'thumb': image, 'icon': image}),
                'context_menu': context_menu}

    @staticmethod
    def team_to_listitem(team):
        name = team[Keys.NAME]
        background = team.get(Keys.BACKGROUND) if team.get(Keys.BACKGROUND) else Images.FANART
        image = team.get(Keys.LOGO) if team.get(Keys.LOGO) else Images.ICON
        context_menu = list()
        context_menu.extend(menu_items.refresh())
        context_menu.extend(menu_items.clear_previews())
        return {'label': name,
                'path': kodi.get_plugin_url({'mode': MODES.TEAMSTREAMS, 'team': name}),
                'art': the_art({'fanart': background, 'poster': image, 'thumb': image, 'icon': image}),
                'context_menu': context_menu}

    def team_channel_to_listitem(self, team_channel):
        images = team_channel.get(Keys.IMAGE)
        image = Images.ICON
        if images:
            image = images.get(Keys.SIZE600) if images.get(Keys.SIZE600) else Images.ICON
        channel_name = team_channel[Keys.NAME]
        title_values = self.extract_channel_title_values(team_channel)
        title = self.title_builder.format_title(title_values)
        context_menu = list()
        context_menu.extend(menu_items.refresh())
        context_menu.extend(menu_items.run_plugin(i18n('play_choose_quality'),
                                                  {'mode': MODES.PLAY, 'name': channel_name, 'source': False, 'use_player': True}))
        return {'label': title,
                'path': kodi.get_plugin_url({'mode': MODES.PLAY, 'name': channel_name}),
                'context_menu': context_menu,
                'is_playable': True,
                'art': the_art({'poster': image, 'thumb': image, 'icon': image})}

    def channel_to_listitem(self, channel):
        image = channel.get(Keys.LOGO) if channel.get(Keys.LOGO) else Images.ICON
        video_banner = channel.get(Keys.VIDEO_BANNER)
        if not video_banner:
            video_banner = channel.get(Keys.PROFILE_BANNER) if channel.get(Keys.PROFILE_BANNER) else Images.FANART
        context_menu = list()
        context_menu.extend(menu_items.refresh())
        context_menu.extend(menu_items.clear_previews())
        context_menu.extend(menu_items.add_blacklist(channel[Keys.ID], channel[Keys.DISPLAY_NAME]))
        if self.has_token:
            context_menu.extend(menu_items.edit_follow(channel[Keys.ID], channel[Keys.DISPLAY_NAME]))
            context_menu.extend(menu_items.edit_block(channel[Keys.ID], channel[Keys.DISPLAY_NAME]))
        return {'label': channel[Keys.DISPLAY_NAME],
                'path': kodi.get_plugin_url({'mode': MODES.CHANNELVIDEOS, 'channel_id': channel[Keys.ID]}),
                'art': the_art({'fanart': video_banner, 'poster': image, 'thumb': image}),
                'context_menu': context_menu}

    @staticmethod
    def video_list_to_listitem(video):
        duration = video.get(Keys.LENGTH)
        plot = video.get(Keys.DESCRIPTION)
        date = video.get(Keys.CREATED_AT)[:10] if video.get(Keys.CREATED_AT) else ''
        year = video.get(Keys.CREATED_AT)[:4] if video.get(Keys.CREATED_AT) else ''
        image = video.get(Keys.PREVIEW) if video.get(Keys.PREVIEW) else Images.VIDEOTHUMB
        if Keys.MEDIUM in image:
            image = image.get(Keys.MEDIUM)
        context_menu = list()
        context_menu.extend(menu_items.refresh())
        context_menu.extend(menu_items.go_to_game(video[Keys.GAME]))
        channel = video[Keys.CHANNEL]
        context_menu.extend(menu_items.set_default_quality(channel[Keys.ID], channel[Keys.NAME], video[Keys.ID]))
        context_menu.extend(menu_items.run_plugin(i18n('play_choose_quality'),
                                                  {'mode': MODES.PLAY, 'video_id': video[Keys.ID], 'source': False, 'use_player': True}))
        return {'label': video[Keys.TITLE],
                'path': kodi.get_plugin_url({'mode': MODES.PLAY, 'video_id': video[Keys.ID]}),
                'context_menu': context_menu,
                'is_playable': True,
                'info': {'duration': str(duration), 'plot': plot, 'plotoutline': plot, 'tagline': plot,
                         'year': year, 'date': date, 'premiered': date, 'mediatype': 'video'},
                'content_type': 'video',
                'art': the_art({'poster': image, 'thumb': image, 'icon': image})}

    def stream_to_listitem(self, stream):
        channel = stream[Keys.CHANNEL]
        video_banner = channel.get(Keys.PROFILE_BANNER)
        if not video_banner:
            video_banner = channel.get(Keys.VIDEO_BANNER) if channel.get(Keys.VIDEO_BANNER) else Images.FANART
        preview = stream.get(Keys.PREVIEW)
        if Keys.MEDIUM in preview:
            preview = preview.get(Keys.MEDIUM)
        logo = channel.get(Keys.LOGO) if channel.get(Keys.LOGO) else Images.VIDEOTHUMB
        image = preview if preview else logo
        title = self.get_title_for_stream(stream)
        info = self.get_plot_for_stream(stream)
        info.update({'mediatype': 'video'})
        context_menu = list()
        context_menu.extend(menu_items.refresh())
        context_menu.extend(menu_items.channel_videos(channel[Keys.ID], channel[Keys.DISPLAY_NAME]))
        context_menu.extend(menu_items.go_to_game(channel[Keys.GAME]))
        context_menu.extend(menu_items.add_blacklist(channel[Keys.ID], channel[Keys.DISPLAY_NAME]))
        if self.has_token:
            context_menu.extend(menu_items.edit_follow(channel[Keys.ID], channel[Keys.DISPLAY_NAME]))
            context_menu.extend(menu_items.edit_block(channel[Keys.ID], channel[Keys.DISPLAY_NAME]))
        context_menu.extend(menu_items.set_default_quality(channel[Keys.ID], channel[Keys.NAME]))
        context_menu.extend(menu_items.run_plugin(i18n('play_choose_quality'),
                                                  {'mode': MODES.PLAY, 'name': channel[Keys.NAME], 'channel_id': channel[Keys.ID], 'source': False, 'use_player': True}))
        return {'label': title,
                'path': kodi.get_plugin_url({'mode': MODES.PLAY, 'name': channel[Keys.NAME], 'channel_id': channel[Keys.ID]}),
                'context_menu': context_menu,
                'is_playable': True,
                'info': info,
                'content_type': 'video',
                'art': the_art({'fanart': video_banner, 'poster': image, 'thumb': image, 'icon': image})}

    def video_to_playitem(self, video):
        # path is returned '' and must be set after
        channel = video[Keys.CHANNEL]
        preview = video.get(Keys.PREVIEW)
        if Keys.MEDIUM in preview:
            preview = preview.get(Keys.MEDIUM)
        logo = channel.get(Keys.LOGO) if channel.get(Keys.LOGO) else Images.VIDEOTHUMB
        image = preview if preview else logo
        title = self.get_title_for_stream(video)
        return {'label': title,
                'path': '',
                'art': the_art({'poster': image, 'thumb': image, 'icon': image}),
                'content_type': 'video',
                'is_playable': True}

    def stream_to_playitem(self, stream):
        # path is returned '' and must be set after
        channel = stream[Keys.CHANNEL]
        preview = stream.get(Keys.PREVIEW)
        if preview:
            preview = preview.get(Keys.MEDIUM)
        logo = channel.get(Keys.LOGO) if channel.get(Keys.LOGO) else Images.VIDEOTHUMB
        image = preview if preview else logo
        title = self.get_title_for_stream(stream)
        return {'label': title,
                'path': '',
                'art': the_art({'poster': image, 'thumb': image, 'icon': image}),
                'content_type': 'video',
                'is_playable': True}

    @staticmethod
    def get_video_info(video):
        channel = video.get(Keys.CHANNEL)
        streamer = channel.get(Keys.DISPLAY_NAME) if channel.get(Keys.DISPLAY_NAME) else i18n('unnamed_streamer')
        game = video.get(Keys.GAME) if video.get(Keys.GAME) else video.get(Keys.META_GAME)
        game = game if game else i18n('unknown_game')
        views = video.get(Keys.VIEWS) if video.get(Keys.VIEWS) else '0'
        title = video.get(Keys.TITLE) if video.get(Keys.TITLE) else i18n('untitled_stream')
        image = video.get(Keys.PREVIEW) if video.get(Keys.PREVIEW) else Images.VIDEOTHUMB
        return {'streamer': streamer,
                'title': title,
                'game': game,
                'views': views,
                'thumbnail': image}

    def get_title_for_stream(self, stream):
        title_values = self.extract_stream_title_values(stream)
        return self.title_builder.format_title(title_values)

    @staticmethod
    def extract_stream_title_values(stream):
        channel = stream[Keys.CHANNEL]

        if Keys.VIEWERS in channel:
            viewers = channel.get(Keys.VIEWERS)
        else:
            viewers = stream.get(Keys.VIEWERS)
        viewers = viewers if viewers else i18n('unknown_viewer_count')

        streamer = channel.get(Keys.DISPLAY_NAME) if channel.get(Keys.DISPLAY_NAME) else i18n('unnamed_streamer')
        title = channel.get(Keys.STATUS) if channel.get(Keys.STATUS) else i18n('untitled_stream')
        game = channel.get(Keys.GAME) if channel.get(Keys.GAME) else i18n('unknown_game')
        broadcaster_language = channel.get(Keys.BROADCASTER_LANGUAGE) if channel.get(Keys.BROADCASTER_LANGUAGE) else i18n('unknown_language')

        return {'streamer': streamer,
                'title': title,
                'game': game,
                'viewers': viewers,
                'broadcaster_language': broadcaster_language}

    @staticmethod
    def extract_channel_title_values(channel):
        streamer = channel.get(Keys.DISPLAY_NAME) if channel.get(Keys.DISPLAY_NAME) else i18n('unnamed_streamer')
        title = channel.get(Keys.TITLE) if channel.get(Keys.TITLE) else i18n('untitled_stream')
        game = channel.get(Keys.GAME) if channel.get(Keys.GAME) else channel.get(Keys.META_GAME)
        game = game if game else i18n('unknown_game')
        viewers = channel.get(Keys.CURRENT_VIEWERS) \
            if channel.get(Keys.CURRENT_VIEWERS) else i18n('unknown_viewer_count')
        broadcaster_language = channel.get(Keys.BROADCASTER_LANGUAGE) if channel.get(Keys.BROADCASTER_LANGUAGE) else i18n('unknown_language')

        return {'streamer': streamer,
                'title': title,
                'viewers': viewers,
                'game': game,
                'broadcaster_language': broadcaster_language}

    @staticmethod
    def get_plot_for_stream(stream):
        channel = stream[Keys.CHANNEL]

        headings = {Keys.GAME: i18n('game').decode('utf-8'),
                    Keys.VIEWERS: i18n('viewers').decode('utf-8'),
                    Keys.BROADCASTER_LANGUAGE: i18n('language').decode('utf-8'),
                    Keys.MATURE: i18n('mature').decode('utf-8'),
                    Keys.PARTNER: i18n('partner').decode('utf-8'),
                    Keys.DELAY: i18n('delay').decode('utf-8')}
        info = {
            Keys.GAME: stream.get(Keys.GAME) if stream.get(Keys.GAME) else i18n('unknown_game').decode('utf-8'),
            Keys.VIEWERS: str(stream.get(Keys.VIEWERS)) if stream.get(Keys.VIEWERS) else u'0',
            Keys.BROADCASTER_LANGUAGE: channel.get(Keys.BROADCASTER_LANGUAGE)
            if channel.get(Keys.BROADCASTER_LANGUAGE) else None,
            Keys.MATURE: str(channel.get(Keys.MATURE)) if channel.get(Keys.MATURE) else u'False',
            Keys.PARTNER: str(channel.get(Keys.PARTNER)) if channel.get(Keys.PARTNER) else u'False',
            Keys.DELAY: str(stream.get(Keys.DELAY)) if stream.get(Keys.DELAY) else u'0'
        }
        title = channel.get(Keys.STATUS) + u'\r\n' if channel.get(Keys.STATUS) else u''

        item_template = u'{head}:{info}  '  # no whitespace around {head} and {info} for word wrapping in Kodi
        plot_template = u'{title}{game}{viewers}{broadcaster_language}{mature}{partner}{delay}'

        def format_key(key):
            value = ''
            if info.get(key) is not None:
                try:
                    val_heading = headings.get(key)
                except:
                    val_heading = headings.get(key)
                try:
                    val_info = info.get(key)
                except:
                    val_info = info.get(key)
                value = item_template.format(head=val_heading, info=val_info)
            return value

        plot = plot_template.format(title=title, game=format_key(Keys.GAME),
                                    viewers=format_key(Keys.VIEWERS), delay=format_key(Keys.DELAY),
                                    broadcaster_language=format_key(Keys.BROADCASTER_LANGUAGE),
                                    mature=format_key(Keys.MATURE), partner=format_key(Keys.PARTNER))

        return {u'plot': plot, u'plotoutline': plot, u'tagline': title.rstrip('\r\n')}

    @staticmethod
    def get_video_for_quality(videos, source=True, return_label=False, quality=None):
        for quality_label, url in videos:
            if ((quality) and (quality.lower() in quality_label.lower())) or len(videos) == 1:
                if return_label:
                    return quality_label, url
                else:
                    return url
        for quality_label, url in videos:
            if (source) and ('source' in quality_label.lower()):
                if return_label:
                    return quality_label, url
                else:
                    return url

        result = kodi.Dialog().select(i18n('choose_quality'), [quality for quality, url in videos])
        if result == -1:
            return None
        else:
            if return_label:
                return videos[result][0], videos[result][1]
            else:
                return videos[result][1]
