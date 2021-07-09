import datetime
import logging
import os
import sys

from ooipy.request import hydrophone_request

from create_spectrogram import save_spectrogram

logging.basicConfig(
    format="%(levelname)s:%(message)s", stream=sys.stdout, level=logging.INFO
)

end_time = datetime.datetime.combine(
    datetime.datetime.today(), datetime.datetime.min.time()
)
start_time = end_time - datetime.timedelta(days=1)
segment_length = datetime.timedelta(minutes=5)
node = "PC01A"

while start_time < end_time:
    segment_end = min(start_time + segment_length, end_time)
    hydrophone_data = hydrophone_request.get_acoustic_data(
        start_time, segment_end, node, verbose=True
    )
    if hydrophone_data is None:
        logging.info(f"Could not get data from {start_time} to {segment_end}")
        start_time = segment_end
        continue
    datestr = start_time.strftime("%Y-%m-%dT%H-%M-%S-%f")[:-3]
    wav_name = f"{datestr}.wav"
    hydrophone_data.wav_write(wav_name)
    save_spectrogram(wav_name)
    os.remove(wav_name)
    start_time = segment_end
