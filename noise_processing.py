import pandas as pd
from orcasound_noise.pipeline.pipeline import NoiseAnalysisPipeline
from orcasound_noise.utils import Hydrophone
import datetime as dt
import os

import pandas as pd
import matplotlib.pyplot as plt
import pytz


from orcasound_noise.pipeline.acoustic_util import plot_spec, plot_bb


import plotly.graph_objects as go

#Example 1: Port Townsend, 1 Hz Frequency, 60-second samples
if __name__ == '__main__':
    pipeline = NoiseAnalysisPipeline(Hydrophone.PORT_TOWNSEND,
                                     delta_f=10, bands=None,
                                     delta_t=60, mode='safe')


now = dt.datetime.now(pytz.timezone('US/Pacific'))

psd_path, broadband_path = pipeline.generate_parquet_file(now - dt.timedelta(hours = 6), 
                                                          now - dt.timedelta(hours = 1), 
                                                          upload_to_s3=False)


psd_df = pd.read_parquet(psd_path)
bb_df = pd.read_parquet(broadband_path)


# Create a new directory because it does not exist
if not os.path.exists('img'):
   os.makedirs('img')

# Create and save psd plot 
fig = plot_spec(psd_df)
fig.write_image('img/psd.png')

# Create and save bb plot
fig = plot_bb(bb_df)
fig.savefig('img/broadband.png')
