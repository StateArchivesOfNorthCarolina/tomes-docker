from setuptools import setup, find_packages

setup(
    name='eaxs2json',
    version='0.0.1',
    packages=find_packages(),
    url='https://github.com/StateArchivesOfNorthCarolina',
    license='',
    author='Jeremy M. Gibson',
    author_email='jeremy.gibson@ncdcr.gov',
    description='',
    install_requires=[
        "elasticsearch>=6.0.0,<7.0.0",
    ]
)
