import json
import re

with open("conf/common.json", "rb") as configFile:
	config = json.loads(configFile.read().decode())

def PostAction(content: bytes) -> bytes:
	try:
		html = content.decode()
	except Exception as e:
		print(e)
		return content

	# fix explicit main site
	mainsite = config['main']
	if mainsite:
		html = re.sub(r'https://cn.wowhead.com/', mainsite, html)

	# wow.zamimg.com cdn
	zamimg = config['cdn']
	if zamimg:
		html = re.sub(r'https://wow.zamimg.com/', zamimg, html)

		# special handling tooltip.js
		html = re.sub(r'"https://wow.zamimg.com"', f'"{zamimg}"', html)

	# ajax.googleapis.com cdn
	html = re.sub(r'https://ajax.googleapis.com/', 'https://ajax.proxy.ustclug.org/', html)

	return html
