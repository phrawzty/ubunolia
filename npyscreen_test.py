#!/usr/bin/env python
# pylint: disable=invalid-name
"""
A text-mode interface to the Ubuntu IRC logs as served by Algolia.
The idea is that this is running against live logs, which explains some of
the design decisions (i.e. lots of querying).
"""

from algoliasearch import algoliasearch
import npyscreen
import json

class Algolia(object):
    """Handles the Algolia stuff."""

    def __init__(self):
        self.app_id = 'PBF4ZR3KBT'
        self.api_key = '9188cd13a0dbf3d0af949802b0e31489' # search-only
        self.index = 'ubuntu_irc_logs'

        # Restricted search (for acquiring metadata).
        self.restricted_search = {
            'page': 1,
            'hitsPerPage': 1,
            'length': 1
        }

        # General search.
        self.general_search = {
            'highlightPreTag': '',
            'highlightPostTag': '',
            'hitsPerPage': 100
        }

        # Keep it simple.
        self.client = algoliasearch.Client(self.app_id, self.api_key)
        self.index = self.client.init_index(self.index)

    def get_channels(self):
        """Get a list of indexed channels."""

        criteria = {'facets': 'channel'}
        results = self.index.search(
            '',
            dict(self.restricted_search, **criteria)
        )

        return results['facets']['channel'].keys()

    def get_top_users(self, num=10):
        """Get the top 10 most active usernames."""

        criteria = {'facets': 'username'}
        results = self.index.search(
            '',
            dict(self.restricted_search, **criteria)
        )

        top_users = results['facets']['username']
        top_user_list = []

        for user in sorted(top_users, key=top_users.get, reverse=True):
            top_user_list.append(user)

        return top_user_list[0:num]

    def get_total_records(self):
        """Get the total number of records."""

        results = self.index.search('')

        return results['nbHits']

    def do_a_search(self, query, criteria):
        """Execute a search and hold on to the result."""

        results = self.index.search(
            query,
            dict(self.general_search, **criteria)
        )

        return results

    def set_cache(self, data):
        """npyscreen has no shared state, so we have to cache results in order
        to process data between forms."""

        with open('cache', 'w') as outfile:
            json.dump(data, outfile)

        return 0

    def get_cache(self):
        """Retreive the cache."""

        with open('cache') as json_data:
            cache = json.load(json_data)

        return cache

# npyscreen makes pylint cry.
class Formy(npyscreen.ActionForm): # pylint: disable=too-many-ancestors
    """Sets up the npyscreen interface."""

    def afterEditing(self):
        """Exit cleanly, one would hope."""

        # Trigger the result form.
        self.parentApp.setNextForm('RESULTDISPLAY')

    def on_ok(self):
        # Do the requested search and set up the data for the result form.

        if self.username.value:
            username = self.username.value
        elif self.top_user.value:
            username = self.username.value

        criteria = {}
        if self.channels.value:
            criteria = {
                'facetFilters': [
                    'channel:' + self.channels.value
                ]
            }

        self.parentApp.alobj.set_cache(
            self.parentApp.alobj.do_a_search(username, criteria)
        )

    def create(self):
        """Create the first menu."""

        self.username = self.add(npyscreen.TitleText, name='Username')
        self.top_user = self.add(
            npyscreen.TitleSelectOne,
            max_height=5,
            scroll_exit=True,
            name='Top Users',
            values=self.parentApp.alobj.get_top_users())
        self.channels = self.add(
            npyscreen.TitleSelectOne,
            max_height=3,
            scroll_exit=True,
            name='Channels',
            values=self.parentApp.alobj.get_channels())
        self.date = self.add(npyscreen.TitleDateCombo, name='Date')

class ResultDisplay(npyscreen.Form): # pylint: disable=too-many-ancestors
    """Display the results."""

    def afterEditing(self):
        """Exit cleanly, one would hope."""

        self.parentApp.setNextForm(None)

    def create(self):
        """Display them results forilla."""

        thing = self.parentApp.alobj.get_cache()

        poop = []

        for hit in thing['hits']:
            datestamp = hit['datestamp']
            channel = hit['channel']
            username = hit['username']
            message = hit['message']
            line = "[%s] (%s/%s): %s]" % (datestamp, channel, username, message)
            poop.append(line)

        self.something = self.add(
            npyscreen.Pager,
            name='Something',
            values=poop)

class Interface(npyscreen.NPSAppManaged):
    """Run that bad boy."""

    def onStart(self):
        self.alobj = Algolia() # pylint: disable=attribute-defined-outside-init
        self.addForm('MAIN', Formy, name='Ubuntu IRC log interface')
        self.addForm('RESULTDISPLAY', ResultDisplay, name='Results!')

# A little main magic.
def main():
    """Run this."""

    interface = Interface()
    interface.run()

# Ok let's do the thing.
if __name__ == '__main__':
    main()
