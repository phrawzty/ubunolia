"""Urwid framework shamelessly lifted from:
https://github.com/izderadicka/xmpp-tester/blob/master/commander.py
To be fair, I cleaned it up and added comments, so it's not all gank. ;)"""
# pylint: disable=too-many-instance-attributes, too-few-public-methods, invalid-name, too-many-arguments


from collections import deque
import threading
import urwid

class UnknownCommand(Exception):
    """Generic unknown command handler."""

    def __init__(self, cmd):
        Exception.__init__(self, 'Unknown command: %s' %cmd)

class Interaction(object):
    """Base class that handles interactions with the Terminal."""

    def __init__(self):
        """Set up basic help and quit capabilites."""

        # Just like IRC except without a prefix slash. :P
        self._quit_cmd = ['quit', 'q']
        self._help_cmd = ['help', '?']

    def __call__(self, line):
        tokens = line.split()
        cmd = tokens[0].lower()
        args = tokens[1:]
        if cmd in self._quit_cmd:
            return Terminal.Exit
        elif cmd in self._help_cmd:
            return self.help(args[0] if args else None)
        elif hasattr(self, 'do_'+cmd):
            return getattr(self, 'do_'+cmd)(*args)
        else:
            raise UnknownCommand(cmd)

    def help(self, cmd=None):
        """Socorro!"""

        def std_help():
            """Rudimentary help text."""

            qc = '|'.join(self._quit_cmd)
            hc = '|'.join(self._help_cmd)
            res = 'Type [%s] command_name to get more help.\n' % hc
            res += 'Type [%s] to quit.\n' % qc

            cl = [name[3:] for name in dir(self) if name.startswith('do_') and len(name) > 3]
            res += 'Available commands: %s' %(' '.join(sorted(cl)))
            return res

        if not cmd:
            return std_help()
        else:
            try:
                fn = getattr(self, 'do_' + cmd)
                doc = fn.__doc__
                return doc or 'No documentation available for %s' %cmd
            except AttributeError:
                return std_help()

class FocusMixin(object):
    """Make a stab at mouse support, because why not?"""

    def mouse_event(self, size, event, button, x, y, focus):
        """Une souris verte, qui courait dans l'herbe..."""

        if focus and hasattr(self, '_got_focus') and self._got_focus:
            self._got_focus()
        return super(FocusMixin, self).mouse_event(size, event, button, x, y, focus)

class ListView(FocusMixin, urwid.ListBox):
    """This is how lines of text actually get displayed."""

    def __init__(self, model, got_focus, max_size=None):
        urwid.ListBox.__init__(self, model)
        self._got_focus = got_focus
        self.max_size = max_size
        self._lock = threading.Lock()

    def add(self, line):
        """Add (display) a line of text."""

        with self._lock: # pylint: disable=not-context-manager
            was_on_end = self.get_focus()[1] == len(self.body)-1
            if self.max_size and len(self.body) > self.max_size:
                del self.body[0]
            self.body.append(urwid.Text(line))
            last = len(self.body) - 1
            if was_on_end:
                self.set_focus(last, 'above')

class Input(FocusMixin, urwid.Edit):
    """Put the means of production into the hands of the worker."""

    signals = ['line_entered']

    def __init__(self, got_focus=None):
        """Provide a scrollable command history (up/down arrows)."""

        urwid.Edit.__init__(self)
        self.history = deque(maxlen=100)
        self._history_index = -1
        self._got_focus = got_focus

    def keypress(self, size, key):
        """Deal with *single* keypresses."""

        if key == 'enter':
            line = self.edit_text.strip()
            if line:
                urwid.emit_signal(self, 'line_entered', line)
                self.history.append(line)
            self._history_index = len(self.history)
            self.edit_text = u''

        if key == 'up':
            self._history_index -= 1
            if self._history_index < 0:
                self._history_index = 0
            else:
                self.edit_text = self.history[self._history_index]

        if key == 'down':
            self._history_index += 1
            if self._history_index >= len(self.history):
                self._history_index = len(self.history)
                self.edit_text = u''
            else:
                self.edit_text = self.history[self._history_index]
        else:
            urwid.Edit.keypress(self, size, key)

class Terminal(urwid.Frame):
    """Simple terminal UI."""

    # colours
    PALLETE = [('reversed', urwid.BLACK, urwid.LIGHT_GRAY),
               ('normal', urwid.LIGHT_GRAY, urwid.BLACK),
               ('error', urwid.LIGHT_RED, urwid.BLACK),
               ('green', urwid.DARK_GREEN, urwid.BLACK),
               ('blue', urwid.LIGHT_BLUE, urwid.BLACK),
               ('magenta', urwid.DARK_MAGENTA, urwid.BLACK)]

    class Exit(object):
        """Brexit means brexit."""

        pass

    def __init__(self, title='', cap='', cmd=None, max_size=100):
        """init."""

        self.header = urwid.Text(title)
        self.model = urwid.SimpleListWalker([])
        self.body = ListView(self.model, lambda: self._update_focus(False), max_size=max_size)
        self.input = Input(lambda: self._update_focus(True))

        footer = urwid.Pile(
            [urwid.AttrMap(urwid.Text(cap), 'reversed'),
             urwid.AttrMap(self.input, 'normal')]
        )

        urwid.Frame.__init__(
            self,
            urwid.AttrWrap(self.body, 'normal'),
            urwid.AttrWrap(self.header, 'reversed'),
            footer
        )

        self.set_focus_path(['footer', 1])
        self._focus = True

        urwid.connect_signal(
            self.input,
            'line_entered',
            self.on_line_entered
        )

        self._cmd = cmd
        self._output_styles = [s[0] for s in self.PALLETE]
        self.eloop = None

    def loop(self, handle_mouse=False):
        """Threads are exciting!"""

        self.eloop = urwid.MainLoop(self, self.PALLETE, handle_mouse=handle_mouse)
        self._eloop_thread = threading.current_thread() # pylint: disable=attribute-defined-outside-init
        self.eloop.run()

    def on_line_entered(self, line):
        """User input!"""

        if self._cmd:
            try:
                res = self._cmd(line)
            except Exception, e: #pylint: disable=broad-except
                self.output('Error: %s' %e)
                return

            if res == Terminal.Exit:
                raise urwid.ExitMainLoop()
            elif res:
                self.output(str(res))

        else:
            self.output(line)

    def output(self, line):
        """Write to the screen."""

        self.body.add(line)

        # I told you threading was exciting!
        if self.eloop and self._eloop_thread != threading.current_thread():
            self.eloop.draw_screen()

    def _update_focus(self, focus):
        """Focus, padawan."""

        self._focus = focus

    def switch_focus(self):
        """Ooohh a shiny!"""

        if self._focus:
            self.set_focus('body')
            self._focus = False
        else:
            self.set_focus_path(['footer', 1])
            self._focus = True

    def keypress(self, size, key):
        """Deal with tab to change between commandline and window."""

        if key == 'tab':
            self.switch_focus()

        return urwid.Frame.keypress(self, size, key)
