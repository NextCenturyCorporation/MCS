from pathlib import Path
import shutil
import unittest

from machine_common_sense.unity_executable_provider import (
    UnityExecutableProvider, AbstractExecutionCache)


class TestUnityExecutableProvider(unittest.TestCase):
    test_cache_location = "./tmp/.mcs-test"

    @classmethod
    def setUpClass(cls):
        AbstractExecutionCache.CACHE_LOCATION = cls.test_cache_location
        cls.provider = UnityExecutableProvider()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_cache_location)
        shutil.rmtree("./tmp")

    def test_provider_init(self):
        print(Path("./").absolute())
        self.assertTrue(Path(self.test_cache_location).exists())


if __name__ == '__main__':
    unittest.main()
