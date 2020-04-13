#!/usr/bin/env python3

import cgi, os
from stat import S_IEXEC
import cgitb; cgitb.enable()
import re
import mimetypes
from userlogger import UserLogger
import templates

def showEditor(path, userLogger):

    # make sure file exists
    if not os.path.isfile(path):
        templates.error(path)
    
    # split file from path
    filepath = os.path.dirname(path)
    filename = os.path.basename(path)

    # mime type
    mime = mimetypes.guess_type(path)
    
    # verify content
    if 'image/' in str(mime):
        listImages = [f for f in os.listdir(filepath) if os.path.isfile(os.path.join(filepath, f)) and 'image/' in str(mimetypes.guess_type(f)) ]
        listImages.sort(key=str.lower)
        currentIndex = listImages.index(filename)
        previousImage = None if currentIndex <= 0 else listImages[currentIndex - 1]
        nextImage = None if currentIndex+1 >= len(listImages) else listImages[currentIndex + 1]
        templates.imageViewer(filepath, filename, previousImage, nextImage)
    elif 'application/zip' in str(mime) or 'application/x-zip-compressed' in str(mime):
        templates.unzipper(filepath, filename)
    elif 'application/pdf' in str(mime):
        templates.pdfViewer(filepath, filename)
    
    # open content as text
    try:
        try:
            # default encoding, utf-8
            with open(os.path.join(filepath, filename), 'r', encoding='utf-8') as fhand:
                textcontent = fhand.read()
        except UnicodeDecodeError:
            # others such as windows,..
            with open(os.path.join(filepath, filename), 'r', encoding='iso-8859-1') as fhand:
                textcontent = fhand.read()
    except Exception as e:
        templates.error(type(e).__name__ + ': ' +str(e))
        
    # replace special characters, i.e.: &times; => &amp;times;
    #textcontent = textcontent.replace('&times;', '&amp;times;')
    specialCharacters = re.findall('&+[a-z]+;', textcontent)
    textcontent = textcontent.replace('&amp;', '&amp;amp;')
    for character in specialCharacters:
        if character != '&amp;':
            textcontent = textcontent.replace(character,'&amp;'+character[1:])
    templates.editor(filepath, filename, textcontent)


##################################################
# main

# create instance of field storage
form = cgi.FieldStorage()

# receive command
path = form.getvalue("path")

if "cmd" in form:
    cmd = form.getvalue("cmd")
else:
    cmd = "nocommand"


##################################################
# permission guard
userLogger = UserLogger()
userPermission = userLogger.getPermission(path)

# make sure user is allowed to read
if (userPermission < UserLogger.PERMISSION_READ):
    userLogger.setTargetUrl('pybrowser.py?path='+path)
    userLogger.showLogin('Identification required')
elif userPermission == UserLogger.PERMISSION_READ:
    if cmd == "nocommand":
        showEditor(path, userLogger)
    else:
        userLogger.setTargetUrl('pybrowser.py?path='+path)
        userLogger.showLogin('Identification required')


##################################################
# check commands (all write permission)

# save
if cmd == "save":
    
    # save file (from editor)
    if os.path.isfile(path):
        try:
            contentRaw = form.getvalue("textcontent")
            fhand = open(path, 'wb')
            #contentRaw = contentRaw.decode("iso-8859-1")
            if contentRaw == None:
                contentRaw = ""
            contentRaw = contentRaw.encode('utf-8')
            # in case of DOS/macOS-formatting, change to unix
            contentUnix = contentRaw.replace(b'\r\n', b'\n') # DOS
            contentUnix = contentUnix.replace(b'\r', b'\n') # MAC os
            fhand.write(contentUnix)
            fhand.close()
            #if ".py" in path:
            #        mode = os.stat(path).st_mode
            #        os.chmod(path, mode|S_IEXEC )
        except Exception as e:
            pass
            templates.error(str(e))

# show editor
showEditor(path, userLogger)
