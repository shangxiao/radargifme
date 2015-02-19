import urllib
import urllib2
import re
from PIL import Image
from flask import Flask, make_response
from images2gif import writeGif
app = Flask(__name__)

radar_url = 'http://www.bom.gov.au/products/IDR023.loop.shtml'
background_image_url = 'http://www.bom.gov.au/products/radar_transparencies/IDR023.background.png'
topography_url = 'http://www.bom.gov.au/products/radar_transparencies/IDR023.topography.png'
range_url = 'http://www.bom.gov.au/products/radar_transparencies/IDR023.range.png'
locations_url = 'http://www.bom.gov.au/products/radar_transparencies/IDR023.locations.png'
legend_url = 'http://www.bom.gov.au/products/radar_transparencies/IDR.legend.0.png'

urllib.urlretrieve(background_image_url, 'background.png')
urllib.urlretrieve(topography_url, 'topography.png')
urllib.urlretrieve(range_url, 'range.png')
urllib.urlretrieve(locations_url, 'locations.png')
urllib.urlretrieve(legend_url, 'legend.png')

legend = Image.open('legend.png').convert('RGBA')
background = Image.open('background.png').convert('RGBA')
topography = Image.open('topography.png').convert('RGBA')
range_ = Image.open('range.png').convert('RGBA')
locations = Image.open('locations.png').convert('RGBA')

image_regex = re.compile(r'theImageNames\[\d\]')
url_regex = re.compile(r'http.*png')

@app.route('/')
@app.route('/radar.gif')
def gifme():
    req = urllib2.urlopen(radar_url)
    lines = req.readlines()
    urls = []
    for line in lines:
        if image_regex.search(line):
            m = url_regex.search(line)
            url = m.group(0)
            urls.append(url)


    frames = []
    for url in urls:
        bg = Image.new("RGBA", legend.size)
        box = (0, 0) + background.size
        bg.paste(background, box=box)
        bg.paste(topography, box=box, mask=topography)

        urllib.urlretrieve(url, 'foreground.png')
        fg = Image.open('foreground.png').convert('RGBA')
        bg.paste(fg, box=box, mask=fg)

        bg.paste(range_, box=box, mask=range_)
        bg.paste(locations, box=box, mask=locations)
        bg.paste(legend, mask=legend)

        frames.append(bg.copy())

    writeGif('derp.gif', frames, duration=0.5)

    f = open('derp.gif', 'rb')
    ba = bytearray(f.read())
    response = make_response(ba)
    response.headers['Content-Type'] = 'image/gif'
    return response

if __name__ == "__main__":
    app.debug = True
    app.run()
    # gifme()
