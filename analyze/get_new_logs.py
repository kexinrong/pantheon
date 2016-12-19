import xml.etree.ElementTree as ET
import urllib
import os.path
import contextlib
import lzma
import tarfile
import subprocess
import shutil

def eligible(text):
	return ".xz" in text and "real-world-results" in text and "FAILED" not in text

def crop(filename):
	i = filename.find("/")
	while '/' in filename[i + 1:]:
		filename = filename[i + 1 :]
		i = filename.find("/")
	return filename[i + 1:]

def strip_extension(filename):
	i = filename.find(".")
	return filename[:i]

base_link = "https://stanford-pantheon.s3.amazonaws.com/"
results_dir = "pantheon_logs/"
tree = ET.parse("pantheon.xml")
root = tree.getroot()

# Get all log links
filenames = []
for contents in root:
	if not "Contents" in contents.tag:
		continue
	for attrib in contents:
		if "Key" in attrib.tag:
			if eligible(attrib.text):
				filenames.append(attrib.text)

# Create table header if needed
if not os.path.exists("pantheon_logs.csv"):
	f = open("pantheon_logs.csv", "w")
	f.write("cc,tpt,delay,loss_rate,cc_hash,master_hash,mahimahi_hash,libutp_hash,"
	    +"sourdough_hash,DOW,start_time,end_time,runtime,is_cellular,sender," + 
	    "sender_address,receiver,receiver_address\n")
	f.close()
	f = open("pantheon_logs_included.txt", "w")
	f.close()

logs = open("pantheon_logs_included.txt", "r")
included = []
for line in logs.readlines():
	included.append(line.strip())
logs.close()

logs = open("pantheon_logs_included.txt", "a")
filesaver = urllib.URLopener()
for name in filenames:
	fname = results_dir + crop(name)
	# download logs from s3
	if not os.path.exists(results_dir + crop(name)):
		print "downloading %s" % fname
		filesaver.retrieve(base_link + name, fname)
	# if not included in the table, generate results
	if not fname in included and "tar" in fname:
		print "processing %s" % fname
		with contextlib.closing(lzma.LZMAFile(fname)) as xz:
		    with tarfile.open(fileobj=xz) as f:
				folder = results_dir + strip_extension(crop(name))
				f.extractall(results_dir)
				subprocess.call('python gen_result_table.py --data-dir "%s"' %(folder), shell=True)
				shutil.rmtree(folder)
		logs.write(fname + "\n")

logs.close()
