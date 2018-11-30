import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET

def GetSites(USERNAME, PASSWORD, APIURL):
# Function to return a list of site names
        site_list = []
        site_list_url = APIURL+'sites'
	try:
		site_list_XML = requests.get(site_list_url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
	except:
		print "Error: could not connect to "+site_list_url
        for site in ET.fromstring(site_list_XML.content):
                if (site.tag == 'site'):
                        site_list.append(site[1].text)
        print "Sites Found:"
        for site in site_list:
                print site
        return site_list
