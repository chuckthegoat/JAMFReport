import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET

class Policy:
        def __init__(self, policy_XML):
		general = ET.fromstring(policy_XML.content)[0]
		scope = ET.fromstring(policy_XML.content)[1]

                self.id = general[0].text
                self.name = general[1].text
		self.computers = []
		self.computer_groups = []

                for scope_item in scope:
                        if (scope_item.tag == 'computers'):
                                for computer in scope_item:
                                        self.computers.append(computer[1].text)
                        elif (scope_item.tag == 'computer_groups'):
                                for computer_group in scope_item:
                                        self.computer_groups.append(computer_group[1].text)

def GetPolicies(USERNAME, PASSWORD, APIURL):
	print 'Downloading policies...'
        # Generate a list of policy IDs
        policy_id_list = []
        policy_id_list_url = APIURL+'policies'
	try:
		policy_id_list_XML = requests.get(policy_id_list_url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
	except:
		print "Error: could not connect to "+policy_id_list_url
        for policy in ET.fromstring(policy_id_list_XML.content):
                if (policy.tag == 'policy'):
                        # Append the ID to the list of policyuration profile IDs
                        policy_id_list.append(policy[0].text)

        # Generate an array of policyobjects
        policy_list = []
        policy_url = APIURL+'policies/id/'
        for policy_id in policy_id_list:
		try:
			policy_XML = requests.get(policy_url+policy_id, auth=HTTPBasicAuth(USERNAME, PASSWORD))
		except:
			print "Error: could not connect to "+policy_url+policy_id
                try:
                        # Create Policy object with id, and name
			policy_list.append(Policy(policy_XML))
                except:
                        print "Error: could not create policy with id "+policy_id
	print 'Policy download complete.'
        return policy_list
