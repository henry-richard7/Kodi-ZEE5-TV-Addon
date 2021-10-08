from __future__ import unicode_literals

# noinspection PyUnresolvedReferences
from codequick import Route, Resolver, Listitem, run
from codequick.utils import urljoin_partial, bold
import requests
import xbmcgui
import re
import urllib
import inputstreamhelper

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
headers = {
    "Origin": "https://www.zee5.com",
    "Referer": "https://www.zee5.com",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "device_id": "4363debbc0dded755df0b635277271c0",
    "platform_name": "desktop_web",
    "uid": "ed7f9dad-15f5-4ef1-b9fd-d119f91408dc",
    "ppid": "4363debbc0dded755df0b635277271c0",
    "User-Agent": USER_AGENT,
    "Country": "IN"
}

languages = "ta,kn,pa,bn,en,ml,mr,gu,te,hi"
platform = 'web_app'


def get_live_token():
    url = 'https://useraction.zee5.com/token/live.php'
    data = requests.get(url, headers=headers).json()
    return data['video_token']


def get_token():
    url = 'https://useraction.zee5.com/token/platform_tokens.php?platform_name={}'.format(
        platform)
    data = requests.get(url, headers=headers).json()
    return data['token']


def get_play_url(channel_id):
    url = f"https://catalogapi.zee5.com/v1/channel/{channel_id}?translation=en&country=IN"
    data = requests.get(url).json()
    stream_url = data['stream_url_hls']
    return f"{stream_url}{get_live_token()}"


@Route.register
def root(plugin, content_type="segment"):
    headers["x-access-token"] = get_token()
    url = f'https://catalogapi.zee5.com/v1/channel/bygenre?sort_by_field=channel_number&sort_order=ASC&genres=FREE%20Channels,Hindi%20Entertainment,Hindi%20Movies,English%20Entertainment,Entertainment,Movie,News,Hindi%20News,English%20News,Marathi,Tamil,Telugu,Bengali,Malayalam,Kannada,Punjabi,Kids,Gujarati,Odiya,Music,Lifestyle,Devotional,Comedy,Drama,Sports,Infotainment&country=IN&translation=en&languages={languages}'

    jd = requests.get(url, headers=headers).json()
    items = jd['items']

    for item in items:
        for channel in item['items']:
            item = Listitem()
            item.label = channel['title']
            item.art[
                "thumb"] = f"https://akamaividz2.zee5.com/image/upload/w_386,h_386,c_scale/resources/{channel['id']}/channel_web/{channel['list_image']}"
            item.art[
                "fanart"] = f"https://akamaividz2.zee5.com/image/upload/w_386,h_386,c_scale/resources/{channel['id']}/channel_web/{channel['list_image']}"
            item.info["plot"] = f"Watch {channel['title']} Now."
            item.set_callback(play_video, channel_id=channel['id'])

            yield item


@Resolver.register
def play_video(plugin, channel_id):
    return plugin.extract_source(get_play_url(channel_id))
