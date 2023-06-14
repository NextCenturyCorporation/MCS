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
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Games/Entertainment :: Simulation',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
        'Typing :: Typed'
    ],
    license='Apache-2',
    python_requires=">=3.7,<3.11",
    packages=setuptools.find_packages(),
    package_data={'': ['*.ini'], },
    install_requires=[
        'ai2thor==2.5.0',
        'colour==0.1.5',
        'importlib-metadata==4.2.0; python_version<"3.8"',
        'importlib-metadata==6.3.0; python_version>="3.8"',
        'matplotlib==3.5.3; python_version<"3.8"',
        'matplotlib==3.7.1; python_version>="3.8"',
        'msgpack==1.0.5',
        'numpyencoder==0.3.0',
        'opencv-python==4.4.0.46; python_version<="3.9"',
        'opencv-python==4.5.4.60; python_version>="3.10"',
        'pydantic==1.10.7',
        'requests==2.31.0',
        'scikit-image==0.19.3',
        'Shapely==1.7.1; python_version<"3.10"',
        'Shapely==1.8.5; python_version>="3.10"',
        'typeguard==3.0.2'
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
