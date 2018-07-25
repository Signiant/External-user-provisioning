<img src="project/uptool.png" alt="uptool" width="200px"/>

# UP Tool

The User Provisioning Tool (UP Tool) can add or remove users from multiple web services with desired permissions and notify new user. Useful when a service does not support single sign-on or the plan cost to get single sign-on is prohibitivly expensive

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
    -s "/External-user-provisioning-new/credentials/client_secret.json" \
    -e test@gmail.com \
    -n "Full Name" \
    -p bitbucket:prod,aws:dev2,papertrail:dev \
    -l {'plugin':'bitbucket:','group1':'developers'};{'plugin':'aws:dev2','group1':'ManageKeys','group2':'Developers'};{'plugin':'papertrail:dev','user[email]':'test@gmail.com','user[read_only]':1,'user[manage_members]':0,'user[manage_billing]':0,'user[purge_logs]':0}
```

### Required
* -c : a file path to your config.yaml file
* -s : a file path to your client_secret.json file
* -e : the email of the new user you will be adding/removing
* -p or -r : name of the services to create accounts in separated by semicolons (-p to add, -r to remove)
* -n : new user's full name

### Optional
* -l : plugins delimited and separated by semicolons with the plugin name as the first field.


## Sample Notification Email
![Sample Email](https://raw.githubusercontent.com/Signiant/External-user-provisioning/master/project/samples/sample-email.png)


## Installing & Running the Uptool Using PyPi

The easiest way to run the tool is by using a pre build package (pypi).

1  _xcode-select --install_
2  _ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"_
3  _brew install python3_
4  _sudo -H pip3 install uptool_
5. _uptool -n "Test User" -c "/full_path_to_your_config_file/config.yaml" -s "/full_path_to_your_client_secret_file/client_secret.json" -e test@mail.com -p all_
6.  Copy the authentication link and paste it into your browser.
7. Follow the authentication steps until you see a verification code. Paste it into the bash shell.


## Installing & Running the Uptool Using Github

If you prefer to use this way to run the tool, you have to install all the required dependencies

1. Install python 3 or higher
2. Clone the repository at https://github.com/Signiant/External-user-provisioning
3. Run the tool from the project folder as a python app (see example above)

## Setting up the Config File

A sample config file template is provided in /project/samples

#### Global fields
1. Enter the new users full name and organization
2. Enter email server authentication information

#### spreadsheet_database fields [click here to learn more](#google-spreadsheet)
1. Enter the id of the index spreadsheet. This that will be updated by the tool and will contain a mapping of username to spreadsheet ID
2. Enter the name of this spreadsheet
3. Enter the folder id where you want to store all your spreadsheets
4. Enter the url of this folder

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

## Google Spreadsheets
The tool will create a Google spreadsheet for every user with information on the status of each pluing when the user is added or removed.  To keep track of all of the individual user spreadsheets, an index spreadsheet is used.  This contains the mapping of username to spreadsheet ID so that the tool can update the sheet when a user is removed.

> You must create the index spreadsheet in Google drive first and configure the ID of this spreadsheet in the config file before running the tool


#### OAuth2 Credentials required to access Google Drive and Sheets
In order for the tool to get authorization to Google drive, you must follow these steps to obtain oAuth credentials and place a file in the correct location before running the tool.

1. Log in into your google account at https://console.developers.google.com
2. From the project drop-down, choose Create a new project, enter a name for the project, and optionally, edit the provided project ID. Click Create.
3. Choose enable apis and services at the top of the screen
4. Search for Googlde Drive API. Activate it.
5. Search for Google Sheets API. Activate it.
6. Go to _Credentials_ on the left side of the screen
7. Ignore the window called _Create credentials_; Instead, Go to the _OAuth consent screeen_ above it
8. Enter product name and press _Save_
9. In the _Credentials_ window, open the drop down menu under _Create credentials_ and choose _OAuth client ID_
10. Choose _Other_ in the Application type, enter the name and press _Create_
11. Press _OK_ to close the pop up window
12. Click on the download arrow on the right from the client IDs created. This will download a json file 
13. Move this json file to the _project_ subdirectory of the repo you have cloned and rename it to _client_secret.json_


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
- If you need to add more columns into the spreadsheet for each user
    - Open spreadsheet.py
    - In the method writeHeaderColumnNamesToSheet(SPREADSHEET_ID, service, email, configMap) add columns' headers to "values2" section
    - In the method writeRowsToSheetToAddUser(SPREADSHEET_ID, email, plugin_tag, log, success) add values for new columns in 'values1'
    - In the method writeRowsToSheetToRemoveUser(SPREADSHEET_ID, log, success, plugin_tag) add values for new columns in 'values1'.
    Make sure that the new values of array rowForThisPlugin[] are properly indexed after new values are added


