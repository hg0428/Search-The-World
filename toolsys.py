from urllib.parse import urlparse as parseurl, urljoin, urlunparse
import time
from os import listdir, path as ospath, makedirs
from bs4 import BeautifulSoup as bs
from re import findall

DATA = {}
from web_crawler import getData, getTitle, getFavicon, GetText
from sys import setswitchinterval, getsizeof

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
    return set(findall(r"[\w']+", s))


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
                newtext += f"{start} {s} {end}"
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
        refs = open(f"{path}refs").read().split("\n")
    except:
        refs = [path]
    for i in listdir(path):
        if ospath.isfile(path + i) and i.startswith(":"):
            saved_text = None
            text = open(path + i).read().split("\n")
            items = getItems(text[0])
            if len(text) == 3: favicon = text[2]
            else: favicon = ""
            if getsizeof(vars()) < MAX_SPACE:
                saved_text = text[1]
            #saves in memory if it has space, else it tells it to retreve it from files when needed
            DATA[items["title"]] = {
                "file":
                path + i,
                "title":
                items["title"],
                "ref":
                refs,
                "link":
                "https://" + items["addr"] +
                i.split("/")[-1].replace(":", "/"),
                "addr":
                items["addr"],
                "favicon":
                favicon,
                "saved_text":
                saved_text
            }
        elif not ospath.isfile(path + i):
            getsites(path + i + "/")


class Result:
    def __init__(self, urlp, title, text, path, soup):
        self.soup, self.urlp, self.path, self.formatted = soup, urlp, path, ""
        self.url = urlunparse(self.urlp)
        self.title = title.replace('\n', '').replace(":", "–").replace(";", "")
        self.text = text.replace("\n",
                                 "").replace("<", "&lt;").replace(">", "&lt;")
        if urlp.path == "": self.urlpath = "/"
        else: self.urlpath = urlp.path
        if not self.urlpath.endswith("/"): self.urlpath += "/"
        self.getreflinks()

    def format(self):
        self.formatted = f"title:{self.title};addr:{self.urlp.netloc}\n{self.text}\n{getFavicon(self.soup, self.url)}"
        #print("Formatted:",self.formatted)
    def getreflinks(self):
        for up in get_sub_domains(self.url):
            up = parseurl(up)
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
            up = parseurl(urljoin(self.urlp.geturl(), l))
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

    def write(self):
        self.format()
        return open(self.path.lower(), "w+").write(self.formatted)


def index(url):
    urlp = parseurl(url)
    url = urlp.scheme + "://" + urlp.netloc + urlp.path
    if urlp.path == "": urlpath = "/"
    else: urlpath = urlp.path
    path = make_path(urlp.netloc)
    f = getData(url)
    #f= ' '.join(str(f).split())
    if f == False:
        print("Error:", url)
        return False
    try:
        makedirs(path)
    except:
        pass
    soup = bs(f, features="html5lib")
    title = getTitle(soup, urlp)
    text = str(GetText(soup))
    if text == "": return False
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
    #makes the description
    return des


#scores each site
def getscore(data, query, words):
    f = data["file"]
    refs = len(data["ref"])
    score = 0
    contents = data["saved_text"]
    if contents == None:
        print("slow") #keep this!
        contents = open(f).read().split("\n")[1]
    favicon = data["favicon"]
    l = {
        data["title"].lower(): 20,
        data["addr"].lower(): 25,
        no_stop_words(words): 1.2,
        contents:1,
        contents.lower(): 0.5,
        CLEAN(contents.lower()): 0.3
    }
    contained = []
    numberofwordsinsite = len(contents.split())
    for i in l:
        m = l[i]
        density = i.split().count(query) / numberofwordsinsite
        score += i.count(query) * 5 * m * density
        score += i.split().count(query) * m * 10 * density
        for w in words:
            density = i.split().count(w) / numberofwordsinsite
            score += i.split().count(w) * m * 5 * density
            score += i.count(w) * m * density
            if score >= 1: contained.append(w)
    score *= len(contained)
    if query in CLEAN(contents):
        des = makedescription(contents, query)
    else:
        hc = hascommon(words, contents)
        if hc != False:
            des = makedescription(contents, hc)
        elif score <= 0:
            return False
        else:
            des = contents[:400]
    des = parseText(des, {query} | words)
    link = data["link"]
    a = (len(contents) - (score * 5)) / 25
    score -= a * (a > 0)
    if score < 0:
        score = contents.lower().count(query)
        score += refs**2
    score += refs
    return score, des, link, data["title"], favicon


def searchall(q):
    words = getwords(q)
    codedict = {}
    l = {}
    for s in DATA:
        r = getscore(DATA[s], q, words)
        if r == False: continue
        score, des, link, title, fav = r
        l[score] = {
            "des": des,
            "score": score,
            "title": title,
            "url": link,
            "favicon": fav
        }
    for key in sorted(l, reverse=True):
        codedict[key] = l[key]
    del words, q, l
    return codedict


def update_all_sites(iters=3):
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
