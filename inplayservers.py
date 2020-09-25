#!/usr/local/bin/python3
# ........._\____
# ......../__|___\__
# .......(0)____(0)_\
import requests
from bs4 import BeautifulSoup

'''
Function to determine whether the current row has the link id and server information
Change this if the html structure changes
Currently set up to check for first td in a row where:
	- the td has a valid string
	- the string has no spaces inside of it
<row>
	<td>
	</td>
</row>
'''
def rowIsValid(row):
	return row.td is not None and row.td.string is not None and not ' ' in row.td.string

'''
Gets the server information from the inPlay page
Returns:
{
	"linkId": ["serverNames"]
}
'''
def getServerInformation():
	# We need portwise to access this URL
	try:
		doc = requests.get('http://172.31.1.20/bigip/In_Play_Status_Page/index.html')
	except:
		print "Error reaching in play status page - make sure you are connected to PortWise!"
	soup = BeautifulSoup(doc.content, 'html.parser')
	servers = {}
	for row in soup.find_all('tr'):
		if rowIsValid(row):
			# Get the latest servers shown by the page - includes home and inplay
			home_servers = row.find_all('td')[1].get_text().split('\n') # home servers are split by \n
			inplay_servers = row.find_all('td')[2].get_text().split(' ') # inplay servers are split by spaces
			# Find unique servers
			unique_servers = set(home_servers + inplay_servers)
			servers[row.td.string] = list(unique_servers)

	# Only exceptions are multi language sites ticketpop, centrepointe, ottawa67, lcpa, bluesfestfr - which we group with 
	return servers
