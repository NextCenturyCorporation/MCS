import shutil
import unittest
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from machine_common_sense.unity_executable_provider import (
    AbstractExecutionCache, Downloader, UnityExecutableProvider)

TEST_TMP = "./tmp"
TEST_CACHE_LOCATION = "./tmp/.mcs-test"
TEST_ZIP = "./tmp/test.zip"


class MockExecutionCache(AbstractExecutionCache):
    EXECUTABLE_FILE = "MCS-AI2-THOR-Unity-App-v.x86_64"

    def has_version(self, version: str) -> bool:
        ver_dir = self._get_version_dir(version)
        return ver_dir.exists()

    def _do_zip_to_cache(self, version: str, zip_file: Path):
        pass

    def _do_get_execution_location(self, version: str) -> Path:
        ver_dir = self._get_version_dir(version)
        return ver_dir.joinpath(self.EXECUTABLE_FILE.format(version))


class MockDownloader(Downloader):
    count = 0

    def download(self, url: str, filename: str,
                 destination_folder: Path) -> Path:
        self.count = self.count + 1
        path = shutil.copy(
            TEST_ZIP, destination_folder.joinpath(filename).as_posix())
        return Path(path)


class TestUnityExecutableProvider(unittest.TestCase):

    def setUp(cls):
        AbstractExecutionCache.CACHE_LOCATION = TEST_CACHE_LOCATION
        cls.provider = UnityExecutableProvider()
        cls.cache = MockExecutionCache()
        cls.provider._cache = cls.cache
        cls.provider._downloader = MockDownloader()
        file = Path(TEST_ZIP)
        zip = ZipFile(file, 'w', ZIP_DEFLATED)
        executable = Path(TEST_TMP).joinpath(cls.cache.EXECUTABLE_FILE)
        executable.touch()
        zip.write(executable, cls.cache.EXECUTABLE_FILE)
        zip.close()

    def tearDown(cls):
        shutil.rmtree(TEST_CACHE_LOCATION)
        shutil.rmtree(TEST_TMP)

    def test_provider_init(self):
        self.assertTrue(Path(TEST_CACHE_LOCATION).exists())

    def test_get_executable_empty(self):
        result = self.provider.get_executable("test")
        self.assertTrue(result.exists())

    def test_get_executable_cache(self):
        self.assertEquals(self.provider._downloader.count, 0)
        result = self.provider.get_executable("test2")
        self.assertTrue(result.exists())
        self.assertEquals(self.provider._downloader.count, 1)

        # try again and verify the downloader isn't called again.
        result = self.provider.get_executable("test2")
        self.assertTrue(result.exists())
        self.assertEquals(self.provider._downloader.count, 1)

    def test_culling(self):
        self.assertEquals(self.provider._downloader.count, 0)
        result1 = self.provider.get_executable("test1")
        self.assertTrue(result1.exists())
        self.assertEquals(self.provider._downloader.count, 1)

        # try again and verify the downloader isn't called again.
        result2 = self.provider.get_executable("test2")
        self.assertTrue(result2.exists())
        self.assertEquals(self.provider._downloader.count, 2)
        self.assertFalse(result1.exists())
        self.assertFalse(result1.parent.exists())


if __name__ == '__main__':
    unittest.main()
