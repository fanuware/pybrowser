#!/usr/bin/env python3

import cgi
import cgitb
import os
import templates
from userlogger import UserLogger
cgitb.enable()

# create instance of field storage
form = cgi.FieldStorage()
userLogger = UserLogger()

def cgiFieldStorageToDict(values):
    params = {}
    for key in values:
        if key != 'url':
            params[ key ] = values.getvalue(key)
    return params

# receive user identification
if ("cmd" in form) and (form.getvalue("cmd") == "logout"):
    userLogger.logout()
    userLogger.showLogin('User is logged out')
if "user" in form and "password" in form:
    userLogger.login(form.getvalue("user"), form.getvalue("password"))
    templates.redirect(userLogger.getTargetUrl())

# validate login authorization
else:
    templates.message('Authorization: ', str(cgiFieldStorageToDict(form)))
    userLogger.showLogin('Error')
