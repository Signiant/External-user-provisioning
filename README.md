# External User Provisioning Tool
Add or remove users from multiple web services with desired permissions and notify new user.
* AWS
* Papertrail
* Bitbucket
* Slack
* Azure
* Jira

 Notify only:
* Artifactory

## Usage

The User Provisioning Tool is a command line tool that accepts a path to the config file, the new user's email, the services to be run and custom permissions or groups for each service. The tool sends an email notifying the new user that emails from various services have been sent to them or by providing them with a link to a service that prompts them to activate their organization account.

example:

The following command creates a Bitbucket prod account in the developers group, a AWS dev2 account in ManageKeys and Developers groups ManageKeys and Developers and a Papertrail account with custom permissions.

    python3 user_provision.py
    	    -c "/External-user-provisioning-new/config-file/config.yaml" \
            -e test@gmail.com \
            -n "Full Name" \
            -p bitbucket:prod,aws:dev2,papertrail:dev \
            -l {'plugin':'bitbucket:','group1':'developers'};{'plugin':'aws:dev2','group1':'ManageKeys','group2':'Developers'};{'plugin':'papertrail:dev','user[email]':'test@gmail.com','user[read_only]':1,'user[manage_members]':0,'user[manage_billing]':0,'user[purge_logs]':0}

Required:
* -c : provide a file path to your config file
* -e : the email of the new user you will be adding/removing
* -p or -r : name of the services to be run separated by semicolons (-p to add and -r to remove)
* -n : new user's full name

Not Required:
* -l : plugins delimited and separated by semicolons with the plugin name as the first field.

## Sample Notification Email
![Sample Email](https://raw.githubusercontent.com/Signiant/External-user-provisioning/master/project/samples/sample-email.png)


## Installing the Tool
Option 1:
1. Install python 3 or higher
2. Clone the repository at https://github.com/Signiant/External-user-provisioning
3. Run the tool from the project folder as a python app

Option 2:
 1. Install python 3 or higher
 2. In the terminal run:
 >     sudo pip3 install ExternalUserProvisioning
 3. Run the tool anywhere using the new console script "userprovision" with required arguments.


> userprovision -n "Full Name"  -c "/Users/user/PycharmProjects/External-user-provisioning-new/project/config-file/config.yaml" -e test@gmail.com -p papertrail:prod


## Setting up the Config File

A sample config file template is provided in /project/samples

#### Global fields
1. Enter the new users full name and organization
2. Enter email server authentication information

#### Papertrail
1. In Settings → Profile, make sure your Papertrail account has 'Manage users and permissions' capabilities.
2. Within the profile screen copy your Prod and Dev API Tokens to the two empty ApiToken fields.
3. Set default permissions in the config file.
> user[email] will be automatically be retrieved from the CLI and should be left blank.

#### BitBucket
1. When signed as an administrator go to  Settings → OAuth → OAuth consumers,  click on Add Consumer to create a key and secret; copy those values into the config file.
2. Set the name of the default groups in the config file.

#### Slack
1. Sign into your admin slack account then use the following link to generate your API token :
 https://api.slack.com/custom-integrations/legacy-tokens
2. Add the generated API token to the config file

#### AWS
1. Sign on AWS with your admin account and go to IAM service, in users find your account. In the security credentials tab under access keys create a key and secret. Enter those values into the config file.
2. Enter default groups

#### Azure Active Directory
1. Enter the administrator email and password.
2. Provide a group a default group.

#### Artifactory
1. The new user is created along with the AD account.
2. The User Provisioning tool sends a link telling the new user to activate their account using their AD username and password

#### Jira
1. Enter your username and password of your Jira administrator account.
2. Provide user groups


### Additional Information
 - Groups are required in either the config file or the command line
 - message_invite and message_remove are the messages included in the sent email
  - Once a user has been created within azure and aws, it is
   up to the administrator to reset their password and provide it to the
   user in a secure manner
   - Users are not deleted or set inactive in Jira. Instead users are
   removed from all groups.
   - for help: python3.6 user_provision.py --help
