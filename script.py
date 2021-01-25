import obspy
import requests
from html.parser import HTMLParser
import numpy as np
from datetime import datetime

# extracting link for last file today
class MyHTMLParser(HTMLParser):
    def handle_data(self, data):
        if 'HYVM2' in data:
            filelist.append(data)
datestr = datetime.today().strftime('%Y/%m/%d')
url='https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/08-HYDBBA103/{}'.format(datestr)
r=requests.get(url)
print(url)
filelist = []
parser = MyHTMLParser()
parser.feed(str(r.content))
filepath = filelist[-1]
full_url = f'{url}/{filepath}'
# reading from url
st = obspy.read(full_url)
st.filter('bandpass', freqmin=2000, freqmax=6000.0)
st.decimate(factor=10)
st.spectrogram(outfile='spectrogram.png', dbscale=True, wlen = 0.1)

