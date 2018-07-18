from setuptools import setup, find_packages
from distutils.core import setup

setup(name='uptool',
      version='2.0',
      description='Python Automation Framework for Development Operations Teams',
      author_email='devops@signiant.com',
      url='https://www.signiant.com',
      packages=find_packages(),
      license='MIT',
      install_requires=['azure>=2.0.0', 'pytz>=2018.3', 'requests>=2.18.4', 'boto3>=1.5.20', 'msrestazure>=0.4.21', 'PyYAML>=3.12', 'beautifulsoup4>=4.6.0', 'keyring>=11.0.0', 'oauth2client>=3.0.0', 'google-api-python-client>=1.4.2', 'httplib2>=0.9.1', 'setuptools>=38.5.1'],
      entry_points = {
              'console_scripts': [
                  'uptool = project.user_provision:main',
               ]
      }
)
