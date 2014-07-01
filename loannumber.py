#!/opt/local/bin/python

# loannumber.py

# import needed modules. re, time and sys are part of python, so you
# get them with an install of the language.
import re
import time
#requests makes http requesting easier.
import requests
import os
# Import smtplib for the actual sending function
import smtplib
import simplejson as json
# Import the email modules we'll need
from email.mime.text import MIMEText
#import pdb
import sys
#This chunk is instapush-python, copied from github.


def instapush(localappid, localsecret, activity, trackers):
    """

    :rtype : object
    """
    pushurl = "http://api.instapush.im/post"
    headers = {"X-INSTAPUSH-APPID": localappid, 'X-INSTAPUSH-APPSECRET': localsecret,
               'Content-Type': 'application/json'}
    data = {"event": activity, "trackers": trackers}
    msgdata = json.dumps(data)
    response = requests.post(pushurl, msgdata, headers=headers)
    if response.text == "<Response [200]>":
        sys.exit()
    return response



if os.isatty(sys.stdin.fileno()):
    # Debug mode.
    wd = os.getcwd
    credfile = "../keys/credfile".format(wd)
else:
    # Cron mode.
    wd = getcwd()
    credfile = "{0}/keys/credfile".format(wd)
#credfile is the full path to the file that holds usernames and passwords
#To work, you need a plain text file. It should have 2 values, each on its own
#line, with no blank lines.  They need to be ordered like this:
#  email (user's email address)
#  password (Viva password)
# This is a terrible hack that I want to replace with Oauth2.
#
try:
    creds = open(credfile, 'r')
except IOError:
    print "Failed to open credential store at " + credfile + "\n"
    raise
except:
    print "Unexpected error:", sys.exc_info()[0]
    raise
else:
    #If we opened the credentials properly, we can pull
    #each line into a variable, removing the "return" at the end of each.
    email = creds.readline().rstrip()
    password = creds.readline().rstrip()
    appid = creds.readline().rstrip()
    secret = creds.readline().rstrip()
    you = creds.readline().rstrip()
    creds.close()
    #print email, password
    #next, check that we have something in each variable.
if email == "" or password == "" or appid == "" or secret == "":
    print "Failed to read one or more of the needed credentials from " + credfile + "\n"

#url is the page where the latest numbers come from
url = "http://viva.kiva.org"
loginpage = url + "/en/user/login?destination=home"
datapage = url + "/en/home"
#print loginpage

logindata = {'name': email, 'pass': password, 'form_id': 'user_login', 'submit': 'Log in'}

#auth = HTTPBasicAuth(email, password)
s = requests.session()
s.keep_alive = False
r = s.post(url=loginpage, data=logindata, cookies=s.cookies)

gotpage = s.get(datapage, cookies=s.cookies, verify=True)
#pdb.set_trace()
prog = re.compile(r".*statistics-teamleader.*<tr class=\"odd\"><td>English</td><td>([0-9]+)</td>.*Loans to be Reviewed",
                  re.MULTILINE | re.DOTALL)
try:
    result = prog.match(gotpage.text)
except:
    print "Regex failed"
    raise
else:
    myresult = result.group(1)
    output = "<html><head><title>" + myresult + "</title></head><body>" + myresult + "<h1></h1></body></html>"
    timestamp = time.strftime("%Y%m%d %H:%M (%Z)")
    msg = MIMEText(myresult + "\n" + timestamp)
    server = smtplib.SMTP(host='smtp.gmail.com', port=587)
    subject = "English Queue"
    msg['Subject'] = subject
    msg['From'] = email
    msg['To'] = you
    s = smtplib.SMTP(host='mailhub3.dartmouth.edu')
    s.sendmail(email, [you], msg.as_string())
    s.quit()

pushsuccess = instapush(appid, secret,
                        activity="Kiva_number_check",
                        trackers={"number": myresult, "date": timestamp})

