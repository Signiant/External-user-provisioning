# External-user-provisioning
Add or remove users from multiple web services with desired permissions
* AWS
* Papertrail
* Bitbucket
* Slack
* Azure
* Jira
#### Notify only:
* Artifactory

## Sample Notification Email
<!---![Sample Report](https://raw.githubusercontent.com/Signiant/aws-team-cost-reporter/master/images/sample_email2.jpg)-->

## Prerequisites
* you must have python 3.0 or higher installed
* installation:
pip install

## Usage

The User Provisioning Tool is a command line tool that accepts a path to the config file, the new user's email, the services to be run and custom permissions or groups for each service.

example:

-c "/Users/elaroche/PycharmProjects/External-user-provisioning-new/config-file/config.yaml" -e test@gmail.com -p github:prod;aws:dev2 -l {'plugin':'bitbucket','group1':'developers'};{'plugin':'aws- dev2','group1':'IAMChangeMyPW','group2':'Developers'};{'plugin':'papertrail-dev','user[email]':'test@gmail.com','user[read_only]':1,'user[manage_members]':0,'user[manage_billing]':0,'user[purge_logs]':0};{'plugin':'papertrail-prod','user[email]':'test@gmail.com','user[read_only]':1,'user[manage_members]':0,'user[manage_billing]':0,'user[purge_logs]':0}
* -c : provide a path to where your config file is located
* -e : the email of the new user you will be adding/removing
* -p or -r : name of the services to be run separated by semicolons (-p to add and -r to remove)
* -l : plugins delimited and separated by semicolons with the plugin name as the first field.

## Setting up the Config File

A sample template is provided in

#### Global fields
1. Enter the new users full name and organization in first 2 fields
2. Enter email server authentication

#### Papertrail
1. In Settings → Profile, make sure your Papertrail account has 'Manage users and permissions' capabilities.
2. Within the profile screen copy your Prod and Dev API Tokens to the two empty ApiToken fields.
3. Set default permissions in the config file.
> user[email] will be automatically be retrieved from the CLI and should be left blank.

#### Slack
1. Sign into your admin slack account then use the following link to generate your API token :
 https://api.slack.com/custom-integrations/legacy-tokens
2. Add the generated API token to the config file

#### Artifactory
1. The new user is created along with the AD account.
2. The User Provisioning tool sends a link telling the new user to activate their account using their AD username and password

#### AWS
1. Sign on AWS with your admin account and go to IAM service, in users find your account. In the security credentials tab under access keys create a key and secret. Enter those values into the config file. Do this for both AWS environments.
2. Enter the default groups

#### Azure Active Directory
1.  Enter the administrator email and password.
2. Provide a group for the new user to be added to.

#### Jira
1. Enter your username and password of your Jira administrator account.
