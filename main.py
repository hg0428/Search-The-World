import htmlparse
from toolsys import getsites, index, searchall, update_all_sites, getwords, parseText
from os import listdir, remove
from flask import request, render_template, Flask, send_file
import concurrent.futures
from autocorrect import Speller
from time import time
import json
## https://yoast.com/what-is-structured-data/
## https://schema.org/
## https://yoast.com/what-is-structured-data/
## https://gist.github.com/lancejpollard/1978404
## !^^!Use Those!^^!
##REVERT TEST

#sitemap datetime format: YYYY-MM-DDThh:mm:ssTZD (eg 2021-05-18T13:58:54-7:00)
def fix(f="htmlparse.py"):
	r=open(f, "r").read().replace("  ", "	")
	open(f, "w+").write(r)
	print("DONE!")
fix()
#Also make better descriptions!
spell = Speller(fast=True)
getsites()

app = Flask("Search The World")
from flask_compress import Compress


#def replacefromto(string, start, end, replacement):
#    return f"{string[:start]}{replacement}{string[end:]}"


COMPRESS_MIMETYPES = [
    'text/html', 'text/css', 'application/json', 'text/js', 'img/png'
]
COMPRESS_LEVEL = 6
COMPRESS_MIN_SIZE = 500
Compress(app)
searches = listdir("searches/")
for f in searches:
	remove(f"searches/{f}")
searches = []


#[pagenum * amount:pagenum * amount + amount]
def makejson(q):
    t = time()
    if q not in searches:
        code = searchall(q)

        open(f"searches/{q}", "w+").write(str(code))
        searches.append(q)
    else:
        code = eval(open(f"searches/{q}").read())
    jsondict = {
        "ResultCount": len(code),
        "Time": time() - t,
        "Keywords":list(getwords(q)),
        "Information": {
            "Main": {},
            "Descriptions": {}
        },
        "Results": {}
    }
    for i in code:
        d = code[i]
        jsondict["Results"][d["link"]] = code[i]

    return jsondict


@app.route("/", methods=["GET", "HEAD"])
def home():
	    #htmlparse.GetInfo("https://Search-The-World.hg0428.repl.co")
	if "q" not in request.args:
		return render_template("home.html")
	pp = 15
	pagenum = 0
	if "pp" in request.args and request.args["pp"] != "0":
	    try:
	        pp = int(request.args["pp"])
	    except:pass
	if "page" in request.args:
	    try:
	        pagenum = int(request.args["page"])
	    except:pass
	q = request.args["q"].lower().replace("/", "")
	if q == "": return render_template("home.html")
	print("Searching for: ", q)
	code = makejson(q)
	results = dict(
	    list(code["Results"].items())[pagenum * pp:pagenum * pp + pp])
	roundup = lambda x: int(x) if x == int(x) else int(x) + 1
	return render_template("search.html",
	                       code=code,
	                       results=results,
	                       search=q,
	                       word=spell(q),
	                       pagenum=pagenum,
	                       len=len,
	                       perpage=pp,
	                       roundup=roundup,
	                       round=round, parseText=parseText)


@app.route("/api")
def api():
    if 'q' in request.args:
        q = request.args["q"].lower().replace("/", "")
        if q == "": return render_template("api.html")
        return json.dumps(makejson(q))
    if "part" in request.args and request.args["part"] == "specs":
        return render_template("apispecs.html")
    else:
        return render_template("api.html")


@app.route("/static/css/home.css")
def css():
    return send_file("static/home.css")


@app.route("/static/img/searchicon.png")
def imgsi():
    return send_file("static/searchicon.png")


@app.route("/static/img/searchiconinvert.png")
def imgsiinverted():
    return send_file("static/searchiconinvert.png")


@app.route("/static/js/page.js")
def pagejs():
    return send_file("static/page.js")


@app.route("/static/img/lt.png")
def imglt():
    return send_file("static/lt.png")


@app.route("/apple-touch-icon-precomposed.png")
@app.route("/apple-touch-icon.png")
@app.route("/favicon.ico")
@app.route("/static/img/favicon.ico")
def fav():
    return send_file("static/favicon.ico")


@app.route("/index", methods=["GET", "POST"])
def index_site_page():
	if request.method != "POST":
		return render_template("index.html")
	site = request.form["site"]
	if "://" not in site:
	    note = "<h2>Please include protocol and / at the end</h2>"
	else:
	    note = '<h2>DONE!</h1> <p class="des">For now this site was listed as anonymous. Login and site statistics will come in a future version. </p>'
	    with concurrent.futures.ThreadPoolExecutor() as executor:
	        future = executor.submit(index, site)
	        value = future.result()
	    if value == False:
	        note = "<h2>Failed: invalid or inactive site</h2>"
	    elif type(value)==str:note=value
	return render_template("index.html", note=note)


@app.route("/sitemap.xml")
def sitemap():
    return send_file("templates/sitemap.xml")


@app.route("/static/js/darkmode.js")
def darkmodejs():
    return send_file("static/darkmode.js")


@app.route("/static/css/api.css")
def apicss():
    return send_file("static/api.css")
@app.route("/static/css/Home-beta.css")
def betacss():
    return send_file("static/Home-beta.css")


@app.route("/static/css/darkmode.css")
def darkcss():
    return send_file("static/darkmode.css")


@app.route("/Policies/termsofservice")
def termsofservice():
    return render_template("Policies/termsofservice.html")


@app.route("/Policies/privacy")
def privacypolicy():
    return render_template("Policies/privacy.html")


@app.route("/robots.txt")
def robots():
    return send_file("static/robots.txt")


@app.after_request
def add_headers(resp):
    resp.headers[
        "Content-Security-Policy"] = "script-src 'self' https://search-the-world.hg0428.repl.co"
    #resp.headers["X-Frame-Options"]="DENY"
    resp.headers["Expires"]="4000"
    resp.headers["Cache-Control"]="max-age=4000"
    resp.headers["Pragma"]="no-cache"
    resp.headers["X-Content-Type-Options"]="nosniff"
    resp.headers["Content-Security-Policy"]="base-uri 'self'"
    return resp


#print(index("https://replit.com"))

#update_all_sites()
#getsites()
app.jinja_env.cache = {}
app.run("0.0.0.0", 8080)
