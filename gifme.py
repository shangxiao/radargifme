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

def get_image(url):
    return Image.open(cStringIO.StringIO(urllib2.urlopen(url).read())).convert('RGBA')

legend = get_image(LEGEND_URL)
background = get_image(BACKGROUND_IMAGE_URL)
topography = get_image(TOPOGRAPHY_URL)
range_ = get_image(RANGE_URL)
locations = get_image(LOCATIONS_URL)

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
