import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='machine_common_sense',
    version='0.1.0',
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
    install_requires=[
        'shapely>=1.7.0',
        'boto3>=1.15',
        ('ai2thor @ '
         'git+https://github.com/NextCenturyCorporation/ai2thor#egg=ai2thor')
    ],
    entry_points={
        'console_scripts': [
            'run_in_human_input_mode=scripts.run_human_input:main',
            'run_scene_timer=scripts.run_scene_timer:main'
        ]
    }
)
