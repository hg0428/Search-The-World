from toolsys import *
from flask import *
from autocorrect import Speller
import time
spell = Speller(fast=True)
getsites()
app = Flask("Search The World")
indev = False


@app.route("/", methods=["GET", "HEAD"])
def home():
    if indev == True and "understand" not in request.args:
        return render_template("indev.html")
    if "q" in request.args:
        pp = 15
        pagenum = 0
        if "pp" in request.args and request.args["pp"] != "0":
            try:
                pp = int(request.args["pp"])
            except:
                pass
        if "page" in request.args:
            try:
                pagenum = int(request.args["page"])
            except:
                pass
        t = time.time()
        q = request.args["q"].lower()
        if q == "": return render_template("home.html")
        q = CLEAN(q)
        print("Searching for: ", q)
        r, a = searchall(q, pp, pagenum)
        roundup = lambda x: x if x == int(x) else int(x) + 1
        return render_template("search.html",
                               code=r,
                               search=q,
                               word=spell(q),
                               pagenum=pagenum,
                               total=a,
                               perpage=pp,
                               roundup=roundup,
                               time=time.time() - t,
                               round=round)
    else:
        return render_template("home.html")


@app.route("/static/css/home.css")
def css():
    return send_file("static/home.css")


@app.route("/static/img/searchicon.png")
def imgsi():
    return send_file("static/searchicon.png")


@app.route("/static/js/page.js")
def pagejs():
    return send_file("static/page.js")


@app.route("/static/img/lt.svg")
def imglt():
    return send_file("static/lt.svg")


@app.route("/apple-touch-icon-precomposed.png")
@app.route("/apple-touch-icon.png")
@app.route("/favicon.ico")
def fav():
    return send_file("static/favicon.ico")


@app.route("/index", methods=["GET", "POST"])
def index_site_page():
    if request.method == "POST":
        site = request.form["site"]
        if "://" not in site:
            note = "<h2>Please include protocol and / at the end</h2>"
        else:
            note = '<h2>DONE!</h1> <p class="des">For now this site was listed as anonymous. Login and site statistics will come in a future version. </p>'
            if index(site) == False:
                note = "<h2>Failed: invalid or inactive site</h2>"

        return render_template("index.html", note=note)
    else:
        return render_template("index.html")


app.run("0.0.0.0", 8080)
