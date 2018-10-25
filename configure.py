#!/usr/bin/python3
from notebook.auth import passwd 
import os

pwhash = "sha1:90b58bbedb1d:afd960baa6013c9cb51a4b28a12affb3e22f1c24"
jupyter_config = os.path.expanduser('~/.jupyter/jupyter_notebook_config.py')

jupyter_comment_start = "# Start of lines added by jupyter-password.py"
jupyter_comment_end = "# End lines added by jupyter-passwordd.py"
jupyter_passwd_line = "c.NotebookApp.password = u'%s'" % (pwhash) 
jupyter_no_browser = "c.NotebookApp.open_browser = False"

with open(jupyter_config, 'a') as file:
    file.write('\n')
    file.write(jupyter_comment_start + '\n')
    file.write(jupyter_passwd_line + '\n')
    file.write(jupyter_no_browser + '\n')
    file.write(jupyter_comment_end + '\n')