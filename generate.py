#!/bin/python3


import os
import sys
import json

def getSourcesPath(basedir):
    return os.path.join(basedir,"sources")

def getHosts(basedir):
    sourcedir=getSourcesPath(basedir)
    return [f for f in os.listdir(sourcedir) if (os.path.isfile(os.path.join(sourcedir, f)) and (not f == "example.com"))]

def getConfig(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def getCurrentDir():
    return os.path.dirname(os.path.abspath(__file__))

def getDirlistOfHost(basedir,hostname):
    filename=os.path.join(getSourcesPath(basedir),hostname)
    with open(filename) as f:
        return [x.strip() for x in f.readlines() if len(x) > 1]


def makeValidRemotePath(p):
    return "/"+p.strip("/")+"/"

def makeValidLocalRemotePath(p):
    return p.strip("/")+"/"

def buildCommandsForHost(basedir,hostname,user,targetdir,keyfilepath=None):
    if not keyfilepath:
        prefix="rdiff-backup --remote-schema 'ssh -C %s sudo rdiff-backup --server' "+user+"@"+hostname+"::"
    else:
        prefix="rdiff-backup --remote-schema 'ssh -i "+keyfilepath + " -C %s sudo rdiff-backup --server' "+user+"@"+hostname+"::"
        #!!!! key path is must not contain spaces, since this code will generate invalid commands
    dirs=getDirlistOfHost(basedir,hostname)
    target = os.path.join(targetdir,hostname)
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
    for h in getHosts(basedir):
        for c in buildCommandsForHost(basedir,h,user,targetdirectory,keyfile):
            lines.append(c)
    return lines

def writeFile(lines,outfile):
    with open(outfile,'w') as file:
        for l in lines:
            file.write(l+'\n')


config=getConfig(os.path.join(getCurrentDir(),"backupconfig.json"))

writeFile(generateScript(config),os.path.join(getCurrentDir(),"backitup.sh"))
