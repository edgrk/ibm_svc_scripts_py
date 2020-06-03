######################################################################################
# Look for SVC UID in Spectrum Control/TPC
#Written by Edgar Kacko
#2020
######################################################################################
import requests
import getpass
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from beautifultable import BeautifulTable

#Define TPC instances
tpc1 = 'https://tpc1:9569/srm/'
tpc2 = 'https://tpc2:9569/srm/'
tpc3 = 'https://tpc3:9569/srm/'
tpclist =[tpc1,tpc2,tpc3]
#Credentials for TPC
username = getpass.getuser()
password = getpass.getpass()
#File with LUN UID
serial = open("serial.txt").read().splitlines()
#Define a table for data output
table = BeautifulTable(max_width=10000)
table.set_style(BeautifulTable.STYLE_COMPACT)
table.column_headers = ["Storage System", "LUN name", "LUN UID", "LUN ID", "Pool", "Compression"]

#Functions
#TPC handlers
def connect_to_tpc(spc_base_url, p_username, p_password):
    '''
    Connects to single TPC, returns the session (connection) hanlder. 
    '''
    session = requests.Session()
    session.verify = False
    response = session.post(spc_base_url + 'j_security_check', data={'j_username': p_username, 'j_password': p_password})
    response.raise_for_status()
    return session

def get_from_tpc(session, url):
    '''
    For given, opened, session it sends HTTP GET call to the TPC.
    '''
    response = session.get(url)
    response.raise_for_status()
    reponse_json = response.json()
    return reponse_json # this returns list

#Main function
def tpc_data(spc_base_url):
    session = connect_to_tpc(spc_base_url, username, password)
    reponse_json = get_from_tpc(session, spc_base_url + 'REST/api/v1/' + 'StorageSystems')
    filtr = [i for i in reponse_json if i['Type'] == 'SAN Volume Controller - 2145']
    for id in filtr:
        vid = id['id']
        reponse_json1 = get_from_tpc(session, spc_base_url + 'REST/api/v1/' + 'StorageSystems/'+vid +'/Volumes')
        for s in serial:
            filt = [i for i in reponse_json1 if i['Volume Unique ID'] == s.lower()]
            for name in filt:
                table.append_row([name['Storage System'],name['Name'],name['Volume Unique ID'], name['Volume ID'], name['Pool'],name['Compressed']])

#main
for name in tpclist:
    tpc_data(name)
print(table)
