#!/usr/bin/env python

# Inspired by 
# https://gitfu.wordpress.com/2008/05/25/git-describe-great-another-way-to-refer-to-commits/
# http://gitready.com/beginner/2009/02/03/tagging.html


defaultRepo = "http://github.com/kgashok/qnaElm" 


#####################
## Get Version details
######################
import subprocess as commands
import re 

def getversion():
    """get the version from git to display as the version number

    Returns:
        string: which contains the version number from the git remote
    """    
    status, repo = commands.getstatusoutput ("git ls-remote --get-url") 
    if status: 
        repo = defaultRepo 
    else:
        repo = re.sub('\.git$', '', repo) 

    status, version = commands.getstatusoutput ("git describe --tags --long")
    if not status: 
        print ("Version: " + version)
    else: 
        print("git describe returned bad status!")
        print("The repo should have at least one release tag!")
        print("Please see https://help.github.com/articles/creating-releases/")
        version = "NA"

    return version
