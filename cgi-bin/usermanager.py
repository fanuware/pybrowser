#!/usr/bin/env python3

import cgi, os
from stat import S_IEXEC
import cgitb; cgitb.enable()
import shutil
from userlogger import UserLogger
import templates

##################################################
# main

# create instance of field storage
form = cgi.FieldStorage()

# receive command
if "cmd" in form:
    cmd = form.getvalue("cmd")
else:
    cmd = "nocommand"

##################################################
# permission guard
userLogger = UserLogger()
userPermission = userLogger.getPermission(os.sep)

# make sure user is allowed to read
if (userPermission < UserLogger.PERMISSION_WRITE):
    userLogger.setTargetUrl('../usermanager.html')
    userLogger.showLogin('Identification required')

##################################################
# check commands (all write permission)

# add user
if cmd == "useradd":
    
    # receive command
    try:
        userLogger.userAdd(
            form.getvalue("name"),
            form.getvalue("password"),
            form.getvalue("pathPermission"),
            form.getvalue("accessPermission")
        )
    except:
        templates.error('Invalid arguments to add user')
    templates.usermanager(userLogger.getUserList(), userLogger.getTargetUrl(), cmd + ' successful')
    
# delete user
elif cmd == "userdel":
    
    # receive command
    try:
        userLogger.userDelete(
            form.getvalue("name")
        )
    except:
        templates.error('Invalid argument to delete user')
    templates.usermanager(userLogger.getUserList(), userLogger.getTargetUrl(), cmd + ' successful')

else:
    templates.usermanager(userLogger.getUserList(), userLogger.getTargetUrl())











