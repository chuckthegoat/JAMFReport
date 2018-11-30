import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET

class Config_Profile:
	def __init__(self, config_XML):
		general = ET.fromstring(config_XML.content)[0]
		scope = ET.fromstring(config_XML.content)[1]
		
		self.id = general[0].text
		self.name = general[1].text
		self.site = general[3][1].text
		self.category = general[4][1].text
		self.payloads = general[10].text
		self.computers = []
		self.computer_groups = []
		
		for scope_item in scope:
			if (scope_item.tag == 'computers'):
				for computer in scope_item:
					self.computers.append(computer[1].text)
			elif (scope_item.tag == 'computer_groups'):
				for computer_group in scope_item:
					self.computer_groups.append(computer_group[1].text)

def GetConfigs(USERNAME, PASSWORD, APIURL):
	print 'Downloading configuration profiles...'
	# Generate a list of configuration profile IDs
	config_id_list = []
	config_id_list_url = APIURL+'osxconfigurationprofiles'
	try:
		config_id_list_XML = requests.get(config_id_list_url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
	except:
		print "Error: could not connect to "+config_id_list_url
	for config in ET.fromstring(config_id_list_XML.content):
		if (config.tag == 'os_x_configuration_profile'):
			# Append the ID to the list of configuration profile IDs
			config_id_list.append(config[0].text)

	# Generate an array of configuration profile objects
	config_list = []
	config_url = APIURL+'osxconfigurationprofiles/id/'
	for config_id in config_id_list:
		config_XML = requests.get(config_url+config_id, auth=HTTPBasicAuth(USERNAME, PASSWORD))
		try:
			# Create Config_Profile object with id, name, site name, category name, and payload contents
			config_list.append(Config_Profile(config_XML))
		except:
			print "Error: could not create configuration profile with id "+config_id
	print 'Configuration profile download complete.'
	return config_list
