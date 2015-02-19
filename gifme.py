import urllib
import urllib2
import re
from PIL import Image
from flask import Flask, make_response
from images2gif import writeGif
app = Flask(__name__)

RADAR_URL = 'http://www.bom.gov.au/products/IDR023.loop.shtml'
BACKGROUND_IMAGE_URL = 'http://www.bom.gov.au/products/radar_transparencies/IDR023.background.png'
TOPOGRAPHY_URL = 'http://www.bom.gov.au/products/radar_transparencies/IDR023.topography.png'
RANGE_URL = 'http://www.bom.gov.au/products/radar_transparencies/IDR023.range.png'
LOCATIONS_URL = 'http://www.bom.gov.au/products/radar_transparencies/IDR023.locations.png'
LEGEND_URL = 'http://www.bom.gov.au/products/radar_transparencies/IDR.legend.0.png'

urllib.urlretrieve(BACKGROUND_IMAGE_URL, 'background.png')
urllib.urlretrieve(TOPOGRAPHY_URL, 'topography.png')
urllib.urlretrieve(RANGE_URL, 'range.png')
urllib.urlretrieve(LOCATIONS_URL, 'locations.png')
urllib.urlretrieve(LEGEND_URL, 'legend.png')

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
    radar_image_urls = [
        url_regex.search(line).group(0)
        for line in urllib2.urlopen(RADAR_URL).readlines()
        if image_regex.search(line)
    ]

    frames = []
    for url in radar_image_urls:
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
