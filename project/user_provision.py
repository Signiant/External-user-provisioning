import argparse
import getpass
import os
import sys
import yaml
import datetime
import logging
import azure,msrestazure
import azure.graphrbac
#internal modules
from project import mail
from project import plugin

def readConfigFile(path):
    configMap = []
    try:
        config_file_handle = open(path)
        configMap = yaml.load(config_file_handle)
        config_file_handle.close()
    except:
        print
        "Error: Unable to open config file %s or invalid yaml" % path
    return configMap

def getDate():
    return datetime.datetime.now()

def getJsonResponse(plugin,email, log, instruction):
    return {"Plugin name": plugin,
                    "Log": (email[:-13]+" "+getpass.getuser()+" "+getDate().strftime("%Y-%m-%d %H:%M") +" | "+ log),
                    "Instruction": instruction}

def main():

    logging.basicConfig(filename='example.log', level=logging.INFO)

    #Command Line
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    parser = argparse.ArgumentParser(description='External user provisioning tool')
    parser.add_argument('-n','--name', help='New user\'s full name',required=True)
    parser.add_argument('-e','--email', help='New user\'s email',required=True)
    parser.add_argument('-c','--config', help='Full path to a config file',required=True)
    parser.add_argument('-p','--plugin', help='The plugin(s) to add users seperated by commas.',required=False)
    parser.add_argument('-r','--remove', help='the plugin to execute to remove users',required=False)
    parser.add_argument('-l','--permission', help='permission for apps that can accept permissions as parameters. write as python dict',required=False)
    args = parser.parse_args()
    configMap = readConfigFile(args.config)

    availablePlugins=[]
    for plugin in configMap['plugins']:
        availablePlugins.append(plugin['plugin']+':'+plugin['tag'])

    allPermissions=[]
    if args.permission is not None:
        permissions= [x.strip() for x in args.permission.split(';')]
        for permission in permissions:
            allPermissions.append(permission)

    #Get entered plugins / all plugins
    plugins=getArgPlugins(args.plugin, configMap)
    pluginsremove=getArgPlugins(args.remove,configMap)
    email=args.email

    pluginInstruction = []
    if args.plugin is not None:
        runPlugins(configMap, plugins,email,allPermissions, pluginInstruction,availablePlugins,args.name,arg='add')
        print('sending email')
        mail.emailOutput(email, configMap, pluginInstruction, arg='add')
    if args.remove is not None:
        runPlugins(configMap, pluginsremove, email, allPermissions, pluginInstruction,availablePlugins,args.name,arg='remove')
        print('sending email')

        mail.emailOutput(email, configMap, pluginInstruction, arg='remove')

def runPlugins(configMap,plugins,email,allPermissions,pluginInstruction,availablePlugins,name,arg):

    for config_plugin in configMap['plugins']:
        plugin_tag = config_plugin['plugin']+':'+config_plugin['tag']
        pluginName = config_plugin['plugin']
        for requested_plugin in plugins:
            if plugin_tag == requested_plugin:
                if plugin_tag in availablePlugins:
                    plugin_handle = plugin.loadPlugin(pluginName)
                    if arg=='add':
                        print("Running invite: %s  " % plugin_tag)
                        json = (plugin_handle.inviteUser(email, configMap, allPermissions, plugin_tag, name))
                    if arg == 'remove':
                        print("Running remove: %s  " % plugin_tag)
                        json = (plugin_handle.removeUser(email, configMap, allPermissions, plugin_tag))
                    pluginInstruction.append(json)

                    logging.info(json['Log'])

def getArgPlugins(pluginsString,configMap):
    plugins=[]
    if pluginsString is not None:
        plugins = [x.strip() for x in pluginsString.split(',')]
        if plugins[0] == "all":
            plugins.pop()
            for config_plugin in configMap['plugins']:
                plugins.append(config_plugin['plugin']+':'+config_plugin['tag'])
    return plugins

def testRemoveEmail(email, configMap, arg='remove'):
    #remove
    pluginInstruction=[{'Plugin name': 'Papertrail dev', 'Log': 'test elaroche 2018-02-12 13:04 | papertrail:dev: test@signiant.com removed from papertrail.\n', 'Instruction': 'test removed from Papertrail Dev'}, {'Plugin name': 'Papertrail prod', 'Log': 'test elaroche 2018-02-12 13:04 | papertrail:prod: test@signiant.com removed from papertrail.\n', 'Instruction': 'test removed from Papertrail Prod'}, {'Plugin name': 'Bitbucket', 'Log': 'test elaroche 2018-02-12 13:04 | BitBucket: test@signiant.com removed from team.\n', 'Instruction': 'test removed from the Bitbucket signiant team.  '}, {'Plugin name': 'Slack', 'Log': "test elaroche 2018-02-12 13:04 | Slack: Remove from slack error: test@signiant.com does not exist or is already inactive\n error: 'user_id'\n", 'Instruction': "Remove from slack error: test@signiant.com does not exist or is already inactive. Exception caught: 'user_id'"}, {'Plugin name': 'Artifactory', 'Log': 'test elaroche 2018-02-12 13:04 | artifactory: test@signiant.com removed alongside AD account \n', 'Instruction': 'test is remove along with AD account'}, {'Plugin name': 'AWS dev1', 'Log': 'test elaroche 2018-02-12 13:04 | aws:dev1: test removed from organization.\n', 'Instruction': 'test was removed from AWS DEV1'}, {'Plugin name': 'AWS dev2', 'Log': 'test elaroche 2018-02-12 13:04 | aws:dev2: test removed from organization.\n', 'Instruction': 'test was removed from AWS DEV2'}, {'Plugin name': 'Azure Active Directory', 'Log': 'test elaroche 2018-02-12 13:04 | azure:dev1: test removed from azure AD.\n', 'Instruction': 'test removed from azure AD.'}, {'Plugin name': 'Jira Server', 'Log': 'test elaroche 2018-02-12 13:04 | jira:prod: test removed from jira.\n', 'Instruction': 'test removed from all groups'}]
    #add
    #pluginInstruction=[{'Plugin name': 'Papertrail dev', 'Log': 'test elaroche 2018-02-12 13:15 | papertrail:dev: Email invite sent from Papertrail.\n', 'Instruction': 'Look for your email invite from papertrail Dev in your inbox'}, {'Plugin name': 'Papertrail prod', 'Log': 'test elaroche 2018-02-12 13:15 | papertrail:prod: Email invite sent from Papertrail.\n', 'Instruction': 'Look for your email invite from papertrail Prod in your inbox'}, {'Plugin name': 'Bitbucket', 'Log': 'test elaroche 2018-02-12 13:15 | BitBucket: Email invite sent from Bitbucket.\n', 'Instruction': 'Look for your email invite from BitBucket in your inbox to join the Signiant team'}, {'Plugin name': 'Slack', 'Log': 'test elaroche 2018-02-12 13:15 | Slack: Instruction sent in email.\n', 'Instruction': 'Follow link to activate your account using your AD username and password: https://signiant-dev.slack.com/signup'}, {'Plugin name': 'Artifactory', 'Log': 'test elaroche 2018-02-12 13:15 | Artifactory: Instruction sent in email.\n', 'Instruction': 'Follow link to activate your account using your AD username and Password: https://signiant.atlassian.net/wiki/spaces/DevOps/pages/436082/NPM+setup+for+Signiant+s+Artifactory+Online+Repository'}, {'Plugin name': 'AWS dev1', 'Log': 'test elaroche 2018-02-12 13:15 | AWS: test added to aws:dev1\n', 'Instruction': 'You have been added to AWS signiantdev. Contact devops@signiant.com for your username and password.  https://signiantdev.signin.aws.amazon.com/console'}, {'Plugin name': 'AWS dev2', 'Log': 'test elaroche 2018-02-12 13:15 | AWS: test added to aws:dev2\n', 'Instruction': 'You have been added to AWS signiantdev2. Contact devops@signiant.com for your username and password. https://signiantdev2.signin.aws.amazon.com/console'}, {'Plugin name': 'Azure Active Directory', 'Log': 'test elaroche 2018-02-12 13:16 | Azure: test added to signiantdev1.onmicrosoft.com.\n', 'Instruction': 'You have been added to Azure AD. Contact devops@signiant.com for your email and password then sign in on: https://portal.azure.com/'}, {'Plugin name': 'Jira Server', 'Log': 'test elaroche 2018-02-12 13:16 | Jira: test added to jira:prod\n', 'Instruction': 'Follow link to activate your account using your AD username and Password: http://ott-jira.ott.signiant.com:8080/'}]
    mail.emailOutput(email, configMap, pluginInstruction, arg='remove')


if __name__ == "__main__":
    main()






