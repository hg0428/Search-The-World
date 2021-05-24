from html.parser import HTMLParser
import web_crawler

class MyHTMLParser(HTMLParser):
    def __init__(self):
        self.tags = []
        super().__init__()

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_endtag(self, tag):
        if self.tags[-1][0] == tag:
            #print("Tag:", tag)
            #print("Attrs:", tags[-1][1])
            #print("Data:", tagdata)
            #print("\n")
            self.tags = self.tags[:-1]
        else:
            pass  #print(
            #    f"Syntax Error on line {self.getpos()}: tag {self.tag} does not match {self.tags[-1][0]}\n"
            #)

    def handle_data(self, data):
        pass  #print("Encountered some data:", data)
        #print("\n")

    def handle_startendtag(self, tag, attrs):
        pass
        #print("Start and End tag:", tag)
        #print("Attrs:", dict(attrs))
        #print("\n")


def finishthejob(website):
    pass


h = MyHTMLParser()
h.feed(open("test").read())
