from urllib3 import PoolManager
from urllib.parse import urlparse as parseurl, urljoin, urlencode
from bs4 import BeautifulSoup as bs
import time
from bs4.element import Comment
http = PoolManager()
import html_text

def save(f, data: list, sep: str):
    open(f, "w+").write(sep.join(data))


def tag_visible(element):
    if element.parent.name in [
            'style', 'script', 'head', 'meta', "[document]", "div"
    ]:
        return False
    if isinstance(element, Comment):
        return False
    return True


def GetText(data):
	return html_text.extract_text(data, guess_layout=False)


def getData(url):
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
  f = response.data.decode()
  #except:
  #  return False
  content_type = response.headers.get('Content-Type').lower()
  if "html" not in content_type: return False
  if response.status != 200: return False
  return f

def getTitle(soup, urlp):
    try:
        title = str(soup.title.string)
    except:
        title = urlp.netloc
    return title


#DONE = [i for i in open("done").read().split("\n") if i != ""]


def getFavicon(soup, site):
    icon_link = soup.find("link", rel="shortcut icon")
    if icon_link is None:
        icon_link = soup.find("link", rel="icon")
    if icon_link is None:
        return urljoin(site, '/favicon.ico')
    favicon = urljoin(site, icon_link["href"])
    return favicon


def send(link, data, soup, urlp):
    data = urlencode({
        "link": link,
        "about": GetText(soup),
        "favicon": getFavicon(soup, link),
        "title": getTitle(soup, urlp)
    }).encode()
    req = http.request("POST",'https://regularwordydisc.generationxcode.repl.co/here',
                  data=data,
                  headers={"Identity": "Projxon Web Crawler 01"
                           })  # this will make the method "POST"

    try:
        eq.read()
    except:
        pass


def crawl(starturl, full=False, todo=lambda x: ""):
    if starturl in DONE: return False
    DONE.append(starturl)
    print(starturl)
    urlp = parseurl(starturl)
    f = getData(starturl)
    if f == False: return f
    soup = bs(f, features="html5lib")
    send(starturl, f, soup, urlp)
    links = soup.find_all('a')
    for link in links:
        link = link.get('href')
        if link is None: continue
        if link.startswith("/"): link = urljoin(starturl, link)
        if full == True and link not in DONE: crawl(link)
    if full == True:
        for link in links:
            if link not in DONE:
                crawl(urljoin(starturl, link.get('href')), full=True)


