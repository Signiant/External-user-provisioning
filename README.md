# External User Provisioning Tool
Add or remove users from multiple web services with desired permissions and notify new user. Useful when a service does not support single sign-on or the plan cost to get single sign-on is prohibitivly expensive

Currently supports:

* AWS
* Papertrail
* Bitbucket
* Slack
* Azure
* Jira
* Artifactory

The tool is built using a plugin model so adding new services that have an API should be just a matter of dropping in a new plugin and associated configuration file changes.

## Usage

The User Provisioning Tool is a command line tool that accepts a path to the config file, the new user's email, the services to be run and custom permissions or groups for each service. The tool sends an email notifying the new user that emails from various services have been sent to them or by providing them with a link to a service that prompts them to activate their organization account.

## Example

The following command creates:
* a Bitbucket user in the prod account who is a member of the developers group
* an IAM user in the AWS dev2 account who is a member of the ManageKeys and Developers groups
* a user in Papertrail with custom permissions

```bash
python3 user_provision.py
    -c "/External-user-provisioning-new/config-file/config.yaml" \
    -e test@gmail.com \
    -n "Full Name" \
    -p bitbucket:prod,aws:dev2,papertrail:dev \
    -l {'plugin':'bitbucket:','group1':'developers'};{'plugin':'aws:dev2','group1':'ManageKeys','group2':'Developers'};{'plugin':'papertrail:dev','user[email]':'test@gmail.com','user[read_only]':1,'user[manage_members]':0,'user[manage_billing]':0,'user[purge_logs]':0}
```

### Required
* -c : a file path to your config file
* -e : the email of the new user you will be adding/removing
* -p or -r : name of the services to create accounts in separated by semicolons (-p to add, -r to remove)
* -n : new user's full name

### Optional
* -l : plugins delimited and separated by semicolons with the plugin name as the first field.

## Sample Notification Email
![Sample Email](https://raw.githubusercontent.com/Signiant/External-user-provisioning/master/project/samples/sample-email.png)


## Installing the Tool

Option 1 (clone)
1. Install python 3 or higher
2. Clone the repository at https://github.com/Signiant/External-user-provisioning
3. Run the tool from the project folder as a python app (see example above)

Option 2 (pip)
 1. Install python 3 or higher
 2. In the terminal run:
 >     sudo pip3 install ExternalUserProvisioning
 3. Run the tool anywhere using the new console script "userprovision" with required arguments.

```bash
userprovision -n "Full Name"  -c "/config-files/user-prov/config-file/config.yaml" -e test@gmail.com -p papertrail:prod
```

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
2. Enter default groups for the new user

#### Azure Active Directory
1. Enter the administrator email and password.
2. Provide a default group to add the new user to

#### Artifactory
1. At Signiant, we use SAML for artifactory
2. The User Provisioning tool sends a link telling the new user to activate their account using their AD username and password

#### Jira
1. Enter a username and password of your Jira administrator account
2. Provide groups to add the new user to

### Google Spreadsheet

To get OAuth2 credentials:

1. Log in into your account at https://console.developers.google.com
2. From the project drop-down, choose Create a new project, enter a name for the project, and optionally, edit the provided project ID. Click Create.
3. Choose enable apis and services at the top of the screen
4. Search for Googlde Drive API. Activate it.
5. Search for Google Sheets API. Activate it.
6. Go to 'Credentials' on the left side of the screen
7. Ignore the window called 'Create credentials'. Go to 'OAuth consent screeen' above it
8. Enter product name and press 'Save'
9. In the 'Credentials' window open the drop down menu under 'Create credentials' and choose 'OAuth client ID'
10. Choose 'Other' in the Application type, enter the name and press 'Create'
11. Press 'OK' to close the pop up window
12. Click on the download arrow on the right from the client IDs created
13. Move this file to your working directory and rename it 'client_secret.json'

Run the following command to install the library using pip:

pip install --upgrade google-api-python-client

If you need to add more columns into the spreadsheet:
1. Open spreadsheet.py
2. In the method writeHeaderColumnNamesToSheet(SPREADSHEET_ID, service, email, configMap) add columns' headers to "values2" section
3. In the method writeRowsToSheetToAddUser(SPREADSHEET_ID, email, plugin_tag, log, success) add values for new columns in 'values1'
4. In the method writeRowsToSheetToRemoveUser(SPREADSHEET_ID, log, success, plugin_tag) add values for new columns in 'values1'.
    Make sure that the new values of array rowForThisPlugin[] are properly indexed after new values are added

### Additional Information
 - Groups are required in either the config file or the command line
 - message_invite and message_remove are the messages included in the sent email
  - Once a user has been created within azure and aws, it is
   up to the administrator to reset their password and provide it to the
   user in a secure manner
   - Users are not deleted or set inactive in Jira. Instead users are
   removed from all groups.
   - for help:
 > python3.6 user_provision.py --help
