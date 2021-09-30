import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()


def get_version():
    version_file = "machine_common_sense/_version.py"
    with open(version_file) as f:
        exec(compile(f.read(), version_file, "exec"))
    return locals()["__version__"]


MCS_VERSION = get_version()


setuptools.setup(
    name='machine_common_sense',
    version=MCS_VERSION,
    maintainer='Next Century, a wholly owned subsidiary of CACI',
    maintainer_email='mcs-ta2@machinecommonsense.com',
    url='https://github.com/NextCenturyCorporation/MCS/',
    description=('Machine Common Sense Python API'
                 ' to Unity 3D Simulation Environment'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    license='Apache-2',
    python_requires=">3.6",
    packages=setuptools.find_packages(),
    package_data={'': ['*.ini'], },
    install_requires=[
        'shapely>=1.7.0',
        'colour>=0.1.5',
        'opencv-python>=4.0',
        'matplotlib>=3.3',
        'msgpack>=1.0.0',
        'ai2thor==2.5.0',
        'scikit-image>=0.17.1',
        'dataclasses==0.8; python_version<"3.7"',
        'marshmallow>=3.5.2'
    ],
    entry_points={
        'console_scripts': [
            ('run_in_human_input_mode='
             'machine_common_sense.scripts.run_human_input:main'),
            ('run_scene_timer='
             'machine_common_sense.scripts.run_scene_timer:main'),
            ('cache_addressables='
             'machine_common_sense.scripts.cache_addressables:main')
        ]
    }
)
