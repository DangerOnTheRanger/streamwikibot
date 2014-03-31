streamwikibot - pulls a list of live Twitch.tv streams into a subreddit sidebar
===============================================================================


License
-------

streamwikibot is licensed under the 2-clause BSD license, of which
a copy is included in the LICENSE file.


Requirements
------------

* [Python 2.7](http://python.org)
* [requests 2.2](http://docs.python-requests.org)
* [PRAW (Python Reddit API Wrapper) 2.1](http://praw.readthedocs.org)


Usage
-----

streamwikibot does not require installation - it runs in-place.
Configuring streamwikibot is done via the `config.ini` file, that contains
variables that control streamwikibot's behavior:

* `subreddit`: What subreddit streamwikibot is meant to control.
* `username`: The reddit username streamwikibot is meant to use. Must have moderator privileges.
* `password`: The reddit password to streamwikibot's account.
* `updatefreq`: How often streamwikibot should check for new streams. Given in seconds. 300 seconds (5 minutes) by default.
* `timeout`: How long streamwikibot should wait before considering its connection timed out. 30 seconds by default.
* `streamcutoff`: How many streams should be displayed in the sidebar. 15 by default.
* `sidebarpage`: What wiki page streamwikibot should write into the subreddit sidebar.
* `sidebartag`: What portion of text in `sidebarpage` streamwikibot should replace with the stream list.
* `aliaspage`: An optional list of aliases to replace game names with. If a game is not on the list, it will still be displayed in the sidebar.
* `wikipage`: The subreddit wiki page containing the list of streams to check. The page should be formatted
  like this:

      stream1

      stream2

      stream3

  And so on.

Here's an example of a typical `config.ini` file:

    [config]
    subreddit = somesubreddit
    username = someredditor
    password = hunter2
    updatefreq = 300
    timeout = 20
    wikipage = streamlist


streamwikibot can be pointed to an alternate config file via the `--config` option; this is
to allow a single streamwikibot copy to control multiple subreddit sidebars.
