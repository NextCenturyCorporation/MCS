import sys
import os

def run_caching_build(build_path):
        os.execl(build_path, build_path, "CACHEADDRESSABLES")

build_path = sys.argv[1]
run_caching_build(build_path)