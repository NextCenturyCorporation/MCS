import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='mcs_python_api',  
    package_dir={'':'python_api'},
    version='0.0.1',
    scripts=['run_mcs_human_input'] ,
    author='Next Century, a wholly owned subsidiary of CACI',
    author_email='mcs-ta2@machinecommonsense.com',
    description='Machine Common Sense Python API to Unity 3D Simulation Environment',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/NextCenturyCorporation/MCS/',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache License',
        'Operating System :: OS Independent',
    ]
)
