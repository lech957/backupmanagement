#!/bin/python3


import os
import sys
import json

def getSourcesPath(basedir):
    return os.path.join(basedir,"sources")

def getHosts(basedir):
    sourcedir=getSourcesPath(basedir)
    return [f for f in os.listdir(sourcedir) if os.path.isfile(os.path.join(sourcedir, f))]

def getConfig(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def getCurrentDir():
    return os.path.dirname(os.path.abspath(__file__))

def getDirlistOfHost(basedir,hostname):
    filename=os.path.join(getSourcesPath(basedir),hostname)
    with open(filename) as f:
        return [x.strip() for x in f.readlines()]


def makeValidRemotePath(p):
    return "/"+p.strip("/")+"/"

def makeValidLocalRemotePath(p):
    return p.strip("/")+"/"

def buildCommandsForHost(basedir,hostname,user,targetdir,keyfilepath=None):
    if not keyfilepath:
        prefix="rdiff-backup --remote-schema 'ssh -C %s sudo rdiff-backup --server' "+user+"@"+hostname+"::"
    else:
        prefix="rdiff-backup --remote-schema 'ssh -i "+keyfilepath  " -C %s sudo rdiff-backup --server' "+user+"@"+hostname+"::"
        #!!!! key path is must not contain spaces, since this code will generate invalid commands
    dirs=getDirlistOfHost(basedir,hostname)
    target = os.path.join(targetdir,hostname)
    return [(prefix+makeValidRemotePath(f)+" "+os.path.join(targetdir,hostname,makeValidLocalRemotePath(f))) for f in dirs]



config=getConfig(os.path.join(getCurrentDir(),"backupconfig.json"))

user=config["user"]
targetdirectory=config["target"]
basedir = getCurrentDir()
print(getHosts(basedir))

print(os.path.join("abc/def","test","path"))

#for h in getHosts(basedir):
#    print("#### "+h)
#    for d in getDirlistOfHost(basedir,h):
#        print(d)
for h in getHosts(basedir):
    for c in buildCommandsForHost(basedir,h,user,targetd):
        print(c)
