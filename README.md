# backupmanagement
Backup script generator with rsync, rdiff-backup and python 


## HowTo

1. Configure the generator script by copying the backupconfig.template.json file to backupconfog.json and editing the backupconfig.json file.

2. Create the source descriptions in the config file

3. Run python3 generate.py to generate the backupscript (backitup.sh) and add execution permission if needed

4. run the backitup.sh script manually or create a cron job for it


## Prerequisites

- rdiff-backup installed on target machine and installed on remote machine(s)
- the user set in the config file must exist on the remote system(s)
- the user must have permissions to read the given paths
- for automation there must SSH publickey authentication enabled on the remote system and a key available on the target system
- the path to the keyfile must not contain spaces
- the rource path must not be "/" since the source path length must be > 1
- for local backups rsync must be installed

## Best practice

### Remote
- create a separated user on the remote system (useradd -m backuper)
- add public key (ssh-copy-id)
- limit the user to only run rdiff-backup (update ~/.ssh/authorized_keys => add "command=rdiff-backup --server" in front of the line with the public key of backuper)
- add a sudo entry for the user to enable the user to run rdiff-backup as root, without password **restrict it to this command!!! - see above**
($ sudo vi /etc/sudoers.d/rdiff  
backuper  ALL=(root)NOPASSWD:/usr/bin/rdiff-backup)
- create $targetdir/hostname before running script. Or - not recommended - run this skript as sudo in order to create hosts base target directories

### Local
- set the "local" in sourcedescription to 'true'
- be aware, that the the delete FLAG is used. If data in the source path have been deleted, it will get deleted in the target path as well!!!!!
- currently there is no option for exclusions available

## TODO
- log files
