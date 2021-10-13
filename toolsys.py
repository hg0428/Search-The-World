from urllib.parse import urlparse as parseurl, urljoin, urlunparse
import time
from os import listdir, path as ospath, makedirs
#from bs4 import BeautifulSoup as bs
from re import findall
import htmlparse
import json

DATA = {}
from sys import setswitchinterval, getsizeof
from htmlparse import GetInfo

setswitchinterval(9999999)
similar = {"-": " "}
stopwords = open("stopwords.txt").read().split()
MAX_SPACE = 4000000000  # in bytes


def make_path(netloc, p="indexed/"):
	folder = netloc.split(".")
	folder.reverse()
	path = p + '/'.join(folder) + "/"
	return path


def get_sub_domains(url):
	if "://" in url:
		urlp = parseurl(url)
		urlsplit = urlp.netloc.split(".")
	else:
		urlsplit = url.split(".")
	l = []
	if len(urlsplit) < 3: return l
	for _ in urlsplit:
		urlsplit = urlsplit[1:]
		l.append(".".join(urlsplit))
		if len(urlsplit) < 3:
			return l


def CLEAN(text):
	text = text.lower()
	for s in similar:
		r = similar[s]
		text = text.replace(s, r)
	return "".join([
	    i for i in text if i in ''.join(list(map(chr, range(97, 123)))) + " "
	])


def getwords(s):
	return tuple(set(findall(r"[\w']+", s)))


def parseText(text, things):
	start = "<strong>"
	end = "</strong>"
	for item in things:
		item = CLEAN(item.lower())
		newtext = ""
		s = ""
		do = True
		for i in text:
			s += i
			if s == start:
				do = False
			if s.endswith(end):
				do = True
				newtext += s
				s = ""
			if (not item.startswith(CLEAN(s.lower()))
			    and not start.startswith(s)) and do == True:
				newtext += s
				s = ""
			if item == CLEAN(
			    s.lower()) and not start.startswith(s) and do == True:
				newtext += f"{start}{s}{end}"
				s = ""
		newtext += s
		text = newtext
	return newtext


def getItems(text):
	try:
		items = dict([tuple(i.split(":")) for i in text.split(";")])
	except:
		return False
	return items


def no_stop_words(words):
	global stopwords
	content = [w for w in words if w.lower() not in stopwords]
	return content


def hascommon(i1, i2):
	a = []
	for i1s in i1:
		if i1s in i2: a.append(i1s)
	if a == []:
		return False
	else:
		return a


def getsites(path="indexed/"):
	try:
		refs = open(f"{path}refs").read().split("\n")
	except:
		refs = [path]
	for i in listdir(path):
		if ospath.isfile(path + i) and i.startswith(":") and getsizeof(
		    vars()) < MAX_SPACE:
			text = json.load(open(path + i))
			#saves in memory if it has space, else it tells it to retreve it from files when needed
			test = {"file": path + i, "ref": refs}
			test.update(text)
			DATA[path + i] = test

		elif not ospath.isfile(path + i):
			getsites(path + i + "/")


class Result:
	def __init__(self, urlp, link, path, soup):
		self.soup, self.urlp, self.path, self.formatted = soup, urlp, path, ""
		self.link = link
		self.url = urlunparse(self.urlp)
		if urlp.path == "": self.urlpath = "/"
		else: self.urlpath = urlp.path
		if not self.urlpath.endswith("/"): self.urlpath += "/"
		self.getreflinks()

	def getreflinks(self):
		for up in get_sub_domains(self.url):
			up = parseurl(up.lower())
			path = make_path(up.netloc)
			if not ospath.exists(path):
				try:
					makedirs(path)
				except:
					pass
			try:
				r = open(path + "refs").read().split("\n")
				if self.url not in r:
					r.append(self.url)
			except:
				r = [self.url]
			open(path + "refs", "w+").write('\n'.join(r))
		for l in self.soup.find_all('a'):
			l = l.get("href")
			if l == None: continue
			up = parseurl(urljoin(self.urlp.geturl().lower(), l.lower()))
			path = make_path(up.netloc)
			if not ospath.exists(path):
				try:
					makedirs(path)
				except:
					pass
			try:
				r = open(path + "refs").read().split("\n")
				if self.url not in r:
					r.append(self.url)
			except:
				r = [self.url]
			open(path + "refs", "w+").write('\n'.join(r))

	def write(self, info):
		return json.dump(info, open(self.path.lower(), "w+"))


def index(url):
	urlp = parseurl(url)
	url = urlp.scheme + "://" + urlp.netloc + urlp.path
	if urlp.path == "": urlpath = "/"
	else: urlpath = urlp.path
	path = make_path(urlp.netloc)
	A = htmlparse.GetInfo(url, urlp)
	if A == False: return False
	if type(A)==str:return A
	data, soup = A
	if data == False:
		print("Error:", url)
		return False
	try:
		makedirs(path)
	except:
		pass
	r = Result(urlp, url, path + urlpath.replace("/", ":"), soup)
	r.write(data)
	print("Indexed:", url)
	return True


def CreateDescription(text, keywords):
	keywords = no_stop_words(keywords)
	totallength = 325
	num = 0
	d = {}
	for i in text:
		key = 0
		des = text[num:totallength + num]
		#print(des.find(" ") - des.rfind(" "))
		des = des[des.find(" "):des.rfind(" ")]
		#print(des)
		for word in keywords:
			key += des.lower().count(word)
		if key > 0:
			d[key] = (num + des.find(" "), num + des.rfind(" "))
		num += 1
	d = sorted(d.items(), reverse=True)
	#print(d)
	for k, v in d:
		#print(k, v)
		return text[v[0]:v[1]]


def getscore(data, query, words):
	score = 0
	description = data["description"]
	text = data["text"]
	link = data["addr"]
	title = data["title"]
	source = {
	    link.lower(): 4,
	    title.lower(): 3,
	    description.lower(): 2,
	    text.lower(): 1
	}
	for word in words:
		for item in data:
			if type(data[item]) != str: continue
			value = data[item]
			score += value.count(query)
			score += value.count(word)
		for s, v in source.items():
			score += s.count(word) * v
	for s, v in source.items():
		score += s.count(query) * v * 4
	if score == 0:
		return False
	metascore = 0
	if title != link: metascore += 2.5
	if description != "": metascore += 0.5
	if len(text) > 250: metascore + 1
	metascore *= len(data)
	des=None
	if query not in description.lower() and query not in title.lower() and query not in link.lower():
		des = CreateDescription(text, words)
	if des==None or des=="":
		if description=="":des=text[:250]
		else:des=description[:350]
	score+=metascore*len(data["ref"])
	#print(score + metascore, title)
	return score + metascore, des


def searchall(q):
	splitq = q.split()
	words = []
	for word in splitq:
		if word not in words: words.append(word)
	codedict = {}
	l = {}
	for s in DATA:
		data = DATA[s]
		r=getscore(data, q, words)
		if r == False: continue
		score, des = r
		l[data["link"]] = {
		    "description": des,
		    "score": score,
		    "title": data["title"],
		    "link": data["link"],
		    "favicon": data["favicon"],
		    "images": data['images'],
		    "data":data
		}
	for key, value in sorted(l.items(),
	                         reverse=True,
	                         key=lambda k: k[1]["score"]):
		codedict[key] = value
	del q, l

	return codedict


def update_all_sites(iters=3, crawl=False):
	print("Starting Update...")
	i = 0
	while i < iters:
		print(f"Iter {i+1} started.")
		for d in DATA:
			index(DATA[d]["link"])
		print(f"Iter {i+1} complete!\n")
		time.sleep(10)
		i += 1
	print("Updated!")


#Updates every site in the data base. This is usefull for when I update the format.
#Using multiple iterations it becomes waking repl proof
