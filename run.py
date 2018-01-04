from BeautifulSoup import BeautifulSoup
import requests
import urlparse
import urllib2


#URL='http://boddenfishing.de/vh/'   #uncomment for single URL scan and call pwn(URL)
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


art="""\
                    ^`.                     o
     ^_              \  \                  o  o
     \ \             {   \                 o
     {  \           /     `~~~--__
     {   \___----~~'              `~~-_     ______          _____
      \                         /// a  `~._(_||___)________/___
      / /~~~~-, ,__.    ,      ///  __,,,,)      o  ______/    \_
      \/      \/    `~~~;   ,---~~-_`~= \ \------o-'
                       /   /            / /
                      '._.'           _/_/
                                      ';|\

                 PHISHERS, BEWARE OF SHARKS!
"""

s = requests.Session()

def exists(path):
    r = requests.head(path)
    return r.status_code == requests.codes.ok

def get_title(path):
        r = requests.get(path)
        html = BeautifulSoup(r.text)
        if html.title is not None:
                return html.title.text
        else:
                return ""

def fetch(url, data=None):
    if data is None:
        return s.get(url).content
    else:
        return s.post(url, data=data).content


print BOLD + HEADER + art + ENDC


def pwn(URL):

        soup = BeautifulSoup(fetch(URL))
        print ""
        print HEADER + "********************************************" + ENDC
        print HEADER + URL + ENDC
        print HEADER + "********************************************" + ENDC
        print ""
        print OKBLUE + "[>] Files used by Phishing kit" + ENDC

        files=[]
        filesprinted=[]
        dirs=['']

        ## First page
        for form in soup.findAll('form'):
                action=form.get('action')
                if action is not None:
                        if not action.startswith('http'):
                                if not action in filesprinted:
                                        print OKGREEN + "=> " + action + ENDC
                                        files.append(action)
                                        filesprinted.append(action)
                                        if '/' in action:
                                                dir=action.split('/')
                                                if not dir[0] in dirs:
                                                        dirs.append(dir[0])
                                                        print FAIL + "[!] Adding '" + dir[0] + "' folder  to the scope" + ENDC

                        else:
                                if not action in filesprinted:
                                        print WARNING + "=> " + action + "(out of scope)" + ENDC
                                        filesprinted.append(action)

        ## other levels
        for file in files:
                suburl= URL + file
                subsoup = BeautifulSoup(fetch(suburl))
                for form in subsoup.findAll('form'):
                        response = requests.get(suburl)
                        respurl=response.url
                        if not respurl in filesprinted:   # Redirection spotted
                                print OKGREEN + "=> " + respurl.replace(URL,"") + "(redirected HTTP 30X)"  + ENDC
                                filesprinted.append(respurl)
                                action=form.get('action')
                                if action is not None:
                                        if not action.startswith('http'):
                                                if not action in filesprinted:
                                                        print OKGREEN + "=> " + action + ENDC
                                                        files.append(action)
                                                        filesprinted.append(action)
                                                        if '/' in action:
                                                                dir=action.split('/')
                                                                if not dir[0] in dirs:
                                                                        dirs.append(dir[0])
                                                                        print FAIL + "[!] Adding '" + dir[0] + "' folder  to the scope" + ENDC
                                        else:
                                                if not action in filesprinted:
                                                        print WARNING + "=> " + action + "(out of scope)" + ENDC
                                                        filesprinted.append(action)

        #If URL contain page name (ie index.php), modify URL to only keep folder name
        if ".php" or ".html" or ".htm" in URL:
                pos=URL.rfind('/')
                URL=URL[:pos+1]

        print ""
        print OKBLUE + "[>] Looking for log files containing phished infos" + ENDC
        # Opening dic
        extensions=['txt','log','dat']
        for dir in dirs:
                if dir=='':
                        currURL=URL
                else:
                        currURL= URL + dir + '/'
                print OKBLUE + "[!] Scanning " + currURL + ENDC
                for ext in extensions:
                        with open('wordlist.dic') as f:
                                for content in f:
                                        content=content.strip()
                                        testurl=currURL + content + "." + ext
                                        #print "Testing " + testurl
                                        if exists(testurl):
                                                print OKGREEN + "=> " + testurl + ENDC


        print ""
        print OKBLUE + "[>] Looking for archive containing phishing kit" + ENDC
        extensions=['zip','tar','tar.gz']
        currURL=URL
        for ext in extensions:
                print OKBLUE + "[!] Search for " + ext  + " archives" +  ENDC
                with open('wordlist.dic') as f:
                        for content in f:
                                content=content.strip()
                                testurl=currURL + content + "." + ext
                                #print "Testing " + testurl
                                if exists(testurl):
                                        print OKGREEN + "=> " + testurl + ENDC

        print ""
        print OKBLUE + "[>] Looking for archive based on folder structure" + ENDC
        extensions=['zip','tar','tar.gz']
        urlsplit=URL.split('/')
        http=urlsplit[0]
        domain=urlsplit[2]
        urlsplit.remove(http)
        urlsplit.remove(domain)
        urlsplit=[x for x in urlsplit if x != '']

        site=http+"//"+domain+"/"
        for folder in urlsplit:
                for ext in extensions:
                        testurl=site + folder + "." + ext
                        #print "Testing " + testurl
                        if exists(testurl):
                                print OKGREEN + "=> " + testurl + ENDC
                site=site+folder+"/"

        print ""
        print OKBLUE + "[>] Looking for c99 & others" + ENDC
        shells=['c99.php','r57.php']
        urlsplit=URL.split('/')
        http=urlsplit[0]
        domain=urlsplit[2]
        urlsplit.remove(http)
        urlsplit.remove(domain)
        urlsplit=[x for x in urlsplit if x != '']

        site=http+"//"+domain+"/"
        for folder in urlsplit:
                for shell in shells:
                        testurl=site + shell
                        #print "Testing " + testurl
                        if exists(testurl):
                                print OKGREEN + "=> " + testurl + ENDC
                site=site+folder+"/"


        print ""
        print OKBLUE + "[>] Looking for Directory Listing" + ENDC
        urlsplit=URL.split('/')
        http=urlsplit[0]
        domain=urlsplit[2]
        urlsplit.remove(http)
        urlsplit.remove(domain)
        urlsplit=[x for x in urlsplit if x != '']

        site=http+"//"+domain+"/"
        for folder in urlsplit:
                testurl=site + folder + "/"
                #print "Testing " + testurl + " : " + get_title(testurl)
                if "Index" in get_title(testurl):
                        print OKGREEN + "=> " + testurl + ENDC
                site=site+folder+"/"


        print ""
        print OKBLUE + "[>] Sending mail to webmaster" + ENDC
        print OKGREEN + "[!] contact@" + domain + ENDC
		# delete this line for github
        print OKGREEN + "[!] webmaster@" + domain + ENDC
		# delete this line for github
		print OKGREEN + "[!] postmaster@" + domain + ENDC
		# delete this line for github
		
with open('targets.txt') as targets:
        for target in targets:
                target=target.rstrip("\n\r")
                pwn(target)
