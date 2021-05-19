from machine_common_sense.unity_executable_provider import (
    UnityExecutableProvider, AbstractExecutionCache)
import unittest
import shutil


class TestConfigManager(unittest.TestCase):
    test_cache_location = "~/.mcs-test"

    @classmethod
    def setUpClass(cls):
        AbstractExecutionCache.CACHE_LOCATION = cls.test_cache_location
        cls.provider = UnityExecutableProvider()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_cache_location)


if __name__ == '__main__':
    unittest.main()
