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

def getApiVersion(host):
    """Get the API version for a host. Defaults to 'legacy' for backward compatibility."""
    return host.get("api", "legacy")


def makeValidRemotePath(p):
    return "/"+p.strip("/")+"/"

def makeValidLocalRemotePath(p):
    return p.strip("/")+"/"

# creates quotes if there are special characters
def createCmdlineValidPath(p):
    res=p
    if " " in res:
        res= f'"{res}"'
    return res

# ── Legacy (API 100 / parent-child protocol) ──────────────────────────

def _buildRemoteSchemaLegacy(host, keyfilepath=None):
    """Build a --remote-schema string for the legacy protocol.

    Uses the deprecated ``%s`` placeholder and ``rdiff-backup --server``
    on the remote side.
    """
    schema = "ssh"
    if ("port" in host) and (host["port"] != 22):
        schema += " -p " + str(host["port"])
    if keyfilepath:
        schema += " -i " + createCmdlineValidPath(keyfilepath)
    if host["compress"]:
        schema += " -C"
    # legacy placeholder %s is replaced by the host_info
    schema += " %s sudo rdiff-backup --server"
    return schema


def buildCommandsForHostLegacy(basedir, host, user, targetdir, keyfilepath=None):
    """Generate legacy rdiff-backup commands (parent-child protocol)."""
    hostname = host["name"]
    schema = _buildRemoteSchemaLegacy(host, keyfilepath)
    prefix = "rdiff-backup --remote-schema '" + schema + "' " + user + "@" + hostname + "::"

    dirs = getDirlistOfHost(host)
    res = []
    for f in dirs:
        locpath = createCmdlineValidPath(os.path.join(targetdir, hostname, makeValidLocalRemotePath(f)))
        res.append("mkdir -p " + locpath)
        res.append(prefix + createCmdlineValidPath(makeValidRemotePath(f)) + " " + locpath)
    return res


# ── API 201 (command-based protocol) ──────────────────────────────────

def _buildRemoteSchemaAPI201(host, keyfilepath=None):
    """Build a --remote-schema string for API 201 (command-based protocol).

    Uses the ``{h}`` placeholder and ``rdiff-backup server`` on the
    remote side.
    """
    schema = "ssh"
    if ("port" in host) and (host["port"] != 22):
        schema += " -p " + str(host["port"])
    if keyfilepath:
        schema += " -i " + createCmdlineValidPath(keyfilepath)
    if host["compress"]:
        schema += " -C"
    # {h} is replaced by the host_info; new CLI uses 'rdiff-backup server'
    schema += " {h} sudo rdiff-backup server"
    return schema


def buildCommandsForHostAPI201(basedir, host, user, targetdir, keyfilepath=None):
    """Generate API-201 rdiff-backup commands (command-based protocol)."""
    hostname = host["name"]
    schema = _buildRemoteSchemaAPI201(host, keyfilepath)
    prefix = ("rdiff-backup --api-version 201 --remote-schema '" + schema
              + "' backup " + user + "@" + hostname + "::")

    dirs = getDirlistOfHost(host)
    res = []
    for f in dirs:
        locpath = createCmdlineValidPath(os.path.join(targetdir, hostname, makeValidLocalRemotePath(f)))
        res.append("mkdir -p " + locpath)
        res.append(prefix + createCmdlineValidPath(makeValidRemotePath(f)) + " " + locpath)
    return res


# ── Unified entry point ───────────────────────────────────────────────

def buildCommandsForHost(basedir, host, user, targetdir, keyfilepath=None):
    """Dispatch to the appropriate builder based on the host's ``api`` field."""
    api = getApiVersion(host)
    if api == 201 or str(api) == "201":
        return buildCommandsForHostAPI201(basedir, host, user, targetdir, keyfilepath)
    else:
        # 'legacy', 100, 200, or absent  →  parent-child protocol
        return buildCommandsForHostLegacy(basedir, host, user, targetdir, keyfilepath)

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
        if h.get("local", False):
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
