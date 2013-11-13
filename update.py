import os
import sys
import urllib2
import re
from config import router_url, router_username, router_password, inwx_url, inwx_username, inwx_password, inwx_dnsid

passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
passman.add_password(None,router_url,router_username,router_password)
authhandler = urllib2.HTTPBasicAuthHandler(passman)
opener = urllib2.build_opener(authhandler)
urllib2.install_opener(opener)
router_status = urllib2.urlopen(router_url).read()
search = re.compile('<TD NOWRAP>(.*)</td>',re.MULTILINE)
matches = search.findall(router_status)
connection_status = matches[1]

if not connection_status == 'On':
    print("Offline, nothing to update.")
    sys.exit(0)

newip = matches[7]

if os.path.exists("/tmp/old.ip"):
    oldip = open("/tmp/old.ip","r").read().rstrip()
else:
    oldip = ""

if oldip == newip:
    print("Old IP = New IP, nothing to update.")
    sys.exit(0)

inwx_xml = """<?xml version="1.0" encoding="UTF-8"?>
<methodCall>
   <methodName>nameserver.updateRecord</methodName>
   <params>
      <param>
         <value>
            <struct>
               <member>
                  <name>user</name>
                  <value>
                     <string>%s</string>
                  </value>
               </member>
               <member>
                  <name>lang</name>
                  <value>
                     <string>en</string>
                  </value>
               </member>
               <member>
                  <name>pass</name>
                  <value>
                     <string>%s</string>
                  </value>
               </member>
               <member>
                  <name>id</name>
                  <value>
                     <int>%s</int>
                  </value>
               </member>
               <member>
                  <name>content</name>
                  <value>
                     <string>%s</string>
                  </value>
               </member>
               <member>
                  <name>ttl</name>
                  <value>
                     <int>3600</int>
                  </value>
               </member>
            </struct>
         </value>
      </param>
   </params>
</methodCall>""" % (inwx_username,inwx_password,inwx_dnsid,newip)

test = re.compile(".+Command completed successfully.+")

req = urllib2.Request(url=inwx_url, data=inwx_xml, headers={'Content-Type': 'text/xml'})
if test.match(urllib2.urlopen(req).read()):
    open("/var/log/dynamicdns.log","a").write("IP updated successfully! %s -> %s\n" % (oldip,newip))
    print("Update successful")
    open("/tmp/old.ip","w").write(newip)
    sys.exit(0)
else:
    open("/var/log/dynamicdns.log","a").write("IP update failed!\n" % (oldip,newip))
    print("Update failed")
    sys.exit(1)


