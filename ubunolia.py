"""A console interface to the Ubuntu IRC logs using an Algolia backend."""
# pylint: disable=invalid-name


from threading import Thread
from algoliahelper import algoliahelper
from turwidal import turwidal


# Run Lola Run!
if __name__ == '__main__':
    # Init with a quick sanity check.

    class Ubunolia(turwidal.Interaction):
        """Extend the Interaction class."""

        def do_connect(self):
            """Connect to the pretend server."""

            # Instantiante the Aloglia object. Come at me, Pythonistas.
            self.algolia = algoliahelper.AlgoliaHelper() # pylint: disable=attribute-defined-outside-init

            # Start querying and dumping logs.
            import time
            def run():
                """This is the thread that injects IRC logs into the window."""

                while True:
                    # Ideally we could set which day we wanted to replay. :P
                    day = '2017-05-16T'
                    hhmm = time.strftime('%H:%M')
                    datestamp = day + hhmm

                    # Ideally we would be able to switch channels. :P
                    logs = self.algolia.get_irc_logs(datestamp, 'ubuntu')
                    for line in logs:
                        terminal.output(line)
                        # Simulate a running conversation by breaking up each
                        # minute-block by the number of log lines from that
                        # minute. HAHA "simulate"
                        #terminal.output('sleeping ' + str(60/len(logs)) + ' seconds.')
                        time.sleep(60 / len(logs))

            thread = Thread(target=run)
            thread.daemon = True
            thread.start()

            return 'Connected to irc://irc.ubuntu.com/#ubuntu'

        def do_list(self):
            """List the channels."""

            channels = self.algolia.get_channels()
            obj = 'Channel list:\n'
            for channel in channels:
                obj = obj + '#' + channel + '\n'

            return obj

        def do_whois(self, username):
            """Get info about a username."""

            whois = self.algolia.get_userinfo(username)

            obj = username + ' was first seen on ' + whois['firstseen'] + \
                '. Since then they have sent ' + str(whois['messages']) + \
                ' in the following channels: '

            for channel in whois['channels']:
                obj = obj + channel + ' '

            return obj

        def do_seen(self, username):
            """Do a "last seen" on a username."""

            lastseen = self.algolia.get_most_recent_user_stamp(username)

            obj = username + ' was last seen on: ' + lastseen

            return obj

    caption = 'Tab to switch focus to upper frame.'
    terminal = turwidal.Terminal(title='Ubunolia', cap=caption, cmd=Ubunolia())

    # Ok go forilla.
    terminal.loop()
