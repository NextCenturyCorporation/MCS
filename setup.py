import setuptools

with open('python_api/README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='machine_common_sense',
    version='0.0.10',
    maintainer='Next Century, a wholly owned subsidiary of CACI',
    maintainer_email='mcs-ta2@machinecommonsense.com',
    url='https://github.com/NextCenturyCorporation/MCS/',
    description='Machine Common Sense Python API to Unity 3D Simulation Environment',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    license='Apache-2',
    python_requires=">3.6",
    install_requires=[
        'shapely',
        'ai2thor @ git+https://github.com/NextCenturyCorporation/ai2thor#egg=ai2thor'
    ],
    package_dir={'':'python_api'},
    packages=setuptools.find_packages('python_api'),
    entry_points={
        'console_scripts':[
            'mcs_run_in_human_input_mode=machine_common_sense.run_mcs_human_input:main',
            'mcs_run_scene_timer=machine_common_sense.run_mcs_scene_timer:main'
        ]
    }
)
