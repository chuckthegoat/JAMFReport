# Imported modules
import sys
import os
import datetime
import threading
import Queue
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET

# Custom modules
sys.path.append("./lib")
import configprofiles
import groups
import policies
import sites

# Variables for connecting to the JSS and building the directory tree
from config import *
DATE = str(datetime.date.today())

# Thread class for downloading lists of objects from the JSS
class DownloadThread(threading.Thread):
	# Initialize with the download function, the queue to put the result in, and the function arguments
	def __init__(self, function, queue, *args):
		threading.Thread.__init__(self)
		self.function = function
		self.queue = queue
		self.args = []
		for arg in args:
			self.args.append(arg)
	def run(self):
		# Place the results of the function with arguments args in the queue
		self.queue.put(self.function(*self.args))
		
# Function to generate xml files for each configuration profile
def WriteConfigProfiles(configs, root):
	for config in configs:
		path = root+config.site+'/'+config.category+'/'
		# If there is no directory for the category, create it
		if not os.path.exists(path):
			print 'Directory '+path+' does not exist in the backup root. Creating...'
			try:
				os.mkdir(path)
			except:
				print 'Error: could not create directory'
		# Create the file and write the payloads to it
		config_file = open(path+config.name+'.xml', "w")
		config_file.write(config.payloads)
		# Close the file
		config_file.close()

# Function to generate scoping information and write it to a csv
def WriteScoping(groups, root):
	for group in groups:
		# If there is not a report yet for a site, create it
		report = root+group.site+'/'+'scoping_report.csv'
		if not os.path.exists(report):
			print 'File '+report+' does not exist. Creating...'
			try:
				# Start the report
				report_file = open(report, "w+")
				report_file.write("\"Group\",\"Scope\",\"Parent Of\",\"Not Parent Of\",\"Child Of\",\"Not Child Of\"\n")
				# Append the current group as a line in the report
				report_file.write("\""+group.name+"\",\""+", ".join(group.scope)+"\",\""+", ".join(group.parent_of)+"\",\""+", ".join(group.not_parent_of)+"\",\""+", ".join(group.child_of)+"\",\""+", ".join(group.not_child_of)+"\"\n")
				# Close the file
				report_file.close()
			except:
				print 'Error: could not create file'
		else:
			# Append the current group as a line in the report
			report_file = open(report, "a")
			report_file.write("\""+group.name+"\",\""+", ".join(group.scope)+"\",\""+", ".join(group.parent_of)+"\",\""+", ".join(group.not_parent_of)+"\",\""+", ".join(group.child_of)+"\",\""+", ".join(group.not_child_of)+"\"\n")
			# Close the file
			report_file.close()

# Function to build the base directory tree
def CreateSiteFolders(sites, root):
	# Create a directory under the root for the daily backup
	path = root+'/'+DATE+'/'
	if not os.path.exists(path):
		print 'Creating daily directory '+path
		try:
			os.mkdir(path)
		except:
			print 'Error: could not create directory'
	# Create directories for each site
	for site in sites:
		sitepath = path+site+'/'
		if not os.path.exists(sitepath):
			print 'Directory '+sitepath+' does not exist in the backup root. Creating...'
			try:
				os.mkdir(sitepath)
			except:
				print 'Error: could not create directory'
	# Return the path of the daily directory
	return path

if __name__ == '__main__':
	# Get a list of sites
	sites = sites.GetSites(USERNAME, PASSWORD, APIURL)
	# Creat the daily directory tree
	dailypath = CreateSiteFolders(sites, BACKUP_ROOT)

	# Create queues to hold the results of the config, policy, and group download functions
	config_queue = Queue.Queue()
	policy_queue = Queue.Queue()
	group_queue = Queue.Queue()
	# Create threads for the config, policy, and group download functions
	config_thread = DownloadThread(configprofiles.GetConfigs, config_queue, USERNAME, PASSWORD, APIURL)
	policy_thread = DownloadThread(policies.GetPolicies, policy_queue, USERNAME, PASSWORD, APIURL)
	group_thread = DownloadThread(groups.GetGroups, group_queue, USERNAME, PASSWORD, APIURL)
	# Start the threads
	config_thread.start()
	policy_thread.start()
	group_thread.start()
	# Wait for all of the threads to finish
	config_thread.join()
	policy_thread.join()
	group_thread.join()
	# Retrieve the config, policy, and grouplists from their respective queues
	config_list = config_queue.get()
	policy_list = policy_queue.get()
	group_list = group_queue.get()

	# Create the config profile xml files
	WriteConfigProfiles(config_list, dailypath)
	# Scope the config profiles and policies to the list of groups
	groups.ScopeObjects(group_list, config_list)
	groups.ScopeObjects(group_list, policy_list)
	# Create the scoping report
	WriteScoping(group_list, dailypath)
