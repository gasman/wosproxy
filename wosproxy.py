#!/usr/bin/env python

import web
import urllib2
import urlparse
import zipfile
import StringIO

WOS_ROOT = 'ftp://ftp.worldofspectrum.org/pub/sinclair/'
#WOS_ROOT = 'http://localhost/~matthew/fakewos/'
ALLOWED_PATHS = [
	'compilations/'
	'demos/',
	'games/',
	'misc/',
	'slt/',
	'trdos/',
	'utils/',
	'zx81/games/',
]
MAX_SIZE = 1474560


def get_wos_file(wos_path):
	url = urlparse.urljoin(WOS_ROOT, wos_path)
	is_allowed = False

	for path in ALLOWED_PATHS:
		if url.startswith(WOS_ROOT + path):
			is_allowed = True
			break

	if not is_allowed:
		raise Exception("Access to this file is blocked")
	f = urllib2.urlopen(url)
	file_content = f.read(MAX_SIZE + 1)
	f.close()
	if len(file_content) > MAX_SIZE:
		raise Exception("Cannot fetch files larger than %s bytes" % MAX_SIZE)
	return file_content


class MainHandler:
	def GET(self):
		return 'Hello world!'


class UnzipHandler:
	def GET(self, wos_path):
		f = StringIO.StringIO(get_wos_file(wos_path))
		z = zipfile.ZipFile(f)
		file_content = None
		filename = None
		for zipinfo in z.infolist():
			filename = zipinfo.filename
			file_content = z.read(zipinfo.filename)
			break

		if not file_content:
			raise Exception("Empty ZIP file")

		web.header("Content-Disposition", "attachment; filename=\"%s\"" % filename)
		web.header("X-Filename", filename)
		web.header("Access-Control-Allow-Origin", "*")
		web.header("Content-Type", "application/octet-stream")
		return file_content


class ZipHandler:
	def GET(self, wos_path):
		file_content = get_wos_file(wos_path)
		web.header("Content-Type", "application/octet-stream")
		web.header("Access-Control-Allow-Origin", "*")
		return file_content

urls = (
	'/', 'MainHandler',
	'/zip/(.*)', 'ZipHandler',
	'/unzip/(.*)', 'UnzipHandler',
)
app = web.application(urls, globals())

if __name__ == "__main__":
	app.run()
