import argparse
import getpass
import os
import sys
import yaml
import plugin
import datetime
import mail

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
        #log.write('------------------------------\n')
    else:
        print('creating file')
        log = open("log.txt", "w+")

    #Command Line
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    parser = argparse.ArgumentParser(description='External user provisioning tool')
    parser.add_argument('-e','--email', help='New user email',required=True)
    parser.add_argument('-c','--config', help='Full path to a config file',required=True)
    parser.add_argument('-p','--plugin', help='The plugin(s) to add users seperated by commas.',required=False)
    parser.add_argument('-r','--remove', help='the plugin to execute to remove users',required=False)
    parser.add_argument('-g','--group', help='groups for apps that can accept groups as parameters',required=False)
    parser.add_argument('-l','--permission', help='permission for apps that can accept permissions as parameters. write as python dict',required=False)
    args = parser.parse_args()

    # load Config file
    configMap = readConfigFile(args.config)

    #groups
    #-g aws-dev1:IAMChangeMyPW_ManageMyKeys,SigniantDevelopers;aws-dev2:IAMChangeMyPW_ManageMyKeys
    #split at ";" then remove "plugin:" then split again, then array of array
    groups=[]
    if args.group is not None:
        groups=[x.strip() for x in args.group.split(';')]
#{'plugin':'papertrail-dev','user[email]':'test@signiant.com','user[read_only]':1,'user[manage_members]':0,'user[manage_billing]':0,'user[purge_logs]':0};{'plugin':'papertrail-prod','user[email]':'test@signiant.com','user[read_only]':1,'user[manage_members]':0,'user[manage_billing]':0,'user[purge_logs]':0}
    #dict of perm (name,dict of perm)

    allPermissions=[]
    if args.permission is not None:
        permissions= [x.strip() for x in args.permission.split(';')]
        for permission in permissions:
            allPermissions.append(permission)

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

    email=args.email
    print("for user:"+email)

    #run required plugins
    validPlugins=[]
    for config_plugin in configMap['plugins']:#get plugin from config file
        plugin_name = config_plugin['name']
        for requested_plugin in plugins: #get the args plugin that you want to run
            if plugin_name==requested_plugin: # check if args is valid
                if plugin_name in ('papertrail-dev','papertrail-prod' ,'bitbucket' , 'slack', 'artifactory', 'aws-dev1' , 'aws-dev2','azure') :
                    plugin_handle = plugin.loadPlugin(plugin_name)
                    print("Running: %s  " % plugin_name)
                    json = (plugin_handle.inviteUser(email, configMap,allPermissions,groups))
                    validPlugins.append(json)
                    log.write(json['Log'])

    for config_plugin in configMap['plugins']:  # get plugin from config file
        plugin_name = config_plugin['name']
        for requested_plugin in pluginsremove:  # get the args plugin that you want to run
            if plugin_name == requested_plugin:  # check if args is valid
                if plugin_name in ('papertrail-dev','papertrail-prod' ,'bitbucket' , 'slack', 'artifactory', 'aws-dev1' , 'aws-dev2','azure') :
                    print("Ran delete: %s  " % plugin_name)
                    plugin_handle = plugin.loadPlugin(plugin_name)  # listUsers
                    json = (plugin_handle.removeUser(email, configMap))
                    validPlugins.append(json)
                    log.write(json['Log'])

    # print('sending email')
    # mail.emailOutput(email, configMap,validPlugins)
    log.close()


if __name__ == "__main__":
    main()






