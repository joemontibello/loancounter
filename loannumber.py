#!/opt/local/bin/python

#loannumber.py

#import needed modules. re, time and sys are part of python, so you
#get them with an install of the language.
import re
import sys
import time
#requests makes http requesting easier.
import requests
from requests.auth import HTTPBasicAuth
#soup = BeautifulSoup(html_doc)
# Import smtplib for the actual sending function
import smtplib
import simplejson as json

# Import the email modules we'll need
from email.mime.text import MIMEText

#This chunk is instapush-python, copied from github.
def instaPush(appID, secret, activity, trackers):
    url = "http://api.instapush.im/post"
    headers = {"X-INSTAPUSH-APPID": appID, 'X-INSTAPUSH-APPSECRET': secret, 'Content-Type': 'application/json'}
    data = {"event": activity, "trackers": trackers}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response


#credfile is the full path to the file that holds usernames and passwords
#To work, you need a plain text file. It should have 2 values, each on its own
#line, with no blank lines.  They need to be ordered like this:
#  email (user's email address)
#  password (Viva password)
# This is a terrible hack that I want to replace with Oauth2.
#
#I've included credgapi as a placeholder file in git, but the name of the file
#doesn't matter as long as the variable points to it correctly.
credfile = "../keys/credfile"
#getcreds opens the file that holds usernames and passwords.
try:
    creds = open(credfile, 'r')
except IOError:
    print "Failed to open credential store at " + credfile + "\n"
    raise
else:
    #If we opened the credentials properly, we can pull
    #each line into a variable, removing the "return" at the end of each.
    email = creds.readline().rstrip()
    password = creds.readline().rstrip()
    appID = creds.readline().rstrip()
    secret = creds.readline().rstrip()
    creds.close()
    #print email, password
    #next, check that we have something in each variable.
if email == "" or password == "" or appID = "" or secret == "":
    print "Failed to read one or more of the needed credentials from " + credfile + "\n"
    
#url is the page where the latest numbers come from
url = "http://viva.kiva.org"
loginpage = url + "/en/user/login?destination=home"
datapage = url + "/en/home"
#print loginpage

logindata = {'name' : email, 'pass' : password, 'form_id' : 'user_login', 'submit' : 'Log in'}

#auth = HTTPBasicAuth(email, password)
s = requests.session()
s.keep_alive = False
r = s.post(url=loginpage, data=logindata, cookies = s.cookies)

gotpage = s.get(datapage, cookies = s.cookies, verify=True)
prog = re.compile(r".*kiva-statistics-teamleader.*<tr class=\"odd\"><td>English</td><td>([0-9]+)</td>.*Loans to be Reviewed by Partner Limit", re.MULTILINE|re.DOTALL)
result = prog.match(gotpage.text)
myresult = result.group(1)
output = "<html><head><title>" + myresult +"</title></head><body>" + myresult +"<h1></h1></body></html>"
timestamp = time.strftime("%Y%m%d %H:%M (%Z)")

#msg = MIMEText(myresult + "\n" + timestamp)
#server = smtplib.SMTP(host='smtp.gmail.com', port=587)
#me = 'joe@viva.kiva.org'
#you = 'gezo727jiba@post.wordpress.com' 
#subject = "English Queue"
#msg['Subject'] = subject
#msg['From'] = me
#msg['To'] = you
#s = smtplib.SMTP(host='mailhub3.dartmouth.edu')
#s.sendmail(me, [you], msg.as_string())
#s.quit()


print instaPush(appID, secret,
    activity="Kiva_number_check",
    trackers={"number": myresult, "date": timestamp})
