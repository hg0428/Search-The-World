from os import path as ospath, listdir
from re import findall
from sys import getsizeof
import time

DATA = {}
MAX_SPACE = 4000000000  # in bytes
#old adverage: 0.8
timeadverage = 0
iters=0
stopwords = open("stopwords.txt").read().split()
open("stopwords.txt", "w").write(" ".join(stopwords))


def getItems(text):
    try:
        items = dict([tuple(i.split(":")) for i in text.split(";")])
    except:
        return False
    return items


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


def hascommon(i1, i2):
    for i1s in i1:
        if i1s in i2: return i1s
    return False


def no_stop_words(words):
    global stopwords
    content = [w for w in words if w.lower() in stopwords]
    return ' '.join(content)


def CLEAN(text):
    text = text.lower()
    return "".join([
        i for i in text if i in ''.join(list(map(chr, range(97, 123)))) + " "
    ])


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
    t = time.time()
    global iters, timeadverage
    f = data["file"]
    refs = len(data["ref"])
    score = 0
    contents = data["saved_text"]
    if contents == None:
        print("slow")  #keep this!
        contents = open(f).read().split("\n")[1]
    favicon = data["favicon"]
    l = {
        data["title"].lower(): 20,
        data["addr"].lower(): 25,
        no_stop_words(words): 1.2,
        contents: 1,
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
    timeadverage+=time.time()-t
    iters+=1
    return score, des, link, data["title"], favicon


def searchall(q="t"):
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


getsites()
adverageoftheadverage=0
number=5
adverageofthetotal=0
for i in range(number):
  searchall()
  adverageoftheadverage+=timeadverage/iters
  adverageofthetotal+=timeadverage

print(adverageoftheadverage/number, adverageofthetotal/number)