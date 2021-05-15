#!/bin/python3


import os
import sys
import json

def getSourcesPath(basedir):
    return os.path.join(basedir,"sources")

def getHosts(config):
    return config["sources"]

def getConfig(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def getCurrentDir():
    return os.path.dirname(os.path.abspath(__file__))

def getDirlistOfHost(host):
    return host["dirs"]


def makeValidRemotePath(p):
    return "/"+p.strip("/")+"/"

def makeValidLocalRemotePath(p):
    return p.strip("/")+"/"

# creates quotes if theer are special characters
def createCmdlineValidPath(p):
    res=p
    if " " in res:
        res= f'"{res}"'
    return res

def buildCommandsForHost(basedir,host,user,targetdir, keyfilepath=None):
    hostname=host["name"]
    prefix="rdiff-backup --remote-schema 'ssh "
    if ("port" in host) and (not  host["port"] ==22):
        prefix=prefix+"-p "+str(host["port"])+ " "
    if  keyfilepath:
        prefix=prefix+ "-i "+ createCmdlineValidPath(keyfilepath) + " "
        #!!!! key path is must not contain spaces, since this code will generate invalid commands
    if host['compress']:
        prefix=prefix+"-C"
    prefix=prefix+" %s sudo rdiff-backup --server' "+user+"@"+hostname+"::"

    dirs=getDirlistOfHost(host)
    res=[]
    for f in dirs:
        locpath=createCmdlineValidPath(os.path.join(targetdir,hostname,makeValidLocalRemotePath(f)))
        res.append("mkdir -p "+locpath)
        res.append((prefix+createCmdlineValidPath(makeValidRemotePath(f))+" "+locpath))
    return res

def buildCommandsLocal(basedir,host,targetdir):
    hostname=host["name"]
    prefix="rsync -a --delete "
    dirs=getDirlistOfHost(host)
    res=[]
    for f in dirs:
        locpath=createCmdlineValidPath(os.path.join(targetdir,hostname,makeValidLocalRemotePath(f)))
        res.append("mkdir -p "+locpath)
        res.append((prefix+createCmdlineValidPath(makeValidRemotePath(f))+" "+locpath))
    return res



def generateScript(config):
    lines=[]
    user=config["user"]
    targetdirectory=config["targetfolder"]
    keyfile=config["keyfile"]
    basedir = getCurrentDir()
    lines.append("#!/bin/bash")
    for h in getHosts(config):
        if h["local"]:
            for c in buildCommandsLocal(basedir,h,targetdirectory):
                lines.append(c)
        else:
            for c in buildCommandsForHost(basedir,h,user,targetdirectory,keyfile):
                lines.append(c)
    return lines

def writeFile(lines,outfile):
    with open(outfile,'w') as file:
        for l in lines:
            file.write(l+'\n')


config=getConfig(os.path.join(getCurrentDir(),"backupconfig.json"))

writeFile(generateScript(config),os.path.join(getCurrentDir(),"backitup.sh"))
