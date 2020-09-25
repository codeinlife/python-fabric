#!/usr/bin/env python

import os, sys, getopt, fnmatch, re


# check either python 2 or python 3
NEWINPUT = None
try:
	NEWINPUT = raw_input
except NameError:
	NEWINPUT = input


'''
Developer: Mike LIM - 09/2017 - Version: 0.5.2.3

Desciprtion: This script will replace string in files recursively and re-write them

Usage: python replace.py "the work path" >> do not forget add double quotes around a path


what does this script do (all file types)?

<script language="javascript"> or <script language="JavaScript">
<!--
.
.
//-->
</script>

will be replaced to this new way

<script type="text/javascript">
.
.
</script>

will remove <!-- and //--> as well, however, some of files do not close javascript tag proper way 

for example,

<script language="javascript"> or <script language="JavaScript">
<!--
.
.
-->
</script>

in this case you need to fix manually. How to check this? you need to run this script first then compare with 7.20.400 template

but html comments like this one 

<!-- some text here --> 

will not be touched
'''

def replace(argv):
	try:
		# default False
		is_c_answer = False
		c_answer = NEWINPUT('\nDid you add double quotes around the path? (y/n) ')
		if c_answer.lower() == 'y' or c_answer.upper() == 'Y':
			is_c_answer = True
		else:
			is_c_answer = False

		if is_c_answer:
			directory_name = sys.argv[1]
			# will check all files
			file_pattern = '*'
			for path, dirs, files in os.walk(os.path.abspath(directory_name)):
				# skip .git directory
				if '.git' in dirs:
					dirs.remove('.git')

				# skip some file extensions
				files = [ file for file in files if not file.endswith(('.jpg','.jpeg','.gif','.png','.psd','.pdf','.xml','.less','.css','.ai','.svg','.zip')) ]

				for filename in fnmatch.filter(files, file_pattern):
					filepath = os.path.join(path, filename)
					with open(filepath) as f:
						line = f.read()
						line = re.sub(r'<script language=\"JavaScript\"', '<script type=\"text/javascript\"', line, flags=re.IGNORECASE)
						#line = re.sub(r'<script>\n', '<script type=\"text/javascript\">\n', line, flags=re.IGNORECASE)
						line = re.sub(r'<!--\n|\s*\/\/-->|\s*\/\/\s-->', '', line)
					with open(filepath, "w") as f:
						print(filepath)
						f.write(line)
	except Exception as e:
		print('\nOops ...')
		print(e)
		print('\nUsage: python replace.py "the work path" >> do not forget add double quotes around a path')

if __name__ == "__main__":
	replace(sys.argv[1:])