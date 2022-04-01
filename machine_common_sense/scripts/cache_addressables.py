import argparse
import os

from machine_common_sense.unity_executable_provider import \
    UnityExecutableProvider

'''
Script will start Unity build with a flag to clear the addressables cache,
cache all the data in catalog and then close the application.

Usage: python cache_addressables.py <unity-build-path>
  unity-build-path: path to Unity AI2THOR build

See code details on how this works inside Unity in  the MCS AI2Thor code at
AddressablesUtil.Awake()

Normally, Unity caches what you use as you use it.  All MCS AI2Thor
executables use the same catalogs the cache is commonly shared between
executables.

'''


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build_path',
                        help="Unity build path.",
                        required=False,
                        default=None)
    return parser.parse_args()


def run_caching_build(build_path):
    os.execl(build_path, build_path, "CACHEADDRESSABLES")


def main():
    args = parse_args()
    path = args.build_path
    if not path:
        path = UnityExecutableProvider().get_executable(force_download=True)
    run_caching_build(path)


if __name__ == '__main__':
    main()
