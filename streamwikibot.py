import os
import sys
import time
import argparse
import ConfigParser
import requests
import praw


TWITCH_API_VERSION = 'v2'
TWITCH_CLIENT_ID = 'streamwikibot'
BASE_TWITCH_API_URL = 'https://api.twitch.tv/kraken/'
CONTENT_TYPE_ACCEPT = 'application/vnd.twitchtv.%s+json' % TWITCH_API_VERSION


class Stream(object):

    MAX_NAME_LEN = 15

    def __init__(self, name, viewer_count, game, url):

        if len(name) > Stream.MAX_NAME_LEN:
            self.name = name[:Stream.MAX_NAME_LEN] + '...'
        else:
            self.name = name
        self.viewer_count = viewer_count
        self.game = game
        self.url = url


def twitch_api_request(path, timeout, params={}):

    headers = {'content-type': CONTENT_TYPE_ACCEPT, 'client-id': TWITCH_CLIENT_ID}
    response = requests.get(BASE_TWITCH_API_URL + path, headers=headers, params=params, timeout=timeout)
    try:
        return response.json()
    except ValueError:
        print response.text
        sys.exit(1)


def get_live_streams(praw_instance, subreddit, listpage, timeout):

    page_content = praw_instance.get_subreddit(subreddit).get_wiki_page(listpage).content_md
    games = page_content.split('\n')
    live_streams = []

    for game in games:
        stream_info = twitch_api_request('search/streams', timeout, {'q' : game})
        if stream_info.has_key('streams') is False:
            continue
        for stream in stream_info['streams']:
            viewer_count = stream['viewers']
            internal_name = stream['channel']['name']
            external_name = stream['channel']['display_name']
            stream_url = 'http://twitch.tv/%s' % internal_name
            live_streams.append(Stream(external_name.rstrip(), viewer_count, game.strip('\r'), stream_url))
    live_streams.sort(lambda x, y: cmp(x.viewer_count, y.viewer_count), reverse=True)

    return live_streams


def update_sidebar(praw_instance, subreddit, streams, cutoff, sidebarpage, sidebartag, aliaspage=''):

    streamtext = []
    formatstr = '[**%(name)s**](%(url)s) | %(game)s | *%(viewer_count)d*'
    alias_lines = praw_instance.get_subreddit(subreddit).get_wiki_page(aliaspage).content_md.split('\n')
    aliases = dict(s.strip('\r').split(' # ') for s in alias_lines if s != '\r')

    for stream in streams[:cutoff]:
        if stream.game in aliases:
            game = aliases[stream.game]
        else:
            game = stream.game
        streamtext.append(formatstr % {'name' : stream.name, 'game' : game, 'viewer_count' : stream.viewer_count, 'url' : stream.url})
    streamtext = '\n'.join(streamtext)
    sidebartext = praw_instance.get_subreddit(subreddit).get_wiki_page(sidebarpage).content_md
    sidebartext = sidebartext.replace(sidebartag, streamtext).replace('&gt;', '>')
    title = praw_instance.get_subreddit(subreddit).get_settings()['title']
    praw_instance.get_subreddit(subreddit).set_settings(title=title, description=sidebartext)


def main():

    argparser = argparse.ArgumentParser()
    default_config_path = os.path.join(os.curdir, 'config.ini')
    argparser.add_argument('--config', help='config file to use (%s by default)' % default_config_path, default=default_config_path)
    args = argparser.parse_args()

    config_parser = ConfigParser.SafeConfigParser(defaults={'aliaspage' : '', 'timeout' : 30, 'streamcutoff' : 15, 'updatefreq' : 300})
    config_parser.readfp(open(args.config))
    update_frequency = config_parser.getint('config', 'updatefreq')
    timeout = config_parser.getint('config', 'timeout')

    praw_instance = praw.Reddit(user_agent='streamwikibot')
    username = config_parser.get('config', 'username')
    password = config_parser.get('config', 'password')
    praw_instance.login(username, password)
    subreddit = config_parser.get('config', 'subreddit')
    listpage = config_parser.get('config', 'wikipage')
    cutoff = config_parser.getint('config', 'streamcutoff')
    sidebarpage = config_parser.get('config', 'sidebarpage')
    sidebartag = config_parser.get('config', 'sidebartag')
    aliaspage = config_parser.get('config', 'aliaspage')

    while True:

        pre_update_time = time.time()
        streams = get_live_streams(praw_instance, subreddit, listpage, timeout)
        update_sidebar(praw_instance, subreddit, streams, cutoff, sidebarpage, sidebartag, aliaspage)
        post_update_time = time.time()
        update_length = post_update_time - pre_update_time
        time.sleep(max(update_frequency - update_length, 0))


if __name__ == '__main__':
    main()
