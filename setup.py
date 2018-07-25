from setuptools import find_packages
from distutils.core import setup

setup(name='uptool',
      version='1.0.6',
      description='The User Provisioning Tool (UP Tool) can add or remove users from multiple web services with desired permissions and notify new user. Useful when a service does not support single sign-on or the plan cost to get single sign-on is prohibitivly expensive',
      author_email='devops@signiant.com',
      url='https://www.signiant.com',
      packages=find_packages(),
      include_package_data=True,
      license='MIT',
      install_requires=['azure>=2.0.0', 'pytz>=2018.3', 'jenkinsapi>=0.2.23', 'paramiko>=2.4.0',
                        'botocore>=1.10.50', 'lxml>=4.2.3', 'requests>=2.4.3', 'boto3>=1.5.20',
                        'msrestazure>=0.4.21', 'PyYAML>=3.12', 'beautifulsoup4>=4.6.0', 'keyring>=11.0.0',
                        'oauth2client>=3.0.0', 'google-api-python-client>=1.4.2', 'httplib2>=0.9.1',
                        'setuptools>=38.5.1', 'six>=1.7', 'nose>=1.3.0', 'tornado>=4.5.1'],
      entry_points = {
              'console_scripts': [
                  'uptool = project.user_provision:main',
               ]
      }
)