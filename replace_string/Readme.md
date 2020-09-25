# Replace an old way javascript tag to a new way

**Run this script**
	
	* You need to run this script first before upgrading to use an Araxis Merge
	* Open windows shell not git bash
	* python replace.py [path]

**Excluded directory and file extensions**

	* Directory - .git
	* Extensions - .jpg, .jpeg, .gif, .png, .psd, .pdf, .xml, .less, .css, .ai, .svg, .zip

**what does this script do (all file types)?**
	
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