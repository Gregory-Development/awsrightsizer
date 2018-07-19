from setuptools import setup

setup(
    name='awsrightsizer',
    version='1.0.1',
    packages=['rightsizer'],
    url='https://github.com/gregoryjordanm/awsrightsizer.git',
    license='Apache-2.0',
    author='Jordan M Gregory',
    author_email='gregory.jordan.m@gmail.com',
    description='A tool to help you determine the correct instance types to use for your running EC2/RDS instances.',
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
