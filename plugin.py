import imp,os

pluginFolder = "./plugins"
mainFile = "__init__"


def getAllPlugins():
    plugins = []
    possibleplugins = os.listdir(pluginFolder)
    for i in possibleplugins:
        location = os.path.join(pluginFolder, i)
        if not os.path.isdir(location) or not mainFile + ".py" in os.listdir(location):
            continue
        info = imp.find_module(mainFile, [location])
        plugins.append({"name": i, "info": info})
    return plugins

def loadPlugin(pluginName):
    return imp.load_source(pluginName, os.path.join(pluginFolder, pluginName, mainFile + ".py"))

def getApiToken(configMap,plugin_tag): #
    for plugin in configMap['plugins']:
        if plugin['tag'] == plugin_tag:
            return plugin['ApiToken']

def getUrl(configMap,plugin_tag):
    for plugin in configMap['plugins']:
        if plugin['tag'] == plugin_tag:
            return plugin['url']

def getPermissions(configMap, plugin_tag):
    for plugin in configMap['plugins']:
        if plugin['tag'] == plugin_tag:
            return plugin['permission']

def getGroups(configMap,plugin_tag):
    groupsList=[]
    for groups in configMap['plugins']:
        if groups['tag']==plugin_tag:
            for group in groups['permission']:
                groupsList.append(group['group'])
    return groupsList

def inviteMessage(configMap,plugin_tag):
    for plugin in configMap['plugins']:
        if plugin['tag'] == plugin_tag:
            return plugin['message_invite']

def removalMessage(configMap,plugin_tag):
    for plugin in configMap['plugins']:
        if plugin['tag'] == plugin_tag:
            return plugin['message_remove']