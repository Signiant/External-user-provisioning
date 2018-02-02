import argparse
import getpass
import os
import sys
import yaml
import mail
import plugin
import datetime
import logging
from azure.common.credentials import UserPassCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.graphrbac.models import UserCreateParameters, PasswordProfile


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
    #help('modules azure.common')

    print (sys.path)


    logging.basicConfig(filename='example.log', level=logging.INFO)

    #Command Line
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    parser = argparse.ArgumentParser(description='External user provisioning tool')
    parser.add_argument('-e','--email', help='New user email',required=True)
    parser.add_argument('-c','--config', help='Full path to a config file',required=True)
    parser.add_argument('-p','--plugin', help='The plugin(s) to add users seperated by commas.',required=False)
    parser.add_argument('-r','--remove', help='the plugin to execute to remove users',required=False)
    parser.add_argument('-l','--permission', help='permission for apps that can accept permissions as parameters. write as python dict',required=False)
    args = parser.parse_args()

    # load Config file
    configMap = readConfigFile(args.config)
    availablePlugins=[]
    for plugin in configMap['plugins']:
        availablePlugins.append(plugin['plugin']+':'+plugin['tag'])

    #{'plugin':'aws', 'group1': 'IAMChangeMyPW_ManageMyKeys', 'group2': 'SigniantDevelopers'};{'plugin':'papertrail-dev','user[email]':'test@signiant.com','user[read_only]':1,'user[manage_members]':0,'user[manage_billing]':0,'user[purge_logs]':0};{'plugin':'papertrail-prod','user[email]':'test@signiant.com','user[read_only]':1,'user[manage_members]':0,'user[manage_billing]':0,'user[purge_logs]':0}
    allPermissions=[]
    if args.permission is not None:
        permissions= [x.strip() for x in args.permission.split(';')]
        for permission in permissions:
            allPermissions.append(permission)

    #Get entered plugins / all plugins
    plugins=getArgPlugins(args.plugin, configMap)
    pluginsremove=getArgPlugins(args.remove,configMap)
    email=args.email
    print("for user:"+email)

    pluginInstruction = []
    if args.plugin is not None:
        arg='add'
        runPlugins(configMap, plugins,email,allPermissions, pluginInstruction,availablePlugins,arg)
       # print('sending email')
        #mail.emailOutput(email, configMap,pluginInstruction)
    if args.remove is not None:
        arg='remove'
        runPlugins(configMap, pluginsremove, email, allPermissions,  pluginInstruction,availablePlugins,arg)
       # print('sending email')
        email= configMap['global']['smtp']['server']
        #mail.emailOutput(email, configMap,pluginInstruction)



def runPlugins(configMap,plugins,email,allPermissions,pluginInstruction,availablePlugins,arg):

    for config_plugin in configMap['plugins']:  # get plugin from config file
        plugin_tag = config_plugin['plugin']+':'+config_plugin['tag']
        pluginName = config_plugin['plugin']
        for requested_plugin in plugins:  # get the args plugin that you want to run
            if plugin_tag == requested_plugin:  # check if args is valid
                if plugin_tag in availablePlugins:  # get plugin map names
                    plugin_handle = plugin.loadPlugin(pluginName)
                    if arg=='add':
                        print("Running invite: %s  " % plugin_tag)
                        json = (plugin_handle.inviteUser(email, configMap, allPermissions, plugin_tag))
                    if arg == 'remove':
                        print("Running remove: %s  " % plugin_tag)
                        json = (plugin_handle.removeUser(email, configMap, allPermissions, plugin_tag))
                    pluginInstruction.append(json)

                    logging.info(json['Log'])

#split args plugins
def getArgPlugins(pluginsString,configMap):
    plugins=[]
    if pluginsString is not None:
        plugins = [x.strip() for x in pluginsString.split(',')]
        if plugins[0] == "all":
            plugins.pop()
            for config_plugin in configMap['plugins']:
                plugins.append(config_plugin['plugin']+':'+config_plugin['tag'])
    return plugins

if __name__ == "__main__":
    main()






