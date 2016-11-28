import datetime
import os
import re
import urllib
from io import BytesIO
from urllib.request import urlopen

from flask import Flask, make_response
from PIL import Image

from images2gif import writeGif

app = Flask(__name__)

cache = False

if cache and not os.path.exists('cache'):
    os.makedirs('cache')

PAGE_URL = 'http://www.bom.gov.au/products/IDR023.loop.shtml'
BACKGROUND_IMAGE_URL = 'http://www.bom.gov.au/products/radar_transparencies/IDR023.background.png'
TOPOGRAPHY_URL = 'http://www.bom.gov.au/products/radar_transparencies/IDR023.topography.png'
RANGE_URL = 'http://www.bom.gov.au/products/radar_transparencies/IDR023.range.png'
LOCATIONS_URL = 'http://www.bom.gov.au/products/radar_transparencies/IDR023.locations.png'
LEGEND_URL = 'http://www.bom.gov.au/products/radar_transparencies/IDR.legend.0.png'
RADAR_URL_PREFIX = 'http://wac.72DD.edgecastcdn.net/8072DD/radimg/radar/IDR023.T.'

image_regex = re.compile(r'theImageNames\[\d\]')
last_image_regex = re.compile(r'theImageNames\[5\] = "http:\/\/.*T\.(\d{12})\.png"')
url_regex = re.compile(r'http.*png')
filename_regex = re.compile(r'\/([^\/]+.png)')

def fetch_image(url):
    if cache:
        filename = os.path.join('cache', filename_regex.search(url).group(1))
        if not os.path.exists(filename):
            print('Caching ' + url)
            try:
                urllib.urlretrieve(url, filename)
            except Exception as e:
                raise Exception("Error retrieving image " + url + "\n" + e.message)
        return Image.open(filename).convert('RGBA')
    else:
        print('Fetching ' + url + '...')
        # try:
        return Image.open(BytesIO(urlopen(url).read())).convert('RGBA')
        # except Exception as e:
            # raise Exception("Error retrieving image " + url + "\n" + e.message)

legend = fetch_image(LEGEND_URL)
background = fetch_image(BACKGROUND_IMAGE_URL)
topography = fetch_image(TOPOGRAPHY_URL)
range_ = fetch_image(RANGE_URL)
locations = fetch_image(LOCATIONS_URL)

def fetch_radar_image_urls():
    return [
        url_regex.search(line.decode()).group(0)
        for line in urlopen(PAGE_URL).readlines()
        if image_regex.search(line.decode('utf-8'))
    ]

def fetch_radar_image_urls_last_6_hours():
    print('Determining radar URLs...')
    urls = []
    for line in urlopen(PAGE_URL).readlines():
        match = last_image_regex.search(line.decode('utf-8'))
        if match:
            timestamp = datetime.datetime.strptime(match.group(1), "%Y%m%d%H%M")
            # for _ in range(240):
            #for _ in range(120):
            for _ in range(70):
                url = RADAR_URL_PREFIX + timestamp.strftime("%Y%m%d%H%M") + '.png'
                urls.insert(0, url)
                timestamp = timestamp + datetime.timedelta(minutes=-6)
    return urls

def create_frame(url):
    try:
        radar = fetch_image(url)
    except IOError:
        print('Skipping bad frame ' + url)
        return None
    print('Creating frame for ' + url + '...')
    frame = Image.new("RGBA", legend.size)
    box = (0, 0) + background.size
    frame.paste(background, box=box)
    frame.paste(topography, box=box, mask=topography)
    frame.paste(radar, box=box, mask=radar)
    frame.paste(range_, box=box, mask=range_)
    frame.paste(locations, box=box, mask=locations)
    frame.paste(legend, mask=legend)
    print('Completed frame for ' + url)
    return frame

@app.route('/')
@app.route('/radar.gif')
def gifme():
    frames = [
        frame
        for frame in [
            create_frame(url)
            for url in fetch_radar_image_urls()
        ]
        if frame != None
    ]

    print('Making gif...')
    gif_buffer = BytesIO()
    writeGif(gif_buffer, frames, duration=0.5)
    print('Done')

    response = make_response(gif_buffer.getvalue())
    response.headers['Content-Type'] = 'image/gif'
    return response

@app.route('/6/radar.gif')
def gifme6():
    frames = [
        frame
        for frame in [
            create_frame(url)
            for url in fetch_radar_image_urls_last_6_hours()
        ]
        if frame != None
    ]
    gif_buffer = BytesIO()
    writeGif(gif_buffer, frames, duration=0.001)
    #f = open('stuff.gif', 'rb+')
    #f.write(gif_buffer.getvalue())

    response = make_response(gif_buffer.getvalue())
    response.headers['Content-Type'] = 'image/gif'
    return response

if __name__ == "__main__":
    app.debug = True
    app.run()
#gifme6()
