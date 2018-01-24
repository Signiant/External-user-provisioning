import argparse
import getpass
import os
import sys
import yaml
import mail
import plugin
import datetime

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
    plugin_results = dict()
    if os.path.isfile('log.txt'):
        log= open('log.txt','a')
        log.write('------------------------------\n')
    else:
        print('creating file')
        log = open("log.txt", "w+")

    #Command Line
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    parser = argparse.ArgumentParser(description='External user provisioning tool')
    parser.add_argument('-c','--config', help='Full path to a config file',required=True)
    parser.add_argument('-p','--plugin', help='the plugin to execute to add users',required=False)
    parser.add_argument('-r','--remove', help='the plugin to execute to remove users',required=False)
    args = parser.parse_args()

    # load Config file
    configMap = readConfigFile(args.config)

    #list of apps to add user to
    plugins=['']
    if args.plugin is not None:
        plugins=[x.strip() for x in args.plugin.split(',')]
        if plugins[0] == "all":
            plugins.pop()
            for config_plugin in configMap['plugins']:
                plugins.append(config_plugin['name'])

    #list of apps to remove user from
    pluginsremove=['']
    if args.remove is not None:
        pluginsremove=[x.strip() for x in args.remove.split(',')]
        if pluginsremove[0] == "all":
            pluginsremove.pop()
            for config_plugin in configMap['plugins']:
                pluginsremove.append(config_plugin['name'])

    email=configMap['global']['newUser']
    print(plugins)
    print("for user:"+email)

    #run required plugins
    validPlugins=[]
    for config_plugin in configMap['plugins']:#get plugin from config file
        plugin_name = config_plugin['name']
        for requested_plugin in plugins: #get the args plugin that you want to run
            if plugin_name==requested_plugin: # check if args is valid
                if plugin_name=='papertrail': ###MAKE ALL METHOD NAMES THE SAME, and repeat that method with args for each
                    runPluginInvite(plugin_name, email, configMap, validPlugins, log)
                elif plugin_name=='bitbucket':#removing from all groups
                    runPluginInvite(plugin_name, email, configMap, validPlugins, log)
                elif plugin_name == 'slack': #returns link only
                    runPluginInvite(plugin_name, email, configMap, validPlugins, log)
                elif plugin_name == 'artifactory': #returns link only
                    runPluginInvite(plugin_name, email, configMap, validPlugins, log)
                elif plugin_name == 'aws':  # returns link only
                    runPluginInvite(plugin_name, email, configMap, validPlugins, log)
                print("Ran invite: %s  " % plugin_name)

    for config_plugin in configMap['plugins']:  # get plugin from config file
        plugin_name = config_plugin['name']
        for requested_plugin in pluginsremove:  # get the args plugin that you want to run
            if plugin_name == requested_plugin:  # check if args is valid
                if plugin_name == 'papertrail':  ###MAKE ALL METHOD NAMES THE SAME, and repeat that method with args for each
                    runPluginRemove(plugin_name, email, configMap, validPlugins, log)
                elif plugin_name == 'bitbucket':  # removing from all groups
                    runPluginRemove(plugin_name, email, configMap, validPlugins, log)
                elif plugin_name == 'slack':  # returns link only
                    runPluginRemove(plugin_name, email, configMap, validPlugins, log)
                elif plugin_name == 'artifactory':  # returns link only
                    runPluginRemove(plugin_name, email, configMap, validPlugins, log)
                elif plugin_name == 'aws':  # returns link only
                    runPluginRemove(plugin_name, email, configMap, validPlugins, log)
                print("Ran delete: %s  " % plugin_name)

   # mail.emailOutput(email, configMap,validPlugins)
    log.close()

def runPluginInvite(plugin_name,email, configMap,validPlugins,log):
    plugin_handle = plugin.loadPlugin(plugin_name)  # listUsers
    json = (plugin_handle.inviteUser(email, configMap))
    validPlugins.append(json)
    log.write(json['Log'])

def runPluginRemove(plugin_name,email, configMap,validPlugins,log):
    plugin_handle = plugin.loadPlugin(plugin_name)  # listUsers
    json = (plugin_handle.removeUser(email, configMap))
    validPlugins.append(json)
    log.write(json['Log'])


if __name__ == "__main__":
    main()




