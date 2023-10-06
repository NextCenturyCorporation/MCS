import builtins
from types import ModuleType

import portalocker


class MockFcntl(ModuleType):
    """
    The fcntl module is not available on Windows; if it's not found, then
    return this mock module which wraps calls to the portalocker library.
    The ai2thor python library depends on its "lockf" function and some static
    variables.
    """

    LOCK_SH = 1
    LOCK_EX = 2
    LOCK_NB = 4
    LOCK_UN = 8

    def lockf(self, lock_file, lock_mode):
        if lock_mode == self.LOCK_SH:
            portalocker.lock(lock_file, portalocker.LockFlags.SHARED)
        if lock_mode > self.LOCK_SH and lock_mode < self.LOCK_UN:
            portalocker.lock(lock_file, portalocker.LockFlags.EXCLUSIVE)
        if lock_mode == self.LOCK_UN:
            portalocker.unlock(lock_file)


class MockModule(ModuleType):
    def __getattr__(self, key):
        return None
    __all__ = []


def mock_import(name, *args, **kwargs):
    try:
        real_module = real_import(name, *args, **kwargs)
        return real_module
    except ImportError as e:
        # Return mocks for all modules required by the ai2thor python library
        # but not available on Windows.
        if name == 'fcntl':
            return MockFcntl(name)
        if name in ['termios', 'tty']:
            return MockModule(name)
        raise e


# Override the built-in import function with mock_import, but save the original
# import function as real_import.
real_import, builtins.__import__ = builtins.__import__, mock_import
