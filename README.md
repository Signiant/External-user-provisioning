<img src="project/uptool.png" alt="uptool" width="200px"/>

# UP Tool

From Signiant Operations comes UP Tool. UP Tool allows you to easily change user credentials across a variety of services using a Python script.

## How It Works

UP Tool adds and removes users from services that provide a REST API to manage users. This is useful when a service does not support single sign-on (SSO), or SSO is too expensive to use.

UP Tool currently supports:

* Amazon Web Services
* Papertrail
* Bitbucket
* Slack
* Azure
* Jira
* Artifactory

UP Tool can be configured to work with any service that supports user provisioning via a REST API.

## Up and Running

### Install UP Tool as a package:
1. Install Python 3.6 or higher
2. Install uptool as a pip package:
    `sudo -H pip3 install --upgrade uptool`

### Developing UP Tool
1. Install Python 3.6 or higher.
2. Clone this repository.
3. Run `pip3 install -r project/requirements.txt` to install the dependencies.

## Running UP Tool from the Command Line

The UP Tool works via command line, and accepts a path to the config file, the new user's email, the services to be run and custom permissions or groups for each service. The tool sends an email notifying the new user that emails from various services have been sent to them or by providing them with a link to a service that prompts them to activate their organization account.

To provision a new user from the command line, use python3 to run the provisioning script:

```bash
$ uptool \
    -c "/External-user-provisioning-new/config-file/config.yaml" \
    -s "/External-user-provisioning-new/credentials/client_secret.json" \
    -e user@example.com \
    -n "User Name" \
    -p bitbucket:prod,aws:dev2,papertrail:dev \
    -l {'plugin':'bitbucket:','group1':'developers'};{'plugin':'aws:dev2','group1':'ManageKeys','group2':'Developers'};{'plugin':'papertrail:dev','user[email]':'test@gmail.com','user[read_only]':1,'user[manage_members]':0,'user[manage_billing]':0,'user[purge_logs]':0}
```

This command creates:

* a Bitbucket user who is a member of the developers group
* an IAM user in an AWS account named `dev2` as member of the ManageKeys and Developers groups
* a user in Papertrail with customized permissions

Once UP Tool finishes, copy the authentication link and paste it into your browser, the follow the authentication steps until you see a verification code.

Paste the authentication code back into UP Tool to verify the provision.

**Note**: If running in development, run the `user_provision.py` script.

### Options

* -c : a file path to your config.yaml file **(Required)**
* -s : a file path to your client_secret.json file **(Required)**
* -e : the email of the new user you will be adding/removing **(Required)**
* -p or -r : **provision** or **revoke** by name of the services to be provisioned, separated by semicolons **(Required)**
* -n : new user's full name **(Required)**
* -l : plugins delimited and separated by semicolons with the plugin name as the first field. **(Optional)**

## Sample Notification Email
![Sample Email](https://raw.githubusercontent.com/Signiant/External-user-provisioning/master/project/samples/sample-email.png)

## Setting up the Configuration File

A sample configuration file template is provided in `/project/samples`

### Global fields

1. Enter the new users full name and organization
2. Enter email server authentication information

### spreadsheet_database fields [click here to learn more](#google-spreadsheet)

1. Enter the id of the index spreadsheet. This will be updated by the tool and will contain a username to spreadsheet ID
2. Enter the name of this spreadsheet
3. Enter the folder id where you want to store all your spreadsheets
4. Enter the url of this folder

### Papertrail

1. In Settings → Profile, make sure your Papertrail account has 'Manage users and permissions' capabilities.
2. Within the profile screen copy your Prod and Dev API Tokens to the two empty ApiToken fields.
3. Set default permissions in the config file.
> user[email] will be automatically be retrieved from the CLI and should be left blank.

### BitBucket

1. When signed as an administrator go to  Settings → OAuth → OAuth consumers,  click on Add Consumer to create a key and secret; copy those values into the config file.
2. Set the name of the default groups in the config file.

### Slack

1. Sign into your admin slack account then use the following link to generate your API token :
 https://api.slack.com/custom-integrations/legacy-tokens
2. Add the generated API token to the config file

### AWS

1. Sign on AWS with your admin account and go to IAM service, in users find your account. In the security credentials tab under access keys create a key and secret. Enter those values into the config file.
2. Enter default groups for the new user

### Azure Active Directory

1. Enter the administrator email and password.
2. Provide a default group to add the new user to

### Artifactory

1. At Signiant, we use SAML for artifactory
2. The User Provisioning tool sends a link telling the new user to activate their account using their AD username and password

### Jira

1. Enter a username and password of your Jira administrator account
2. Provide groups to add the new user to

## Google Spreadsheet
The tool will create a Google spreadsheet for every user with information on the status of each plugin when a user is added or removed. To keep track of all of the individual user spreadsheets, an index spreadsheet is used. This contains the mapping of username to spreadsheet ID so that the tool can update the sheet when a user is removed.

**Note**:  You must create the index spreadsheet in Google drive first and configure the ID of this spreadsheet in the config file before running the tool

### OAuth2 Credentials required to access Google Drive and Sheets

In order for the tool to get authorization to Google drive, you must follow these steps to obtain oAuth credentials and place the values into you config.yaml file.

1. Log in into your Google account at https://console.developers.google.com
2. From the project drop-down, choose Create a new project, enter a name for the project, and optionally, edit the provided project ID. Click Create.
3. Choose enable APIs and services at the top of the screen
4. Activate Google Drive API and Google Sheets API.
6. Go to **Credentials** on the left side of the screen
7. Ignore the window called **Create credentials**; Instead, Go to the **OAuth consent screen** above it
8. Enter product name and press **Save**
9. In the **Credentials** window, open the drop down menu under **Create credentials** and choose **OAuth client ID**
10. Choose **Other** in the Application type, enter the name and press **Create**
11. Press **OK** to close the pop up window
12. Click on the download arrow on the right from the client IDs created. This will download a json file.
13. Move this json file to the project subdirectory of the repository you have cloned and rename it to _client_secret.json_

#### Client Id and Client Secret for a Microsoft Azure Active Directory
In order for the tool to be able to work with Azure Active Directory, you must follow these steps to obtain Client ID, Client Secret and Tenant ID credentials and place the values into you config.yaml file.


1. Sign in to the Azure portal.
2. Click on More Services on the left hand side, and choose Azure Active Directory.
3. Click on App registrations and choose Add.
4. Enter a name for the application and select ‘Web Application and/or Web API’ as the Application Type. Enter the base URL (“http://your_app_name”), then click on the Create button.
5. Click on Settings. Here you can see Client ID value.
6. Click on the Keys option.
7. When all the settings are saved, you will see the Client Secret.
8. To get Tenant ID:
    - Navigate to Dashboard
    - Navigate to ActiveDirectory
    - Navigate to Manage / Properties
    - Copy the "Directory ID"


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
    * In the method writeRowsToSheetToAddUser(SPREADSHEET_ID, email, plugin_tag, log, success) add values for new columns in 'values1'
    * In the method writeRowsToSheetToRemoveUser(SPREADSHEET_ID, log, success, plugin_tag) add values for new columns in 'values1'.

    Make sure that the new values of array rowForThisPlugin[] are properly indexed after new values are added
