#!/usr/bin/env python3

import cgi, os

import shutil
from userlogger import UserLogger
import templates
import mimetypes
from stat import S_IEXEC


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

def getRecbin():
    if not os.path.isdir("recbin") and not os.path.isdir("../recbin"):
        os.mkdir("recbin")
    return "recbin" if os.path.isdir("recbin") else "../recbin"


##################################################
# main

# create instance of field storage
form = cgi.FieldStorage()

if "path" in form:
    filepath = form.getvalue("path")
    filepath = filepath.rstrip(os.sep)
else:
    filepath = os.sep

if "cmd" in form:
    cmd = form.getvalue("cmd")
else:
    cmd = "nocommand"

# receive file for upload
try:
    uploadfiles = form["uploadfiles"]
    cmd = "uploadfiles"
except:
    pass

# receive page (optional)
currentPage = 0 if "page" not in form else int(form.getvalue("page"))


##################################################
# permission guard
userLogger = UserLogger()
userPermission = userLogger.getPermission(filepath)
userLogger.setTargetUrl('pybrowser.py?path='+filepath)

# make sure user is allowed to read
if (userPermission < UserLogger.PERMISSION_READ):
    userLogger.showLogin('Identification required')
elif userPermission == UserLogger.PERMISSION_READ:
    if (cmd == "nocommand"):
        templates.directory(filepath, userLogger, currentPage)
    else:
        userLogger.showLogin('Identification required')


##################################################
# check commands (all read permission)

# upload file
if cmd == "uploadfiles":
    
    # upload file to server
    try:
        # if single file received, make file list-accessable
        if uploadfiles.filename:
            uploadfiles = list([uploadfiles])
    except:
        pass
    try:
        for file in uploadfiles:
            FILEPATH = os.path.join(filepath, file.filename)
            
            # create file
            with open(FILEPATH , 'wb') as fhand:
                contentRaw = file.file.read()
                fhand.write(contentRaw)
                fhand.close()
            
            # convert text file to unix format
            mime = mimetypes.guess_type(FILEPATH)
            if 'text' in str(mime):
                with open(FILEPATH , 'wb') as fhand:
                    contentRaw = contentRaw.replace(b'\r\n', b'\n') # DOS
                    contentRaw = contentRaw.replace(b'\r', b'\n') # MAC os
                    fhand.write(contentRaw)
                    fhand.close()
                
            # make file executable
            if ".py" in FILEPATH:
                mode = os.stat(FILEPATH).st_mode
                os.chmod(FILEPATH, mode|S_IEXEC )
    except Exception as e:
        templates.message("UploadError", str(e))

# new
elif cmd == "new":
    
    # new folder
    if not os.path.exists(filepath):
        os.mkdir(filepath)
        filepath = os.path.dirname(filepath)
    
    # save file (from editor)
    elif os.path.isfile(filepath):
        try:
            contentRaw = form.getvalue("textcontent")
            fhand = open(filepath, 'wb')
            contentRaw = contentRaw.encode('utf-8')
            # in case of DOS/macOS-formatting, change to unix
            #contentUnix = contentRaw.replace('\r\n', '\n') # DOS
            #contentUnix = contentUnix.replace('\r', '\n') # MAC os
            contentUnix = contentRaw.replace(b'\r\n', b'\n') # DOS
            contentUnix = contentUnix.replace(b'\r', b'\n') # MAC os
            fhand.write(contentUnix)
            fhand.close()
            if ".py" in filepath:
                    mode = os.stat(filepath).st_mode
                    os.chmod(filepath, mode|S_IEXEC )
        except Exception as e:
            templates.error(str(e))
    
# remove folder/file
elif cmd == "remove":
    recbin = getRecbin()
    userRecbin = os.path.join(recbin, userLogger.isLoggedIn())
    if not os.path.isdir(userRecbin):
        os.mkdir(userRecbin)
    if os.path.isdir(filepath) or os.path.isfile(filepath):
        try:
            destination = getUnusedName(os.path.join(userRecbin, os.path.basename(filepath)))
            os.rename(filepath, destination)
        except:
            pass

# rename
elif cmd == "rename":
    try:
        newname = form.getvalue("newname")
        if os.path.exists(filepath):
            os.rename(filepath, os.path.join(os.path.dirname(filepath), newname))
    except:
        pass

# copy
elif cmd == "copy":
    if os.path.isfile(filepath) or os.path.isdir(filepath):
        userLogger.setCopyUrl(filepath)
    if os.path.isdir(filepath):
        filepath = os.path.split(filepath)[0]

# paste
elif cmd == "paste":
    sourceFile = userLogger.getCopyUrl()
    userLogger.resetCopyUrl()
    destFileName = getUnusedName(os.path.join(filepath, os.path.basename(sourceFile)))
    if os.path.isfile(sourceFile):
        shutil.copy(sourceFile, destFileName)
    elif os.path.isdir(sourceFile):
        shutil.copytree(sourceFile, destFileName)
    else:
        templates.error("No copy file found")

# unzip
elif cmd == "unzip":
    import zipfile

    dirpath = os.path.dirname(filepath)
    newFolder = getUnusedName(os.path.join(dirpath, os.path.basename(filepath).replace('.zip', '')))
    os.mkdir(newFolder)
    try:
        zipf = zipfile.ZipFile(filepath, 'r')
        zipf.extractall(newFolder)
        zipf.close()
    except Exception as e:
        templates.message("Unzip", str(e))
    filepath = dirpath 
    #templates.message("Unzip", filepath)

# validate filepath
if not os.path.isdir(filepath):
    filepath = os.path.dirname(filepath)
    if not os.path.isdir(filepath):
        filepath = os.sep

# show directory
if (userLogger.getPermission(filepath) >= userLogger.PERMISSION_READ):
    templates.directory(filepath, userLogger, currentPage)
else:
    userLogger.showLogin('Identification required')




















