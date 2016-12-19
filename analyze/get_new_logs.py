import xml.etree.ElementTree as ET
import urllib
import os.path

def eligible(text):
	return ".xz" in text and "real-world-results" in text and "FAILED" not in text

def crop(filename):
	i = filename.find("/")
	while '/' in filename[i + 1:]:
		filename = filename[i + 1 :]
		i = filename.find("/")
	return filename[i + 1:]

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


# Download all logs
filesaver = urllib.URLopener()
for name in filenames:
	if not os.path.exists(results_dir + crop(name)):
		print name
		filesaver.retrieve(base_link + name, results_dir + crop(name))

