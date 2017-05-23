from algoliasearch import algoliasearch

class AlgoliaHelper(object):
    """Handles the Algolia stuff."""

    def __init__(self):
        self.app_id = 'PBF4ZR3KBT'
        self.api_key = '9188cd13a0dbf3d0af949802b0e31489' # search-only
        self.index_name = 'ubuntu_irc_logs'

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
            'hitsPerPage': 1000
        }

        # Keep it simple.
        self.client = algoliasearch.Client(self.app_id, self.api_key)
        self.index = self.client.init_index(self.index_name)

    def get_channels(self):
        """Get a list of indexed channels."""

        criteria = {'facets': 'channel'}
        results = self.index.search(
            '',
            dict(self.restricted_search, **criteria)
        )

        return results['facets']['channel'].keys()

    def do_a_search(self, query, criteria):
        """Execute a generic search based on some criteria."""

        results = self.index.search(
            query,
            dict(self.general_search, **criteria)
        )

        return results

    def get_irc_logs(self, timestamp, channel):
        """Search for IRC logs given a datestamp and criteria."""

        # Because we're only interested in exact timestamp hits, we need the
        # ranking info in order to filter out inexact results.
        criteria = {
            'facetFilters': ['channel:' + channel],
            'getRankingInfo': 1
        }
        results = self.index.search(
            timestamp,
            dict(self.general_search, **criteria)
        )

        returnable = []
        for hit in results['hits']:
            if hit['_rankingInfo']['proximityDistance'] <= 3:
                returnable.append('[' + hit['datestamp'] + '] ' + \
                    hit['username'] + ': ' + hit['message'])

        return returnable

    def get_most_recent_user_stamp(self, username):
        """Get the timestamp of the most recent log line for a user."""

        criteria = {
            'facetFilters': ['username:' + username],
            'getRankingInfo': 1
        }
        results = self.index.search(
            '',
            dict(self.general_search, **criteria)
        )

        # The datestamp field is ordered ascending, but we want the last one,
        # so we have to get the entire result list then pick the final item.
        returnable = results['hits'][(results['nbHits'] - 1)]['datestamp']

        return returnable

    def get_userinfo(self, username):
        """Get information about a user."""

        criteria = {
            'getRankingInfo': 1,
            'facets': '*',
        }
        results = self.index.search(
            username,
            dict(self.restricted_search, **criteria)
        )

        returnable = {}
        returnable['channels'] = results['facets']['channel'].keys()
        returnable['messages'] = results['nbHits']
        returnable['firstseen'] = results['hits'][0]['datestamp']

        return returnable
