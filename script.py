import obspy
import requests
from html.parser import HTMLParser
import datetime
import re
import matplotlib.pyplot as plt

# extracting link for last file today
class MyHTMLParser(HTMLParser):
    def handle_data(self, data):
        if 'HYVM2' in data:
            filelist.append(data)

yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
datestr = yesterday.strftime('%Y/%m/%d')
node = 'PC01A'
url = f'https://rawdata.oceanobservatories.org/files/RS01SBPS/{node}/08-HYDBBA103/{datestr}'

page = requests.get(url)
if page.status_code == 404:
    print('Following directory doesn\'t exist:\n' + url)

filelist = []
parser = MyHTMLParser()
parser.feed(str(page.content))

for filename in filelist:
    full_url = f'{url}/{filename}'
    st = obspy.read(full_url)
    st.filter('bandpass', freqmin=2000, freqmax=6000.0)
    st.decimate(factor=10)
    recording_time = re.search(r'OO-HYVM2--YDH-(.*?)\.mseed', filename).group(1)
    # upload-artifact doesn't support ':' in filepaths!
    recording_time = recording_time.replace(':', '-')
    outfile = f'{recording_time}_spectrogram.png'
    st.spectrogram(outfile=outfile, dbscale=True, wlen = 0.1)
    # Need to do some clearing, otherwise matplotlib hogs too much memory
    # when saving plots to files
    plt.cla()
    plt.close('all')
    print('Finished ' + filename)
