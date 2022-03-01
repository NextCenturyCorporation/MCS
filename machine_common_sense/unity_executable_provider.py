import datetime
import glob
import logging
import platform
import shutil
import tarfile
from abc import ABC, abstractmethod
from pathlib import Path
from zipfile import ZipFile

import requests
from progressbar import Bar, FileTransferSpeed, Percentage, ProgressBar

from ._version import __version__

logger = logging.getLogger(__name__)

LINUX_URL = "https://github.com/NextCenturyCorporation/MCS/releases/download/{ver}/MCS-AI2-THOR-Unity-App-v{ver}-linux.zip"  # noqa
MAC_URL = "https://github.com/NextCenturyCorporation/MCS/releases/download/{ver}/MCS-AI2-THOR-Unity-App-v{ver}-mac.zip"  # noqa
LINUX_DEV_URL = "https://ai2thor-unity-releases.s3.amazonaws.com/MCS-AI2-THOR-Unity-App-vdevelop-linux.zip"  # noqa
MAC_DEV_URL = "https://ai2thor-unity-releases.s3.amazonaws.com/MCS-AI2-THOR-Unity-App-vdevelop-mac.zip"  # noqa


class UnityExecutableProvider():
    '''Automatically provides MCS AI2-THOR Unity executable for the MCS package.
    Will check a cache and download if necessary'''

    DOWNLOAD_FILE = "MCS-AI2-THOR-Unity-App-v{}.zip"
    PLATFORM_MAC = "Darwin"
    PLATFORM_LINUX = "Linux"
    PLATFORM_OTHER = "other"

    def __init__(self):
        self._downloader = Downloader()
        self._platform_init()

    def _platform_init(self):
        self._switcher = {
            self.PLATFORM_LINUX: self._linux_init,
            self.PLATFORM_MAC: self._mac_init,
            self.PLATFORM_OTHER: self._other_init
        }
        sys = platform.system()
        self._switcher.get(sys, self.PLATFORM_OTHER)()

    def _mac_init(self):
        self._cache = MacExecutionCache()

    def _linux_init(self):
        self._cache = LinuxExecutionCache()

    def _other_init(self):
        raise Exception(
            "Ai2thorProvider only supports Linux and Mac. "
            f"Platform={platform.system()}"
        )

    def clear_cache(self, version=None):
        '''clears the entire cache if no version is passed in, otherwise
        clears the specified version'''
        if version is None:
            self._cache.remove_whole_cache()
        else:
            self._cache.remove_cache_version(version)

    def get_executable(self, version=None,
                       download_if_missing=True, force_download=False) -> Path:
        '''For a given version, this will return the path to that executable
        or throw an exception if it cannot be found.
        '''
        if version is None:
            version = __version__
        if version in ["dev", "development", "develop"]:
            logger.warn(
                "Warning: Attempting to use development version of "
                "MCS-AI2Thor.  This is intended for developers only.")
            version = "develop"
            url = self._downloader.get_url(version)
            force_download |= self._downloader.is_updated(
                url, self._cache.modified_date(version))
        if not force_download and self._cache.has_version(version):
            return self._cache.get_execution_location(version)
        if (download_if_missing or force_download):
            url = self._downloader.get_url(version)
            dest = self._cache._get_version_dir(version)
            dest.mkdir(exist_ok=True, parents=True)
            zip_file_name = self.DOWNLOAD_FILE.format(version)
            zip_file = self._downloader.download(url, zip_file_name, dest)
            self._cache.add_zip_to_cache(version, zip_file)
            return self._cache.get_execution_location(version)
        else:
            raise Exception(
                f"unable to locate ai2thor for version={version}")


class AbstractExecutionCache(ABC):
    '''Handles platform agnostic (between Mac and Linux) code for running a
    cache for MCS Unity executables.  '''
    CACHE_LOCATION = Path.home() / ".mcs/"
    TIMESTAMP_FILE = ".timestamp"

    def __init__(self):
        cache_base = self.CACHE_LOCATION.expanduser()
        self._base = cache_base
        if not cache_base.exists():
            cache_base.mkdir(parents=True)
            logger.debug(
                f"Created mcs cache at {cache_base.as_posix()}")

    def get_execution_location(self, version: str) -> Path:
        '''Returns the location of the executable file'''
        ver_dir = self._get_version_dir(version)
        exec = ver_dir / self._get_executable_file().format(
            version=version)
        self.cull_cache(version)
        return exec

    def _get_version_dir(self, version: str) -> Path:
        '''returns a Path object for the path to the directory for the given
         version.
        '''
        return self._base / version

    def has_version(self, version: str) -> bool:
        '''Return whether the cache has the given version'''
        ver_dir = self._get_version_dir(version)
        if not ver_dir.exists():
            return False
        for file in self._get_required_files():
            file = file.format(version=version)
            exists = (ver_dir / file).exists()
            if not exists:
                logger.info(f"Missing file: {file}")
                return False
        return True

    def modified_date(self, version: str) -> datetime.datetime:
        mod_date = datetime.datetime.min
        if (self.has_version(version)):
            ver_dir = self._get_version_dir(version)
            path = (ver_dir / self.TIMESTAMP_FILE)
            if path.exists():
                return datetime.datetime.fromtimestamp(
                    path.stat().st_mtime)
        return mod_date

    def add_zip_to_cache(self, version, zip_file: Path):
        ver_dir = self._get_version_dir(version)
        zip = ZipFile(zip_file)
        logger.info(
            f"Unzipping {zip_file.name} to {ver_dir.as_posix()}")
        zip.extractall(ver_dir)
        logger.info(f"Deleting {zip_file.name}.")
        zip_file.unlink()
        ver_dir = self._get_version_dir(version)
        file = self._get_executable_file().format(version=version)
        (ver_dir / file).chmod(755)

        for file in self._get_gz_files():
            file = file.format(version=version)
            gz = ver_dir / file
            logger.info(
                f"Unzipping {gz.name} to {ver_dir.as_posix()}.")
            self._unzip_tar_gz(gz, ver_dir)
            logger.info(f"Deleting {gz.name}.")
            gz.unlink()
        (ver_dir / self.TIMESTAMP_FILE).touch()

    def _unzip_tar_gz(self, tar_gz_file: Path, dest: Path):
        tar = tarfile.open(tar_gz_file.as_posix(), "r:gz")
        tar.extractall(path=dest.as_posix())
        tar.close()

    def remove_cache_version(self, version):
        # todo need to delete files
        ver_dir = self._get_version_dir(version)
        shutil.rmtree(ver_dir)

    def remove_whole_cache(self):
        shutil.rmtree(self._base)

    def cull_cache(self, last_version: str):
        try:
            list = glob.glob(f"{self._base.as_posix()}/*")
            ver_dir = self._get_version_dir(last_version)
            for name in list:
                logger.debug(f"test: {name}")
                file = Path(name)
                keep = file.is_dir() and ver_dir.samefile(file)
                if not keep:
                    logger.debug(f"deleting {file.as_posix()}")
                    shutil.rmtree(file)
        except Exception:
            logger.exception(
                "Error attempting to cull MCS Unity executable cache", )

    @abstractmethod
    def _get_executable_file(self):
        pass

    @abstractmethod
    def _get_gz_files(self):
        pass

    @abstractmethod
    def _get_required_files(self):
        pass


class MacExecutionCache(AbstractExecutionCache):
    '''Handles Mac specific code for running a cache for MCS Unity executables.
    '''
    EXECUTABLE_FILE = "MCS-AI2-THOR-Unity-App-v{version}.app/Contents/MacOS/MCS-AI2-THOR"  # noqa
    REQUIRED_FILES = ["MCS-AI2-THOR-Unity-App-v{version}.app"]
    GZ_FILES = []

    def _get_executable_file(self):
        return self.EXECUTABLE_FILE

    def _get_gz_files(self):
        return self.GZ_FILES

    def _get_required_files(self):
        return self.REQUIRED_FILES


class LinuxExecutionCache(AbstractExecutionCache):
    '''Handles Linux specific code for running a cache for MCS Unity executables.
    '''
    REQUIRED_FILES = [
        "LinuxPlayer_s.debug",
        "UnityPlayer.so",
        "UnityPlayer_s.debug",
        "MCS-AI2-THOR-Unity-App-v{version}_Data",
        "MCS-AI2-THOR-Unity-App-v{version}.x86_64"]
    EXECUTABLE_FILE = "MCS-AI2-THOR-Unity-App-v{version}.x86_64"
    GZ_FILES = ["MCS-AI2-THOR-Unity-App-v{version}_Data.tar.gz"]

    def _get_executable_file(self):
        return self.EXECUTABLE_FILE

    def _get_gz_files(self):
        return self.GZ_FILES

    def _get_required_files(self):
        return self.REQUIRED_FILES


class Downloader():
    '''Handles downloading MCS AI2THOR package'''

    def get_url(self, ver):
        sys = platform.system()
        if (sys == "Windows"):
            raise Exception("Windows is not supported")
        elif sys == "Linux":
            return LINUX_URL.format(
                ver=ver) if ver != "develop" else LINUX_DEV_URL
        elif sys == "Darwin":
            return MAC_URL.format(ver=ver) if ver != "develop" else MAC_DEV_URL
        else:
            raise Exception(f"OS '{sys}' not supported")

    def download(self, url: str, filename: str,
                 destination_folder: Path) -> Path:
        file_data = self._do_download(url)
        # todo probably change this
        file = destination_folder / filename
        file.write_bytes(file_data)
        return file

    # TODO should probably change how we download so we can write file
    # sequentially
    def _do_download(self, url):
        logger.debug(f"Downloading file from {url}")
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
            f" of {str(round(size / 1024 / 1024, 2))[:4]}MB",
        ]

        pbar = ProgressBar(widgets=widgets, maxval=size).start()
        file_data = []
        for buf in r.iter_content(1024):
            if buf:
                file_data.append(buf)
                total_bytes += len(buf)
                pbar.update(total_bytes)
        pbar.finish()

        return b"".join(file_data)

    def is_updated(self, url, date: datetime.datetime):
        # Default to true?
        try:
            updated = True
            r = requests.get(url, stream=True)
            r.raise_for_status()
            last_mod = r.headers['last-modified']
            r.close()
            dt = datetime.datetime.strptime(
                last_mod,
                "%a, %d %b %Y %H:%M:%S %Z")
            updated = dt > date
        except Exception as e:
            logger.warn(
                "Error checking last modified of development build",
                exc_info=e)
        finally:
            return updated
