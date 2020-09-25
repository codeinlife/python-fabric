#!/usr/local/bin/python3
# ........._\____
# ......../__|___\__
# .......(0)____(0)_\

from tqdm import tqdm


#########################################################################
##
## OTHER FUNCTIONS WILL BE HERE
##
#########################################################################
def create_bar(*args, **kwargs):
	# Instanciate tqdm bar once
	pbar = tqdm(*args, **kwargs)
	# Create the actual callback
	def viewbar(a, b):
		pbar.total = int(b)
		pbar.update(a)
	# Return the callback
	return viewbar