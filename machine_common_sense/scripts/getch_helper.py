# Source:
# https://stackoverflow.com/questions/510357/python-read-a-single-character-from-the-user

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""

    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            try:
                self.impl = _GetchUnix()
            except ImportError:
                self.impl = _GetchMacCarbon()

    def __call__(self):
        return self.impl()


class _GetchUnix:
    def __init__(self):
        import sys  # noqa: F401
        import tty  # noqa: F401

    def __call__(self):
        import sys
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt  # pylint: disable=import-error # noqa: F401

    def __call__(self):
        import msvcrt  # pylint: disable=import-error # noqa: F401
        return msvcrt.getch()


class _GetchMacCarbon:
    """
    A function which returns the current ASCII key that is down;
    if no ASCII key is down, the null string is returned.  The
    page http://www.mactech.com/macintosh-c/chap02-1.html was
    very helpful in figuring out how to do this.
    """

    def __init__(self):
        import Carbon  # pylint: disable=import-error

        # pylint: disable= W0104
        Carbon.Evt  # see if it has this (in Unix, it doesn't)

    def __call__(self):
        import Carbon  # pylint: disable=import-error
        if Carbon.Evt.EventAvail(0x0008)[0] == 0:  # 0x0008 is the keyDownMask
            return ''
        #
        # The event contains the following info:
        # (what, msg, when, where, mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
        #
        # The message (msg) contains the ASCII char which is
        # extracted with the 0x000000FF charCodeMask; this
        # number is converted to an ASCII character with chr() and
        # returned
        #
        (what, msg, *other) = Carbon.Evt.GetNextEvent(0x0008)[1]
        return chr(msg & 0x000000FF)


getch = _Getch()
