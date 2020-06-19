#jabber_home_cluster.py
"""
Published on GitHub 2020-06-22

For each CUCM cluster
   Build a list with the CSF device information per the class csf
   Build a list with the user information per the class user_ucm
Parse these lists to generate the actionable results.
This program takes 6+ hours to run for all 24 CUCM clusters.

https://paultursan.com/2016/04/getting-started-with-python-cucm-axl-api-programming/
Requires ZEEP, the SOAP API for Python
"""
from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.exceptions import Fault
from zeep.plugins import HistoryPlugin
from requests import Session
from requests.auth import HTTPBasicAuth
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from lxml import etree
import requests
import re
import csv
import smtplib
import email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
global path
path = r"H:\Programming\python\UDS"
global path2
path2 = r"H:\Programming\python\UDS"
global csf_list
csf_list = []
global uid_list
uid_list = []
global cucm_list
cucm_list = []
global out_list
out_list = []


from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

disable_warnings(InsecureRequestWarning)
username = 'Automation'
password = 'Automation'

class cucm:
   def __init__(host, hostname, ver, rhm, city):
      host.hostname = hostname
      host.ver = ver
      host.rhm = rhm
      host.city = city

class csf:
   def __init__(csf, device, uid, ucm, home):
      csf.device = device
      csf.uid = uid
      csf.ucm = ucm
      csf.home = home

class user_ucm:
   def __init__(user, uid, ucm, home):
      user.uid = uid
      user.ucm = ucm
      user.home = home

def send_email(email_str):
   msg = MIMEText(email_str)
   msg['To'] = "user1@yourcompany.com,user2@yourcompany.com"
   msg['From'] = email.utils.formataddr(('HOME_CLUSTER', 'UCtools@yourcompany.com'))
   msg['Subject'] = 'Jabber Home Cluster Tool'
   server = smtplib.SMTP('pop.yourcompany.com', 25)
   server.set_debuglevel(False) # show communication with the server
   try:
      server.sendmail(msg['From'], msg['To'].split(","), msg.as_string())
   finally:
      server.quit()
      
def show_history():
   for item in [history.last_sent, history.last_received]:
      print(etree.tostring(item["envelope"], encoding="unicode", pretty_print=True))
      
def build_lists(host,ver):
   wsdl = 'file://H:/Programming/python/CUCM/AXL/axlsqltoolkit/schema/' + ver + '/AXLAPI.wsdl'
   location = 'https://{host}:8443/axl/'.format(host=host)
   binding = "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding"

   session = Session()
   session.verify = False
   session.auth = HTTPBasicAuth(username, password)
   transport = Transport(cache=SqliteCache(), session=session, timeout=20)
   history = HistoryPlugin()
   client = Client(wsdl=wsdl, transport=transport, plugins=[history])
   service = client.create_service(binding, location)
   # build the csf_list
   try:
      resp = service.listPhone(searchCriteria={'name': '%'}, returnedTags={'name': '', 'description': '', 'model': ''})
      try:
          phone_list = resp['return'].phone
          for phone in phone_list:
            if phone.model == 'Cisco Unified Client Services Framework':
               try:
                  resp1 = service.getPhone(name=phone.name)
                  dev = resp1['return'].phone
                  try:
                     resp = service.listUser(searchCriteria={'userid': dev.ownerUserName._value_1}, \
                        returnedTags={'firstName': '', 'lastName': '', 'userid': ''})
                     try:
                        user_list = resp['return'].user
                        for user in user_list:
                           try:
                              resp1 = service.getUser(uuid=user.uuid)
                              guser = resp1['return'].user
                              csf_list.append( csf(phone.name,  dev.ownerUserName._value_1, host, guser['homeCluster']))
                           except:
                              continue    
                     except:
                        return
                  except Fault:
                     show_history()
               except:
                  continue      
      except:
         return
   except Fault:
      show_history()
   # build the uid_list
   try:
      resp = service.listUser(searchCriteria={'userid': '%'}, returnedTags={'firstName': '', 'lastName': '', 'userid': ''})
      try:
          user_list = resp['return'].user
          for user in user_list:
            try:
               resp1 = service.getUser(uuid=user.uuid)
               guser = resp1['return'].user
               uid_list.append( user_ucm(user.userid, host, guser['homeCluster']))
            except:
               continue    
      except:
         return
   except Fault:
      show_history()

def read_cucm():
   #read the cucm, version, and rhm from an input file for processing
   in_file = open(path2 + "\cucm-fqdn-ver.txt","r")
   cucm_read = csv.reader(in_file)
   for ucm in cucm_read:
      cucm_list.append( cucm(ucm[0], ucm[1], ucm[2], ucm[3])) # see cucm class for mapping

def parse_lists():
   email_str = ''
   out_str = ("CSF Device,CSF UID,CSF UCM,CSF Home Cluster,UID UCM,UID Home Cluster\n")
   out_list.append(out_str)
   admins = ['admin1', 'admin2', 'admin3']
   for dev_row in csf_list:
      if dev_row.uid not in admins:
         for user_row in uid_list:
            if user_row.uid == dev_row.uid:
               to_print = 0
               if dev_row.home == 'false':
                  to_print = 1
               if dev_row.ucm != user_row.ucm and user_row.home == 'true':
                  to_print = 1
               if to_print == 1:
                  out_str = (dev_row.device + ',' + dev_row.uid + ',' + dev_row.ucm + ',' +\
                     dev_row.home + ',' + user_row.ucm + ',' + user_row.home)
                  out_list.append(out_str)
   for row in out_list:
      email_str = email_str + row + '\n'
   return email_str
   
def main():
   read_cucm()
   for ucm in cucm_list:
      print("Build CSF & UID list " + ucm.rhm)
      build_lists(ucm.hostname, ucm.ver)
   
   email_str = parse_lists()
   send_email(email_str)

   out_file = open(path + "\\home_problem.csv","w")
   out_file.write('\n'.join(out_list))
   out_file.close()

if __name__== "__main__":
   main()
