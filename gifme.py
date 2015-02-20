import urllib2
import cStringIO
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

legend = Image.open(cStringIO.StringIO(urllib2.urlopen(LEGEND_URL).read())).convert('RGBA')
background = Image.open(cStringIO.StringIO(urllib2.urlopen(BACKGROUND_IMAGE_URL).read())).convert('RGBA')
topography = Image.open(cStringIO.StringIO(urllib2.urlopen(TOPOGRAPHY_URL).read())).convert('RGBA')
range_ = Image.open(cStringIO.StringIO(urllib2.urlopen(RANGE_URL).read())).convert('RGBA')
locations = Image.open(cStringIO.StringIO(urllib2.urlopen(LOCATIONS_URL).read())).convert('RGBA')

image_regex = re.compile(r'theImageNames\[\d\]')
url_regex = re.compile(r'http.*png')

def fetch_radar_image_urls():
    return [
        url_regex.search(line).group(0)
        for line in urllib2.urlopen(RADAR_URL).readlines()
        if image_regex.search(line)
    ]

def create_frame(url):
    frame = Image.new("RGBA", legend.size)
    box = (0, 0) + background.size
    frame.paste(background, box=box)
    frame.paste(topography, box=box, mask=topography)

    fg = Image.open(cStringIO.StringIO(urllib2.urlopen(url).read())).convert('RGBA')
    frame.paste(fg, box=box, mask=fg)

    frame.paste(range_, box=box, mask=range_)
    frame.paste(locations, box=box, mask=locations)
    frame.paste(legend, mask=legend)

    return frame


@app.route('/')
@app.route('/radar.gif')
def gifme():
    frames = [create_frame(url) for url in fetch_radar_image_urls()]

    gif_buffer = cStringIO.StringIO()
    writeGif(gif_buffer, frames, duration=0.5)

    response = make_response(gif_buffer.getvalue())
    response.headers['Content-Type'] = 'image/gif'
    return response

if __name__ == "__main__":
    app.debug = True
    app.run()
    # gifme()
