from setuptools import setup
from os import path

this_dir = path.abspath(path.dirname(__file__))
with open(path.join(this_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='awsrightsizer',
    version='1.0.2',
    packages=['rightsizer'],
    url='https://github.com/gregoryjordanm/awsrightsizer.git',
    license='Apache-2.0',
    author='Jordan M Gregory',
    author_email='gregory.jordan.m@gmail.com',
    description='A tool to help you determine the correct instance types to use for your running EC2/RDS instances.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3 :: Only'
    ],
    install_requires=[
        'boto3',
    ],
    entry_points={
          'console_scripts': [
              'rightsizer = rightsizer.main:main'
          ]
      },
)
