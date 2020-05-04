#!/usr/bin/env python3

import cgi
import cgitb
import os
import sys
import zipfile
import mimetypes
import templates
from userlogger import UserLogger
cgitb.enable()


def getRecbin():
    if not os.path.isdir('recbin') and not os.path.isdir('../recbin'):
        os.mkdir('recbin')
    return os.path.abspath('recbin' if os.path.isdir('recbin') else '../recbin')

def getUnusedName(file):
    if not os.path.exists(file):
        return file
    basepath, basename = os.path.split(file)
    p = basename.rfind('.')
    extension = basename[p:] if p > 0 else ""
    name = basename[:len(basename)-len(extension)]
    counter = 0
    outFile = file
    while os.path.exists(outFile):
        counter += 1
        outFile = os.path.join(basepath, name + str(counter) + extension)
    return outFile


##################################################
# main

# create instance of field storage
form = cgi.FieldStorage()
userLogger = UserLogger()

# receive filepath
try:
    file = form.getvalue("path")
except:
    pass

# allows browser to display known content inline
isInline = True
try:
    w = form.getvalue("inline").lower()
    #isInline = w != "0" and w != "false"
    isInline = False
except:
    pass


##################################################
# permission guard
userPermission = userLogger.getPermission(os.path.dirname(file))

# make sure user is allowed to read
if (userPermission < UserLogger.PERMISSION_READ):
    if "redirect" not in form:
        args = '&'.join([key + '=' + str(form[key].value) for key in form.keys()])
        if args:
            url = os.path.basename(os.environ['SCRIPT_NAME']) + '?redirect=True&' + args
        else:
            url = os.path.basename(os.environ['SCRIPT_NAME']) + '?redirect=True'
        templates.redirect(url)
    else:
        userLogger.showLogin('Identification required')


##################################################
# create download
def createDownload(fullname, **kwargs):
    mime_type = mimetypes.guess_type(fullname)[0]
    name = os.path.basename(fullname) if 'name' not in kwargs else kwargs['name']
    print ("Content-Type: " + mime_type)
    if 'inline' not in kwargs or kwargs['inline'] is False:
        print ("Content-Disposition: attachment; filename=" + name)
    print ("")
    sys.stdout.flush()
    sys.stdout.buffer.write(open(fullname, "rb").read())

if os.path.isfile(file):
    createDownload(file, inline=(isInline))
elif os.path.isdir(file):
    def zipdir(path, ziph, ignore):
        for root, dirs, files in os.walk(path):
            if ignore in root:
                continue
            for file in files:
                try:
                    absPath = os.path.join(root, file)
                    ziph.write(
                        absPath,
                        os.path.relpath(absPath, os.path.dirname(path)))
                except PermissionError as e:
                    pass
    recbin = getRecbin()
    tmpZipName = getUnusedName(os.path.join(recbin, 'tmpZip.zip'))
    zipf = zipfile.ZipFile(tmpZipName, 'w', zipfile.ZIP_DEFLATED)
    zipdir(file, zipf, recbin)
    zipf.close()
    createDownload(tmpZipName, name=(os.path.basename(file) + '.zip'))
    os.remove(tmpZipName)
else:
    templates.error(file)
