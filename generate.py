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

def buildCommandsForHost(basedir,host,user,targetdir, keyfilepath=None):
    hostname=host["name"]
    prefix="rdiff-backup --remote-schema 'ssh "
    if ("port" in host) and (not  host["port"] ==22):
        prefix=prefix+"-p "+str(host["port"])+ " "
    if  keyfilepath:
        prefix=prefix+ "-i "+keyfilepath + " "
        #!!!! key path is must not contain spaces, since this code will generate invalid commands
    prefix=prefix+"-C %s sudo rdiff-backup --server' "+user+"@"+hostname+"::"

    dirs=getDirlistOfHost(host)
    res=[]
    for f in dirs:
        locpath=os.path.join(targetdir,hostname,makeValidLocalRemotePath(f))
        res.append("mkdir -p "+locpath)
        res.append((prefix+makeValidRemotePath(f)+" "+locpath))
    return res



def generateScript(config):
    lines=[]
    user=config["user"]
    targetdirectory=config["targetfolder"]
    keyfile=config["keyfile"]
    basedir = getCurrentDir()
    lines.append("#!/bin/bash")
    for h in getHosts(config):
        for c in buildCommandsForHost(basedir,h,user,targetdirectory,keyfile):
            lines.append(c)
    return lines

def writeFile(lines,outfile):
    with open(outfile,'w') as file:
        for l in lines:
            file.write(l+'\n')


config=getConfig(os.path.join(getCurrentDir(),"backupconfig.json"))

writeFile(generateScript(config),os.path.join(getCurrentDir(),"backitup.sh"))
