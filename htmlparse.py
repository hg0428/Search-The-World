#https://deepai.org/machine-learning-model/nsfw-detector
from urllib3 import PoolManager
import html_text
import cssutils
http = PoolManager()
try:
	from BeautifulSoup import BeautifulSoup, ResultSet
except ImportError:
	from bs4 import BeautifulSoup, ResultSet
from urllib.parse import urlparse, urljoin, urlunparse
import json
from bs4.element import Comment
import re
import time
import requests


def image_detector(src):
	#print(src)
	r = requests.post(
			"https://api.deepai.org/api/nsfw-detector",
			data={
					'image': src,
			},
			headers={'api-key': 'd0b362a7-84c8-48f4-b7c4-a6ffb078972a'})
	j = r.json()
	#print(type(j), j)
	if 'err' in j:return 0.2
	return j["output"]["nsfw_score"]


helper = json.load(open("helper.json"))


def GetData(url, contenType="html"):
	try:
		response = http.request(
				"GET",
				url,
				headers={
						"Identity":
						"Projxon Web Crawler 01",
						"User-Agent":
						"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15"
				})
	except:
		return False
	#try:
	f = response.data
	if f == False: return False
	if content_type := response.headers.get('Content-Type'):
		content_type = content_type.lower()
		if contenType not in content_type: return False
	if response.status != 200: return False
	return f.decode()


def tag_visible(element):
	if element.parent.name in [
			'style', 'script', 'head', 'meta', "[document]", "div"
	]:
		return False
	if isinstance(element, Comment):
		return False
	return True


def GetText(data):
	open("testtxt", "w+").write(data)
	return html_text.extract_text(data, guess_layout=False)


def getTitle(soup, urlp):
	try:
		title = str(soup.title.string)
	except:
		title = urlp.netloc
	return title


def getFavicon(soup, site):
	icon_link = soup.find("link", rel="shortcut icon")
	if icon_link is None:
		icon_link = soup.find("link", rel="icon")
	if icon_link is None:
		return urljoin(site, '/favicon.ico')
	return urljoin(site, icon_link["href"])


def GetInfo(website, up):
	#up = urlparse(website)
	saved = {
			'link': website,
			'base': up.netloc,
			'scheme': up.scheme,
			'description': ""
	}
	f_data = str(GetData(website))
	#f= ' '.join(str(f).split())
	if f_data == False:
		print("Error:", website)
		return False
	soup = BeautifulSoup(f_data, features="html5lib")
	for tagname in helper:
		for tag in helper[tagname]:
			t = soup.findAll(tagname, tag["requirements"])
			for i in t:
				if tag['data'].lower() not in i.attrs: continue
				else: t = i
			if type(t) == ResultSet: continue
			if tag['data'] == "": data = t.text
			else:
				try:
					data = t.get(tag['data'].lower())
				except:
					continue
			if tag['save'] == True:
				saved[tag['name']] = data
	if "theme-color" not in saved:
		#saved["theme-color"]
		sheets = [
		    cssutils.parseStyle(styletag.string)
		    for styletag in soup.findAll('style') if styletag.string
		]
		for styletag in soup.findAll('link', type='text/css'):
				CSSData=GetData(styletag.href, "")
				sheets.append(cssutils.parseStyle(CSSData))
		print(sheets)
	else:print(saved["theme-color"])
	unfiltered_img=soup.findAll('img')
	safety = 1
	images = []
	videos = []
	if len(unfiltered_img)>0:
		for img in unfiltered_img:
			src = urljoin(website, img.get('src'))
			if src==website:continue
			a = image_detector(src)
			safety += a
			if a < 0.2:
				images.append(src)
		videos.extend(
		    urljoin(website, vid.get('src')) for vid in soup.findAll('video'))
		safety=safety/len(unfiltered_img)
		if safety>0.5:
			print("UNSAFE")
			return "UNSAFE: Inappropiate images dectected; contact @./hg0428#6088 on discord if you believe this is a mistake."
	saved["safety"] = safety
	saved["images"] = images
	saved["videos"] = videos
	saved["time-of-indexing"] = time.time()
	saved["title"] = getTitle(soup, up)
	saved["text"] = " ".join(GetText(f_data).split())
	saved["favicon"] = getFavicon(soup, website)
	saved["addr"] = up.netloc
	print(len(saved) - 3)
	return saved, soup


#with open('apple.txt', 'w+') as outfile:
#	 json.dump(GetInfo("https://apple.com/"), outfile)
#GetInfo("https://replit.com/")
#GetInfo("https://httpimgs.compilingcoder.repl.co/")
