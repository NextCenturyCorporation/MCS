
from abc import ABC, abstractmethod
import logging
from zipfile import ZipFile
import tarfile
import requests
from progressbar import ProgressBar, Bar, Percentage, FileTransferSpeed
import platform
from machine_common_sense.logging_config import LoggingConfig
from pathlib import Path

# change to __name__ before mrege
logger = logging.getLogger("machine_common_sense")

LINUX_URL = "https://ai2thor-unity-releases.s3.amazonaws.com/" + \
    "MCS-AI2-THOR-Unity-App-v{}-linux.zip"
MAC_URL = "https://ai2thor-unity-releases.s3.amazonaws.com/" + \
    "MCS-AI2-THOR-Unity-App-v{}-mac.zip"


TEST_OVERRIDE = "http://ipv4.download.thinkbroadband.com/5MB.zip"

PLATFORM_MAC = "Darwin"
PLATFORM_LINUX = "Linux"
PLATFORM_OTHER = "other"

current_version = "0.4.2"


# TODO before code review - if reviewer sees this, yell at developer!
# Add option to clear force a new download
# Do we want cleanup?

class Ai2thorProvider():
    def __init__(self):
        self._downloader = Downloader()
        self._platform_init()

    def _platform_init(self):
        self._switcher = {
            PLATFORM_LINUX: self._linux_init,
            PLATFORM_MAC: self._mac_init,
            PLATFORM_OTHER: self._other_init
        }
        sys = platform.system()
        self._switcher.get(sys, PLATFORM_OTHER)()

    def _mac_init(self):
        self._cache = MacExecutionCache()

    def _linux_init(self):
        self._cache = LinuxExecutionCache()

    def _other_init(self):
        raise Exception(
            "Ai2thorProvider only supports Linux and Mac.  Platform={}".format(
                platform.system()))

    def get_executable(self, version=current_version,
                       download_if_missing=True, ) -> Path:
        '''For a given version, this will return the path to that executable
        or throw an exception if it cannot be found.
        '''
        if self._cache.has_version(version):
            return self._cache.get_execution_location(version)
        if (download_if_missing):
            url = self._downloader.get_url(version)
            dest = self._cache._get_version_dir(version)
            dest.mkdir(exist_ok=True, parents=True)
            zip_file = self._downloader.download(url, dest)
            self._cache.add_zip_to_cache(version, zip_file)
            return self._cache.get_execution_location(version)
        else:
            raise Exception(
                "unable to locate ai2thor for version={}".format(version))


CACHE_LOCATION = "~/.mcs/"


class AbstractExecutionCache(ABC):

    def __init__(self):
        '''
        '''
        cache_base = Path(CACHE_LOCATION).expanduser()
        self._base = cache_base
        if not cache_base.exists():
            cache_base.mkdir()
            logger.debug(
                "Created mcs cache at {}".format(
                    cache_base.as_posix()))

    def _get_version_dir(self, version: str) -> Path:
        '''returns a Path object for the path to the directory for the given
         version.
        '''
        ver_path = self._base.joinpath(version)
        return ver_path

    def add_zip_to_cache(self, version, zip_file):
        ver_dir = self._get_version_dir(version)
        zip = ZipFile(zip_file)
        zip.extractall(ver_dir)
        self._do_zip_to_cache(version, zip_file)

    def _unzip_tar_gz(self, tar_gz_file: Path, dest: Path):
        tar = tarfile.open(tar_gz_file.as_posix(), "r:gz")
        tar.extractall(path=dest.as_posix())
        tar.close()

    def remove_cache(self, version):
        # todo need to delete files
        self._get_version_dir(version).rmdir()

    @abstractmethod
    def has_version(self, version: str) -> bool:
        pass

    @abstractmethod
    def _do_zip_to_cache(self, version: str, zip_file: Path):
        pass

    @abstractmethod
    def get_execution_location(self, version: str) -> Path:
        pass


class MacExecutionCache(AbstractExecutionCache):
    APP_FILE = "MCS-AI2-THOR-Unity-App-v{}.app"

    def __init__(self):
        AbstractExecutionCache.__init__(self)

    def has_version(self, version: str) -> bool:
        ver_dir = self._get_version_dir(version)
        app = ver_dir.joinpath(self.APP_FILE.format(version))
        return ver_dir.exists() and app.exists()

    def _do_zip_to_cache(self, version: str, zip_file: Path):
        pass

    def get_execution_location(self, version: str) -> Path:
        ver_dir = self._get_version_dir(version)
        return ver_dir.joinpath(self.APP_FILE.format(version))

    # MAC appears to have MCS-AI2-THOR-Unity-App-v0.4.2.app folder, but need
    # to verify later


class LinuxExecutionCache(AbstractExecutionCache):
    REQUIRED_FILES = [
        "LinuxPlayer_s.debug",
        "UnityPlayer.so",
        "UnityPlayer_s.debug",
        "MCS-AI2-THOR-Unity-App-v{version}_Data",
        "MCS-AI2-THOR-Unity-App-v{version}.x86_64"]
    EXECUTABLE_FILE = "MCS-AI2-THOR-Unity-App-v{version}.x86_64"
    GZ_FILES = ["MCS-AI2-THOR-Unity-App-v{version}_Data.tar.gz"]

    def __init__(self):
        AbstractExecutionCache.__init__(self)

    def _do_zip_to_cache(self, version: str, zip_file: Path):
        '''Linux distributable contains a tar.gz file that needs unzipped
        The executable file needs to be turned to executable
        '''
        ver_dir = self._get_version_dir(version)
        file = self.EXECUTABLE_FILE.format(version=version)
        ver_dir.joinpath(file).chmod(755)

        for file in self.GZ_FILES:
            file = file.format(version=version)
            self._unzip_tar_gz(ver_dir.joinpath(file), ver_dir)

    def has_version(self, version: str) -> bool:
        ver_dir = self._get_version_dir(version)
        if not ver_dir.exists():
            return False
        for file in self.REQUIRED_FILES:
            file = file.format(version=version)
            exists = ver_dir.joinpath(file).exists()
            if not exists:
                logger.info("Missing file: " + file)
                return False
        return True

    def get_execution_location(self, version: str) -> Path:
        ver_dir = self._get_version_dir(version)
        exec = ver_dir.joinpath(self.EXECUTABLE_FILE.format(version=version))
        return exec


class Downloader():

    # TODO change default to current?
    def get_url(self, ver=None):
        if ver is None:
            # todo latest or current?
            ver = "0.4.2"

        sys = platform.system()
        if (sys == "Windows"):
            raise Exception("Windows is not supported")
        elif (sys == "Linux"):
            return LINUX_URL.format(ver)
        elif (sys == "Darwin"):
            return MAC_URL.format(ver)
        else:
            raise Exception("OS '{}' not supported".format(sys))

    def download(self, url: str, destination_folder: Path) -> Path:
        file_data = self._do_download(url)
        # todo probably change this
        zip_file_name = "ai2thor.zip"
        zip_file = destination_folder.joinpath(zip_file_name)
        zip_file.write_bytes(file_data)
        return zip_file

    # TODO should probably change how we download so we can write file
    # sequentially
    def _do_download(self, url):
        test_override = False
        if test_override:
            url = TEST_OVERRIDE

        logger.debug("Downloading file from %s" % url)
        r = requests.get(url, stream=True)
        r.raise_for_status()
        size = int(r.headers["Content-Length"].strip())
        total_bytes = 0

        widgets = [
            url.split("/")[-1],
            ": ",
            Bar(),
            Percentage(),
            " ",
            FileTransferSpeed(),
            " of {0}MB".format(str(round(size / 1024 / 1024, 2))[:4]),
        ]

        pbar = ProgressBar(widgets=widgets, maxval=size).start()
        # m = hashlib.sha256()
        file_data = []
        for buf in r.iter_content(1024):
            if buf:
                file_data.append(buf)
                # m.update(buf)
                total_bytes += len(buf)
                pbar.update(total_bytes)
        pbar.finish()
        # if m.hexdigest() != sha256_digest:
        #    raise Exception("Digest mismatch for url %s" % url)

        return b"".join(file_data)


LoggingConfig.init_logging(LoggingConfig.get_dev_logging_config())
provider = Ai2thorProvider()
executable = provider.get_executable("0.4.1")
logger.debug("ret: " + executable.as_posix())


# d = Downloader()
# url = d.get_url()
# temp = d.download(url)
# logger.debug(temp)
