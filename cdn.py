import json
import logging
import re

from flask import Flask, request, Response
import requests
from waitress import serve

from common import PostAction

with open("conf/cdn.json", "rb") as configFile:
	config = json.loads(configFile.read().decode())

app = Flask(__name__)

@app.route("/<path:path>")
def RpMain(path):
	header = {
		'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
	}
	if request.referrer:
		header['referer'] = re.sub(r'https?://[^/]*/', 'https://cn.wowhead.com/', request.referrer)
	r = requests.get('https://wow.zamimg.com/' + path, headers = header)
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
