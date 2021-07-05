import datetime
import logging
import sys

from ooipy.request import hydrophone_request

from create_spectrogram import save_spectrogram

logging.basicConfig(
    format="%(levelname)s:%(message)s", stream=sys.stdout, level=logging.INFO
)

end_time = datetime.datetime.today()
start_time = end_time - datetime.timedelta(days=1)
segment_length = datetime.timedelta(minutes=5)
node = "PC01A"

while start_time < end_time:
    segment_end = min(start_time + segment_length, end_time)
    hydrophone_data = hydrophone_request.get_acoustic_data(
        start_time, segment_end, node
    )
    wav_name = f"{start_time}.wav"
    hydrophone_data.wav_write(wav_name)
    save_spectrogram(wav_name)
    start_time = segment_end
