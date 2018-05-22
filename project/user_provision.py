import argparse
import getpass
import os
import sys
import yaml
import datetime
import logging
import imp

import azure
import msrestazure
import azure.graphrbac
# internal modules
from project import mail
from project import plugin

imp.reload(plugin)

#sdfgsdermn@gmail.com
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


def getJsonResponse(plugin, email, log, instruction, success):
    return {"Plugin name": plugin,
            "Log": (email.split('@', 1)[0] + " " + getpass.getuser() + " " + getDate().strftime("%Y-%m-%d %H:%M") + " | " + log),
            "Instruction": instruction,
            "Success": success}



def main():
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    parser = argparse.ArgumentParser(description='External user provisioning tool')
    parser.add_argument('-n', '--name', help='New user\'s full name', required=True)
    parser.add_argument('-e', '--email', help='New user\'s email', required=True)
    parser.add_argument('-c', '--config', help='Full path to a config file', required=True)
    parser.add_argument('-p', '--plugin', help='The plugin(s) to add users seperated by commas.', required=False)
    parser.add_argument('-r', '--remove', help='The plugin to execute to remove users', required=False)
    parser.add_argument('-l', '--permission',
                        help='Permissions for apps that can accept permissions as parameters. Write as python dict.',
                        required=False)
    args = parser.parse_args()

    logging.basicConfig(filename='log_' + args.email.split('@', 1)[0] + '.log', level=logging.INFO)

    configMap = readConfigFile(args.config)

    availablePlugins = []
    for plugin in configMap['plugins']:
        availablePlugins.append(plugin['plugin'] + ':' + plugin['tag'])

    allPermissions = []
    if args.permission is not None:
        permissions = [x.strip() for x in args.permission.split(';')]
        for permission in permissions:
            allPermissions.append(permission)

    # Get entered plugins / all plugins
    plugins = getArgPlugins(args.plugin, configMap)
    pluginsremove = getArgPlugins(args.remove, configMap)
    emails = [x.strip() for x in args.email.split(',')]

    pluginInstruction = []
    if args.plugin is not None:
        for email in emails:

            if runPlugins(configMap, plugins, email, allPermissions, pluginInstruction, availablePlugins, args.name, arg='add'):

                print('\nsending email')
                mail.emailOutput(email, configMap, pluginInstruction, arg='add')

            else:
                print("Email to a user was not sent. No plugins worked")

    if args.remove is not None:

        for email in emails:

           if runPlugins(configMap, pluginsremove, email, allPermissions, pluginInstruction, availablePlugins, args.name, arg='remove'):

                print('sending email')
                mail.emailOutput(email, configMap, pluginInstruction, arg='remove')

           else:
                print("User was not deleted from any of the accounts")


def runPlugins(configMap, plugins, email, allPermissions, pluginInstruction, availablePlugins, name, arg):
    registered = False
    for config_plugin in configMap['plugins']:
        plugin_tag = config_plugin['plugin'] + ':' + config_plugin['tag']
        pluginName = config_plugin['plugin']
        for requested_plugin in plugins:
            if plugin_tag == requested_plugin:
                if plugin_tag in availablePlugins:
                    plugin_handle = plugin.loadPlugin(pluginName)

                    if arg == 'add':
                        print("\nRunning invite: %s  " % plugin_tag)
                        json = (plugin_handle.inviteUser(email, configMap, allPermissions, plugin_tag, name))

                    if arg == 'remove':
                        print("\nRunning remove: %s  " % plugin_tag)
                        json = (plugin_handle.removeUser(email, configMap, allPermissions, plugin_tag))

                    if json['Success']:

                        pluginInstruction.append(json)
                        logging.info(json['Log'])
                        print(json['Instruction'])
                        registered = True

                    else:
                        print("Could not " + arg + " '" + name + "' using plugin '" + pluginName + "'\n")

    if registered:
        return True
    else:
        return False


def getArgPlugins(pluginsString, configMap):
    plugins = []
    if pluginsString is not None:
        plugins = [x.strip() for x in pluginsString.split(',')]
        if plugins[0] == "all":
            plugins.pop()
            for config_plugin in configMap['plugins']:
                plugins.append(config_plugin['plugin'] + ':' + config_plugin['tag'])
    return plugins


if __name__ == "__main__":
    main()



