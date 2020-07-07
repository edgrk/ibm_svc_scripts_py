######################################################################################
# Generate list of degraded/offline hosts from all SVC
#Written by Edgar Kacko
#2020
######################################################################################
import requests
import getpass
import urllib3
import paramiko
import json
import csv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Defining TPC servers
tpc1 = "yourTPCserver"
tpc2 = "yourTPCserver"
#List of TPC servers
tpclist =[tpc1,tpc2]
#Authorization
username = getpass.getuser()
password = getpass.getpass()

#Helper objects
listofdict = []
ddict = {}
list3 = []


#Define SSH and base command to run
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cmdtorun = "lshost -nohdr -delim ,"


#Defining helper function to get list of SVCs
def tpc_data(spc_base_url):
    session = requests.Session()
    session.verify = False
    response = session.post(spc_base_url + "j_security_check", data={"j_username": username, "j_password": password})
    response.raise_for_status()
    response = session.get(spc_base_url + "REST/api/v1/" + "StorageSystems")
    response.raise_for_status()
    reponse_json = response.json()
    filtr = [i for i in reponse_json if i["Type"] == "SAN Volume Controller - 2145"]
    for name in filtr:
        ddict["SVC"] = name["Name"]
        ddict["IP"] = name["IP Address"]
        listofdict.append(dict(ddict))

#Loop to obtain data
for name in tpclist:
    tpc_data(name)

#Main loop to get data from SVC.
try:
    for name in listofdict:
        svcname = name["SVC"]
        hostname = name["IP"]
        ssh_client.connect(hostname=hostname, username=username, password=password)
        stdin,stdout,stderr = ssh_client.exec_command(cmdtorun)
        output = stdout.readlines()
        #Parcel of SVC output to separate dictonary
        for line in output:
            parcel = (svcname + ',' + line)
            list2 = parcel.split(',') 
            new_dict = {"SVC_name":list2[0],
                        "Host ID":list2[1],
                        "Host Name":list2[2],
                        "Port Count":list2[3],
                        "Iogroup Count":list2[4],
                        "Status":list2[5],
                        }
                            
            list3.append(new_dict)
            dic_json = json.dumps(list3)
            dic_json1 = json.loads(dic_json)
except:
    pass

#Filter for offline/degraded paths
filtr = [i for i in dic_json1 if i["Status"] == "degraded" or i["Status"] == "offline"]

#Store results in csv file
with open('data.csv', 'w', encoding='utf8', newline='') as output_file:
    fc = csv.DictWriter(output_file, 
                        fieldnames=filtr[0].keys(),

                       )
    fc.writeheader()
    fc.writerows(filtr)