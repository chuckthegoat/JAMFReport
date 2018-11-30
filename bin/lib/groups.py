import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET

class Group:
# Defines a class to associate group objects with
        def __init__(self, group_XML):
		general = ET.fromstring(group_XML.content)

                self.id = general[0].text
                self.name = general[1].text
                self.is_smart = general[2].text
		self.site = general[3][1].text
                self.scope = []
                self.parent_of = []
                self.not_parent_of = []
                self.child_of = []
                self.not_child_of = []

		for criterion in general[4]:
			if (criterion.tag == "criterion" and criterion[0].text == "Computer Group"):
				if (criterion[3].text == "not member of"):
					self.not_child_of.append(criterion[4].text)
				elif (criterion[3].text == "member of"):
					self.child_of.append(criterion[4].text)

def ScopeGroupParents(groups):
	for group in groups:
		for child in groups:
			if (group.name in child.not_child_of):
				group.not_parent_of.append(child.name)
			elif (group.name in child.child_of):
				group.parent_of.append(child.name)

def GetGroups(USERNAME, PASSWORD, APIURL):
# Function to populate a list of group objects from Casper using the API and return that list.
	print 'Downloading groups...'
	# Generate a list of group IDs
	group_id_list = []
	group_id_list_url = APIURL+'computergroups'
	try:
		group_id_list_XML = requests.get(group_id_list_url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
	except:
		print "Error: could not connect to "+group_id_list_url
	for group in ET.fromstring(group_id_list_XML.content):
		if (group.tag == 'computer_group'):
			group_id_list.append(group[0].text)

	# Generate an array of group objects
        group_list = []
	group_url = APIURL+'computergroups/id/'
	for group_id in group_id_list:
		try:
			group_XML = requests.get(group_url+group_id, auth=HTTPBasicAuth(USERNAME, PASSWORD))
		except:
			print "Error: could not connect to "+group_url+group_id
		group = ET.fromstring(group_XML.content)
		try:
			# Create a new group object with id, name, is_smart, and site
			group_list.append(Group(group_XML))
		except:
			print "Error: could not create group with id "+group[0].text

	# Populate the scoping information for the group objects
	ScopeGroupParents(group_list)
	
	print 'Group download complete.'
        return group_list

def ScopeObjects(groups, objects):
	for group in groups:
		for object in objects:
			if (group.name in object.computer_groups):
				group.scope.append(object.name)
