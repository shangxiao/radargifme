import urllib
import urllib2
import re
from PIL import Image
from flask import Flask, make_response
from images2gif import writeGif
app = Flask(__name__)

radar_url = 'http://www.bom.gov.au/products/IDR023.loop.shtml'
background_image_url = 'http://www.bom.gov.au/products/radar_transparencies/IDR023.background.png'
image_regex = re.compile(r'theImageNames\[\d\]')
url_regex = re.compile(r'http.*png')

@app.route('/')
def gifme():
    urllib.urlretrieve(background_image_url, 'background.png')

    req = urllib2.urlopen(radar_url)
    lines = req.readlines()
    urls = []
    for line in lines:
        if image_regex.search(line):
            m = url_regex.search(line)
            url = m.group(0)
            urls.append(url)

    background = Image.open('background.png')

    frames = []
    for url in urls:
        urllib.urlretrieve(url, 'foreground.png')
        foreground = Image.open('foreground.png')
        bg = Image.new("RGBA", background.size)
        bg.paste(background)
        fg = Image.new('RGBA', foreground.size)
        fg.paste(foreground)
        bg.paste(fg, box=(0, 0), mask=fg)
        frames.append(bg.copy())

    writeGif('derp.gif', frames, duration=0.5)


    f = open('derp.gif', 'rb')
    ba = bytearray(f.read())
    response = make_response(ba)
    response.headers['Content-Type'] = 'image/gif'
    return response

if __name__ == "__main__":
    app.run()
    # gifme()
