#!/usr/bin/python3

def printTextarea(textcontent):
    import sys, codecs
    #sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    print('<textarea id="textcontent" name="textcontent" form="usrform">'+textcontent+'</textarea>')
