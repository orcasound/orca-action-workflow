import obspy
import requests
from html.parser import HTMLParser
import datetime
import re

# extracting link for last file today
class MyHTMLParser(HTMLParser):
    def handle_data(self, data):
        if 'HYVM2' in data:
            filelist.append(data)

yesterday = datetime.datetime.today() - datetime.timedelta(days=2)
datestr = yesterday.strftime('%Y/%m/%d')
node = 'PC01A'
url = f'https://rawdata.oceanobservatories.org/files/RS01SBPS/{node}/08-HYDBBA103/{datestr}'

page = requests.get(url)
if page.status_code == 404:
    print('Following directory doesn\'t exist:\n' + url)

filelist = []
parser = MyHTMLParser()
parser.feed(str(page.content))

for filename in filelist[-10:]:
    recording_time = re.search(r'OO-HYVM2--YDH-(.*?)\.mseed', filename).group(1)
    full_url = f'{url}/{filename}'
    st = obspy.read(full_url)
    st.filter('bandpass', freqmin=2000, freqmax=6000.0)
    st.decimate(factor=10)
    st.spectrogram(outfile=f'{recording_time}_spectrogram.png', dbscale=True, wlen = 0.1)
    print('Finished ' + filename)
