import os
import sys

'''
Script will start Unity build with a flag to clear the addressables cache,
cache all the data in catalog and then close the application.

Usage: python cache_addressables.py <unity-build-path>
  unity-build-path: path to Unity AI2THOR build

See code details on how this works inside Unity in  the MCS AI2Thor code at
AddressablesUtil.Awake()

Normally, Unity caches what you use as you use it.  All MCS AI2Thor
executables use a small set of catalogs (dev, prod) and the caches are
commonly shared between executables.

'''


def run_caching_build(build_path):
    os.execl(build_path, build_path, "CACHEADDRESSABLES")


build_path = sys.argv[1]
run_caching_build(build_path)
