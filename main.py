import json
import logging
import re
from typing import Optional

from flask import Flask, request, Response
import requests
from waitress import serve

with open("conf/main.json", "rb") as configFile:
	config = json.loads(configFile.read().decode())

app = Flask(__name__)

def PostAction(content: bytes) -> bytes:
	try:
		html = content.decode()
	except Exception as e:
		print(e)
		return content

	# wow.zamimg.com cdn
	zamimg = config['cdn']
	if zamimg:
		html = re.sub(r'https://wow.zamimg.com/', zamimg, html)

	# ajax.googleapis.com cdn
	html = re.sub(r'https://ajax.googleapis.com/', 'https://ajax.proxy.ustclug.org/', html)

	return html

@app.route("/")
def RpIndex():
	header = {
		'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
	}
	r = requests.get('https://cn.wowhead.com/', headers = header)
	return PostAction(r.content), r.status_code

@app.route("/<path:path>")
def RpMain(path):
	header = {
		'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
	}
	if request.referrer:
		header['referer'] = re.sub(r'https?://[^/]*/', 'https://cn.wowhead.com/', request.referrer)
	r = requests.get('https://cn.wowhead.com/' + path, headers = header)
	return Response(PostAction(r.content), status = r.status_code, content_type = r.headers['Content-Type'])

if __name__ == "__main__":

	if config["cors"]:
		@app.after_request
		def AfterRequest(response):
			header = response.headers
			header['Access-Control-Allow-Origin'] = '*'
			return response

	if config["debug"]:
		app.run(
			debug = True,
			host = config["listenHost"],
			port = config["listenPort"],
		)
	else:
		logger = logging.getLogger('waitress')
		logger.setLevel(logging.INFO)
		serve(
			app,
			host = config["listenHost"],
			port = config["listenPort"],
		)
