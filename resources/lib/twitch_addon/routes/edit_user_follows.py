# -*- coding: utf-8 -*-
from ..addon.common import kodi
from ..addon.utils import i18n


def route(api, channel_id=None, channel_name=None, game=None):
    if (channel_id is None or channel_name is None) and game is None:
        return

    if not game:
        is_following = api.check_follow(channel_id)
    else:
        is_following = api.check_follow_game(game)

    if not game:
        display_name = channel_name
    else:
        display_name = game

    if is_following:
        confirmed = kodi.Dialog().yesno(i18n('toggle_follow'), i18n('unfollow_confirm') % display_name)
        if confirmed:
            if not game:
                result = api.unfollow(channel_id)
            else:
                result = api.unfollow_game(game)
            kodi.notify(msg=i18n('unfollowed') % display_name, sound=False)
    else:
        confirmed = kodi.Dialog().yesno(i18n('toggle_follow'), i18n('follow_confirm') % display_name)
        if confirmed:
            if not game:
                result = api.follow(channel_id)
            else:
                result = api.follow_game(game)
            kodi.notify(msg=i18n('now_following') % display_name, sound=False)