#https://deepai.org/machine-learning-model/nsfw-detector
from urllib3 import PoolManager
import html_text

http = PoolManager()
try:
	from BeautifulSoup import BeautifulSoup, ResultSet
except ImportError:
	from bs4 import BeautifulSoup, ResultSet
from urllib.parse import urljoin, urlparse
import json
from bs4.element import Comment
import time
import requests
import extruct


def extract_metadata(text, up):
	return extruct.extract(text,
	                       base_url=up.netloc,
	                       uniform=True,
	                       syntaxes=['json-ld'])


metaDataTypes = {
    "Organization": ["name", "url"],
    "VideoGame": ["name", "url", "author", "genre", "aggregateRating", "image"]
}


def parse_metadata(text, up):
	print("start")
	Result={}
	metadata = extract_metadata(text, up)['json-ld']
	print(metadata)
	for md in metadata:
		mdtype=md["@type"]
		if mdtype in metaDataTypes: 
			for k,v in md.items():
				if k in metaDataTypes[mdtype]:
					Result[k]=v
	print(Result)
	return Result
					
				


def image_detector(src):
	r = requests.post(
	    "https://api.deepai.org/api/nsfw-detector",
	    data={
	        'image': src,
	    },
	    headers={'api-key': 'd0b362a7-84c8-48f4-b7c4-a6ffb078972a'})
	j = r.json()
	#print(type(j), j)
	if 'err' in j: return 0.2
	return j["output"]["nsfw_score"]


helper = json.load(open("helper.json"))


def GetData(url):
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
	#except:
	#  return False
	content_type = response.headers.get('Content-Type').lower()
	if "html" not in content_type: return False
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
	a = html_text.extract_text(data, guess_layout=False)
	return a


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
	favicon = urljoin(site, icon_link["href"])
	return favicon


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
				if tag['data'] not in i.attrs: continue
				else: t = i
			if type(t) == ResultSet: continue
			if tag['data'] == "": data = t.text
			else:
				try:
					data = t.get(tag['data'])
				except:
					continue
			if tag['save'] == True:
				saved[tag['name']] = data
	unfiltered_img = soup.findAll('img')
	safety = 0
	images = []
	videos = []
	if len(unfiltered_img) > 0:
		for img in unfiltered_img:
			src = urljoin(website, img.get('src'))
			if src == website: continue
			a = image_detector(src)
			safety += a
			if a < 0.3:
				images.append(src)
		for vid in soup.findAll('video'):
			videos.append(urljoin(website, vid.get('src')))
		safety = safety / len(unfiltered_img)
		if safety > 0.5:
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
	saved["metaData"]= parse_metadata(f_data, up)
	return saved, soup


#with open('apple.txt', 'w+') as outfile:
#   json.dump(, outfile)
#GetInfo("https://replit.com/")
#GetInfo("https://httpimgs.compilingcoder.repl.co/")
#GetInfo("https://nomanssky.com/",urlparse("https://nomanssky.com/"))

