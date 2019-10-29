#!/usr/bin/env python3

import cgi, os
from stat import S_IEXEC
import cgitb; cgitb.enable()

import userlogger

def message(title, message):
    print("Content-type:text/html\n")
    print('<!DOCTYPE html><html lang="en">')
    print('<head>')
    print('<title>Message</title>')
    print('<link rel="shortcut icon" href="../static/directory.ico">')
    print('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    print('</head>')
    print('<body>')
    print('<h1>'+title+'</h1>')
    print('<h2 style="color=red;">'+message+'</h2>')
    print('</body>')
    print('</html>')
    exit()


def error(msg):
    message('Error', msg)
    

def redirect(targetUrl):
    if (targetUrl == None):
        targetUrl="pybrowser.py"    
    # html output
    print('Content-type:text/html\n')
    print('<!DOCTYPE html><html lang="en">')
    print('<head>')
    print('<link rel="shortcut icon" href="../static/directory.ico">')
    print('<meta http-equiv="refresh" content="0;url='+targetUrl+'" />')
    print('<title>You are going to be redirected</title>')
    print('</head> ')
    print('<body>')
    print('<h3>Authorization in process</h3>')
    print('</body>')
    print('</html>')
    exit()
    

def login(message, randomHash):
    '''show login page'''
    print("Content-type:text/html\n")
    print('<!DOCTYPE html><html lang="en">')
    print('<head>')
    print('<title>Login</title>')
    print('<link rel="shortcut icon" href="../static/directory.ico">')
    print('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    print('<link rel="stylesheet" href="../static/directory.css">')
    print('</head>')
    print('<body>')
    print('<h3>'+message+'</h3>')
    print('<div id="login_wrapper"><form id="passwordForm" enctype="multipart/form-data" action="authorization.py" method="post" autocomplete="off">')
    print('<input type="hidden" id="password" name="password" value="' + randomHash + '" />')
    print('<label for="password_field">Username:</label>')
    print('<input id="user_field" type="text" name="user" value="" autofocus="true">')
    print('<label for="password_field">Password:</label>')
    print('''<input id="password_field" type="password" style="background: " value ="" name="identification">''')
    print('<button onclick="sendLogin()">Login</button></form></div>')
    print('<script src="../static/sha512.js"></script>')
    #print('<script>function autoreset() { document.getElementById("password_field").value = ""; } autoreset();</script>')
    print('</body>')
    print('</html>')
    exit()


def editor(filepath, filename, textcontent, userLogger):
    permission = userLogger.getPermission(filepath)

    print("Content-type:text/html;charset=utf-8\n")
    print('<!DOCTYPE html><html lang="en">')
    print('<head>')
    print('<title>Directory</title>')
    print('<link rel="shortcut icon" href="../static/directory.ico">')
    print('<link rel="stylesheet" href="../static/directory.css">')
    print('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    print('</head>')
    print('<body>')
    print('''<span id="pathname">''' + os.path.join(filepath, filename) + '''</span>
    <div id="menu">
    <form action="pybrowser.py" method = "post">
    <input name="path" type="hidden" value="''' + filepath + '''">
    <label class="menu_item" id="menu_cancel">
    <input class="menu_selector" type="submit" name="submit">Back</label>
    </form>''')
    from userlogger import UserLogger
    if permission >= userLogger.PERMISSION_WRITE:
        print('''<form action="edit.py" id="usrform" onsubmit="addTextContent()" method = "post">
    <input name="path" type="hidden" value="''' + os.path.join(filepath, filename) + '''">
    <input name="cmd" type="hidden" value="save">
    <label class="menu_item" id="menu_save">
    <input class="menu_selector" type="submit">Save</label>
    </form><IFRAME style="display:none" name="hidden-form"></IFRAME>''')
    if userLogger.isLoggedIn():
        print('<form enctype = "multipart/form-data" action="authorization.py" method = "post">')
        print('<label class="menu_item" id="menu_logout"><input type="hidden" name="cmd" value="logout"><input type="submit" style="display: none;">'+userLogger.isLoggedIn()+'</label></form>')
    else:
        print('<form enctype = "multipart/form-data" action="authorization.py" method = "post">')
        print('<label class="menu_item" id="menu_login"><input type="hidden" name="cmd" value="logout"><input type="submit" style="display: none;">Login</label></form>')
    print('</div>')
    import specialCharacter
    specialCharacter.printTextarea(textcontent)
    print('''    <script>
        // window keyboard listener
        var keys = {};
        window.addEventListener("keydown",
            function(event){
                if (event.ctrlKey || event.metaKey) {
                switch (String.fromCharCode(event.which).toLowerCase()) {
                case 's':
                    event.preventDefault();
                        document.getElementById("usrform").target = "hidden-form"; 
                        document.getElementById("usrform").submit();
                        document.getElementById("usrform").target = "_self";
                        break;
                    }
                }
            }, false);
    </script>''')
    print('<script src="../static/directory.js"></script>')
    print('</body>')
    print('</html>')
    exit()


def pdfViewer(filepath, filename):
    print("Content-type:text/html;charset=utf-8\n")
    print('<!DOCTYPE html><html lang="en">')
    print('<head>')
    print('<title>Directory</title>')
    print('<link rel="shortcut icon" href="../static/directory.ico">')
    print('<link rel="stylesheet" href="../static/directory.css">')
    print('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    print('</head>')
    print('<body>')
    print('''<span id="pathname">''' + os.path.join(filepath, filename) + '''</span>
    <div id="menu">
    <form action="pybrowser.py" method = "post">
    <input name="path" type="hidden" value="''' + filepath + '''">
    <label class="menu_item" id="menu_cancel">
    <input class="menu_selector" type="submit" name="submit">Back</label>
    </form>''')
    print('</div>')
    print('''<object id="pdfView" data="download.py?path=''' + os.path.join(filepath, filename) + '''" type="application/pdf" width="100%" height="100%">
        <p><a href="download.py?path=''' + os.path.join(filepath, filename) + '''">Download</a></p>
        </object>''')
    print('<script src="../static/directory.js"></script>')
    print('</body>')
    print('</html>')
    exit()
    

def imageViewer(filepath, filename, previousImage=None, nextImage=None):
    '''show editor page'''
    print("Content-type:text/html\n")
    print('<!DOCTYPE html><html lang="en">')
    print('<head>')
    print('<title>Directory</title>')
    print('<link rel="shortcut icon" href="../static/directory.ico">')
    print('<link rel="stylesheet" href="../static/directory.css">')
    print('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    print('</head>')
    print('<body>')
    print('''<span id="pathname">''' + os.path.join(filepath, filename) + '''</span>
    <div id="menu">
    <form action="pybrowser.py" method = "post">
    <input name="path" type="hidden" value="''' + filepath + '''">
    <label class="menu_item" id="menu_cancel">
    <input class="menu_selector" type="submit" name="submit">Back</label>
    </form>''')
    if previousImage:
        print('''<form enctype = "multipart/form-data" action="edit.py" method = "post">
        <label class="menu_item" id="menu_previous"><input name="path" type="hidden" value="''' + os.path.join(filepath, str(previousImage)) + '''">
        <input type="submit" style="display: none;">Previous</label></form>''')
    if nextImage:
        print('''<form enctype = "multipart/form-data" action="edit.py" method = "post">
        <label class="menu_item" id="menu_next"><input name="path" type="hidden" value="''' + os.path.join(filepath, str(nextImage)) + '''">
        <input type="submit" style="display: none;">Next</label></form>''')
    print('</div>')
    print('<div id="multimedia"><img src="download.py?path=' + os.path.join(filepath, filename) + '" alt="image preview"></div>')
    print('<script src="../static/directory.js"></script>')
    print('</body>')
    print('</html>')
    exit()


def unzipper(filepath, filename):
    '''show option to unzip'''
    print("Content-type:text/html\n")
    print('<!DOCTYPE html><html lang="en">')
    print('<head>')
    print('<title>Directory</title>')
    print('<link rel="shortcut icon" href="../static/directory.ico">')
    print('<link rel="stylesheet" href="../static/directory.css">')
    print('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    print('</head>')
    print('<body>')
    print('''<span id="pathname">''' + os.path.join(filepath, filename) + '''</span>
    <div id="menu">
    <form action="pybrowser.py" method = "post">
    <input name="path" type="hidden" value="''' + filepath + '''">
    <label class="menu_item" id="menu_cancel">
    <input class="menu_selector" type="submit" name="submit">Back</label>
    </form>''')
    print('</div>')
    print('''<form action="pybrowser.py" method = "post">
            <label>
                <input type="hidden" name="path" value="''' + os.path.join(filepath, filename) + '''">
                <input type="hidden" name="cmd" value="unzip">
                <input type="submit" value='Unzip'></span>
            </label>
        </form>''')
    print('<script src="../static/directory.js"></script>')
    print('</body>')
    print('</html>')
    exit()


def usermanager(userList, targetUrl, message=""):
    print("Content-type:text/html\n")
    print('<!DOCTYPE html><html lang="en">')
    print('<head>')
    print('<title>Directory</title>')
    print('<link rel="shortcut icon" href="../static/directory.ico">')
    print('<link rel="stylesheet" href="../static/directory.css">')
    print('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    print('</head>')
    print('<body>')
    print('''<span id="pathname">''' + targetUrl[targetUrl.find(os.sep):] + '''</span>
    <div id="menu">
    <form action="pybrowser.py" method = "post">
    <input name="path" type="hidden" value="''' + targetUrl[targetUrl.find(os.sep):] + '''">
    <label class="menu_item" id="menu_cancel">
    <input class="menu_selector" type="submit" name="submit">Back</label>
    </form></div>''')
    print('<h3>'+message+'</h3>')
    print('''<form action="usermanager.py" method="post" name="UserAdd">
        <fieldset>
            <legend>Add User</legend>
            <input id="user_add_form" type="text" name="name" placeholder="Name" required autocomplete="off">
            <input id="password_field" type="text" name="password_field" placeholder="Password" required autocomplete="off">
            <input type="text" name="pathPermission" placeholder="/etc/" required autocomplete="off">
            <input type="text" name="accessPermission" placeholder="2" required autocomplete="off">
            <input type="hidden" name="cmd" value="useradd">
            <input type="hidden" id="password" name="password" value="_" />
            <input type="reset" value="Reset">
            <button onclick="sendCreateUser()">Create</button>
        </fieldset>
    </form>
    <form action="usermanager.py" method="post" name="UserDelete">
        <fieldset>
            <legend>Delete User</legend>
            <input type="text" name="name" placeholder="Name" required>
            <input type="hidden" name="cmd" value="userdel">
            <input type="reset" value="Reset">
            <input type="submit" value="Submit">
        </fieldset>
    </form>''')
    print('<table style="width:100%"><tr><th>Name</th><th>Permission</th></tr>')
    for user in userList:
        print('<tr><td>'+user[0]+'</td><td>'+user[1]+'</td></tr>')
    print('</table><script src="../static/sha512.js"></script></body></html>')
    exit()


def directory(filepath, userLogger, currentPage=0):
    permission = userLogger.getPermission(filepath)
    MAX_LIST_LEN = 500
    
    # fix path if necessary
    if not os.path.isdir(filepath):
        templates.error(filepath)
        
    # list all folder and files, sort by name and folder
    listAll = [(os.path.isfile(os.path.join(filepath, f)), f) for f in os.listdir(filepath)]
    listAll.sort(key=lambda row: row[1].lower())
    listAll.sort(key=lambda row: row[0])
    startIndex = currentPage * MAX_LIST_LEN
    if startIndex not in range(0, len(listAll)):
        startIndex = 0
    listCurrent = listAll[startIndex:startIndex + MAX_LIST_LEN]
    listFolder = map(lambda t: t[1],
        filter(lambda t: not t[0], listCurrent))
    listFiles = map(lambda t: t[1],
        filter(lambda t: t[0], listCurrent))
    pageHasPrevious = startIndex > 0
    pageHasNext = len(listAll) > (currentPage + 1) * MAX_LIST_LEN

    # html output
    print("Content-type:text/html\n")
    print('<!DOCTYPE html><html lang="en">')
    print('<head>')
    print('<title>Directory</title>')
    print('<link rel="shortcut icon" href="../static/directory.ico">')
    print('<link rel="stylesheet" href="../static/directory.css">')
    print('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    print('</head>')
    print('<body>')
    print('<span id="pathname">' + filepath + '</span><span id="sep">' + os.sep + '</span>')

    # menu-bar
    print('<div id="menu">')
    if permission >= userLogger.PERMISSION_WRITE:
        print('<button id="insertFolder"><span style="inline" class="menu_item" id="menu_insert" >Insert Folder</span></button>')
        print('<form id="upload_form" enctype = "multipart/form-data" action="pybrowser.py" method = "post">')
        print('<label class="menu_item" id="menu_upload">')
        print('<input class="menu_selector" type="file" name="uploadfiles" multiple>Upload file</label>')
        print('<input type="hidden" name="path" value="' + filepath + '"></form>')
    if pageHasPrevious:
        print('''<form enctype = "multipart/form-data" action="pybrowser.py" method = "post">
        <label class="menu_item" id="menu_previous"><input name="path" type="hidden" value="''' + filepath + '''">
        <input type="hidden" name="page" value="'''+str(currentPage-1)+'''">
        <input type="submit" style="display: none;">Previous</label></form>''')
    if pageHasNext:
        print('''<form enctype = "multipart/form-data" action="pybrowser.py" method = "post">
        <label class="menu_item" id="menu_next"><input name="path" type="hidden" value="''' + filepath + '''">
        <input type="hidden" name="page" value="'''+str(currentPage+1)+'''">
        <input type="submit" style="display: none;">Next</label></form>''')
    if permission >= userLogger.PERMISSION_ADMIN:
        print('''<form enctype = "multipart/form-data" action="usermanager.py" method = "post">
        <label class="menu_item" id="menu_users"><input name="path" type="hidden" value="''' + filepath + '''">
        <input type="submit" style="display: none;">Users</label></form>''')
    if userLogger.isLoggedIn():
        print('<form enctype = "multipart/form-data" action="authorization.py" method = "post">')
        print('<label class="menu_item" id="menu_logout"><input type="hidden" name="cmd" value="logout"><input type="submit" style="display: none;">'+userLogger.isLoggedIn()+'</label></form>')
    else:
        print('<form enctype = "multipart/form-data" action="authorization.py" method = "post">')
        print('<label class="menu_item" id="menu_login"><input type="hidden" name="cmd" value="logout"><input type="submit" style="display: none;">Login</label></form>')
    print('</div>')
    
    # back folder
    prevPath = filepath
    if (len(prevPath) > 1):
        if (prevPath[-3:] == '../'):
            prevPath = '../'+prevPath
        else:
            prevPath = os.path.dirname(prevPath)
    print('''<div class="listitem">
        <form action="pybrowser.py" method = "post">
            <label>
                <input type="hidden" name="path" value="'''+prevPath+'''">
                <input type="submit" style="display: none;"><span class="link foldertree">Back</span>
            </label>
        </form>''')
    copyUrl = userLogger.getCopyUrl()
    if (copyUrl != None) and (os.path.isfile(copyUrl) or os.path.isdir(copyUrl)):
        print('''<form action="pybrowser.py" method = "post">
            <label>
                <input type="hidden" name="path" value="''' + filepath + '''">
                <input type="hidden" name="cmd" value="paste">
                <input type="submit" style="display: none;"><span class="edittool copy"></span>
            </label>
        </form>''')
    print('</div>')

    # list folders
    for name in listFolder:
        print('''<div class="listitem">
        <form action="pybrowser.py" method = "post">
            <label>
                <input type="hidden" name="path" value="''' + os.path.join(filepath, name) + '''">
                <input type="submit" style="display: none;"><span class="link folder">''' + name + '''</span>
            </label>
        </form>
        <form action="download.py" method = "post">
            <label>
                <input type="hidden" name="path" value="''' + os.path.join(filepath, name) + '''">
                <input type="hidden" name="inline" value="0">
                <input type="submit" style="display: none;"><span class="edittool download"></span>
            </label>
        </form>''')
        if permission >= userLogger.PERMISSION_WRITE:
            print('''<form action="pybrowser.py" method = "post">
            <label>
                <input type="hidden" name="path" value="''' + os.path.join(filepath, name) + '''">
                <input type="hidden" name="cmd" value="copy">
                <input type="submit" style="display: none;"><span class="edittool copy"></span>
            </label>
        </form>
        <button class="edittool rename" value="''' + os.path.join(filepath, name) + '''"></button>
        <form action="pybrowser.py" method = "post">
            <label>
                <input type="hidden" name="path" value="''' + os.path.join(filepath, name) + '''">
                <input type="hidden" name="cmd" value="remove">
                <input type="submit" style="display: none;"><span class="edittool remove"></span>
            </label>
        </form>''')
        print('</div>')
    
    # list files
    for name in listFiles:
        print('''<div class="listitem">
        <form action="edit.py" method = "post">
            <label>
                <input type="hidden" name="path" value="''' + os.path.join(filepath, name) + '''">
                <input type="submit" style="display: none;"><span class="link ''' + name[name.rfind('.')+1:].lower() + '''">'''+name+'''</span>
            </label>
        </form>
        <form action="download.py" method = "post">
            <label>
                <input type="hidden" name="path" value="''' + os.path.join(filepath, name) + '''">
                <input type="hidden" name="inline" value="0">
                <input type="submit" style="display: none;"><span class="edittool download"></span>
            </label>
        </form>''')
        if permission >= userLogger.PERMISSION_WRITE:
            print('''<form action="pybrowser.py" method = "post">
            <label>
                <input type="hidden" name="path" value="''' + os.path.join(filepath, name) + '''">
                <input type="hidden" name="cmd" value="copy">
                <input type="submit" style="display: none;"><span class="edittool copy"></span>
            </label>
        </form>
        <button class="edittool rename" value="''' + os.path.join(filepath, name) + '''"></button>
        
        <form action="pybrowser.py" method = "post">
            <label>
                <input type="hidden" name="path" value="''' + os.path.join(filepath, name) + '''">
                <input type="hidden" name="cmd" value="remove">
                <input type="submit" style="display: none;"><span class="edittool remove"></span>
            </label>
        </form>''')
        print('</div>')
    
    # dialog/select_folder
    print('''
    <div id="modalInsertFolder" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <label>Name:</label>
            <input id="foldername" type="text">
            <form id="formInsertFolder" action="pybrowser.py" method = "post">
                <button id="insertFolderSubmit">Ok</button>
                <input id="insertFolderPath" type="hidden" name="path">
                <input type="hidden" name="cmd" value="new">
            </form>
        </div>
    </div>
    <div id="modalRename" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <form id="formRename" action="pybrowser.py" method = "post">
                <label>New name:</label>
                <input id="newname" type="text" name="newname">
                <button id="renameSubmit">Ok</button>
                <input id="renamePath" type="hidden" name="path" value="fromJavascript">
                <input type="hidden" name="cmd" value="rename">
            </form>
        </div>
    </div>''')
    print('<script src="../static/directory.js"></script>')
    print('</body>')
    print('</html>')
    exit()










