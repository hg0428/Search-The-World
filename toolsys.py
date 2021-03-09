import urllib
from urllib.parse import urlparse as parseurl, urljoin
import os
from nltk.corpus import stopwords as stopwords
try:
    stopwords = stopwords.words('english')
except:
    import nltk
    nltk.download("stopwords")
    stopwords = stopwords.words('english')
from bs4 import BeautifulSoup as bs
import re
DATA = {}
from web_crawler import *

# Add reference points for all parent domains
similar = {"-": " "}


def CLEAN(text):
    for s in similar:
        r = similar[s]
        text = text.replace(s, r)
    return "".join([
        i for i in text if i in ''.join(list(map(chr, range(97, 123)))) + " "
    ])


def getwords(s):
    return re.findall(r"[\w']+", s)


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
                newtext += start + s + end
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
    content = [w for w in words if w.lower() in stopwords]
    return ' '.join(content)


def hascommon(i1, i2):
    for i1s in i1:
        if i1s in i2: return i1s
    return False


def getsites(path="indexed/"):
    try:
        refs = int(open(path + "refs"))
    except:
        refs = 1
    for i in os.listdir(path):
        if os.path.isfile(path + i) and i.startswith(":"):
            DATA[open(path + i).readlines()[0].split(";")[0].split(":")[1]] = {
                "file": path + i,
                "ref": refs
            }
        elif not os.path.isfile(path + i):
            getsites(path + i + "/")


class Result:
    def __init__(self, urlp, title, text, path, soup):
        self.soup = soup
        self.urlp = urlp
        self.url = urllib.parse.urlunparse(self.urlp)
        self.title = title.replace('\n', '').replace(":", "–").replace(";", "")
        self.text = text.replace("\n",
                                 "").replace("<", "&lt;").replace(">", "&lt;")
        self.path = path
        self.images = []
        self.formatted = ""
        if urlp.path == "": self.urlpath = "/"
        else: self.urlpath = urlp.path
        if not self.urlpath.endswith("/"): self.urlpath += "/"
        self.getreflinks()

    def format(self):
        self.formatted = f"title:{self.title};addr:{self.urlp.netloc}\n{self.text}\n{getFavicon(self.soup, self.url)}"
        #print("Formatted:",self.formatted)
    def getreflinks(self):
        for l in self.soup.find_all('a'):
            l = l.get("href")
            up = parseurl(urljoin(self.urlp.geturl(), l))
            folder = up.netloc.split(".")
            folder.reverse()
            path = "indexed/" + '/'.join(folder) + "/"
            if not os.path.exists(path): continue
            try:
                r = int(open(path + "info").read())
            except:
                r = 1
            r += 1
            open(path + "refs", "w+").write(str(r))

    def write(self):
        self.format()
        return open(self.path, "w+").write(self.formatted)

    def writeimages(self):
        images = []
        for i in self.images:
            if not i.startswith(self.urlp.scheme) and not i.startswith("/"):
                i = self.urlp.scheme + "://" + self.urlp.netloc + self.urlpath + i
            elif i.startswith("/"):
                i = self.urlp.scheme + "://" + self.urlp.netloc + i
            images.append(i)
        self.images = images
        return open('/'.join(self.path.split("/")[:-1]) + "/images",
                    "a+").write("\n".join(images))


def index(url):
    urlp = parseurl(url)
    url = urlp.scheme + "://" + urlp.netloc + urlp.path
    if urlp.path == "": urlpath = "/"
    else: urlpath = urlp.path
    folder = urlp.netloc.split(".")
    folder.reverse()
    path = "indexed/" + '/'.join(folder) + "/"
    f = getData(url)
    if f == False: return False
    try:
        os.makedirs(path)
    except:
        pass
    soup = bs(f, features="html5lib")
    title = getTitle(soup, urlp)
    text = str(GetText(soup))
    if text == "": return
    r = Result(urlp, title, text, path + urlpath.replace("/", ":"), soup)
    r.write()
    print("Indexed:", url)
    return True


def makedescription(text, item):
    amount = 200
    des = text.partition(item)
    des = des[0][des[0].rfind(' ', 0,
                              len(des[0]) - amount):] + des[1] + des[2][
                                  des[2].rfind(' ', 0,
                                               len(des[2]) - amount):]

    return des


def getscore(f, refs, query, words):
    score = 0
    contents = open(f).read().split("\n")
    if len(contents) == 3: favicon = contents[2]
    else: favicon = ""
    items = getItems(contents[0])
    contents = contents[1]
    l = {
        items["title"].lower(): 10,
        items["addr"].lower(): 5,
        no_stop_words(words): 1,
        contents.lower(): 0.5,
        CLEAN(contents.lower()): 0.3
    }
    contained = []
    for i in l:
        m = l[i]
        score += i.lower().count(query) * 5 * m
        for w in words:
            score += i.lower().count(w) * m
            if score >= 1: contained.append(w)
    score *= len(contained)
    if query in contents:
        des = makedescription(contents, query)
    else:
        hc = hascommon(words, contents)
        if hc != False:
            des = makedescription(contents, hc)
        elif score <= 0:
            return False
        else:
            des = contents[:300]
    des = parseText(des, words + [query])
    link = "https://" + items["addr"] + f.split("/")[-1].replace(":", "/")
    if score > 0:
        score += refs**2
        return score, des, link, items["title"], favicon
    else:
        print("???")
        return False


def searchall(q, amount=15, pagenum=0):
    words = list(dict.fromkeys(getwords(q)).keys())
    codedict = {}
    l = {}
    for s in DATA:
        f = DATA[s]['file']
        refs = DATA[s]['ref']
        r = getscore(f, refs, q, words)
        if r == False: continue
        score, des, link, title, fav = r
        l[score] = {
            "des": des,
            "score": score,
            "title": title,
            "url": link,
            "favicon": fav
        }
    for key in sorted(l, reverse=True)[pagenum * amount:pagenum * amount +
                                       amount]:
        codedict[key] = l[key]
    return codedict, len(l)

def update_all_sites():
  for d in DATA:
    print(d)
update_all_sites()