import pandas as pd
from orcasound_noise.pipeline.pipeline import NoiseAnalysisPipeline
from orcasound_noise.utils import Hydrophone
import datetime as dt

import pandas as pd
import matplotlib.pyplot as plt
from orcasound_noise.pipeline.acoustic_util import plot_spec, plot_bb


#Example 1: Port Townsend, 1 Hz Frequency, 60-second samples
if __name__ == '__main__':
    pipeline = NoiseAnalysisPipeline(Hydrophone.PORT_TOWNSEND,
                                     delta_f=10, bands=None,
                                     delta_t=60, mode='safe')


now = dt.datetime.now()

psd_path, broadband_path = pipeline.generate_parquet_file(now, 
                                                          now - dt.timedelta(hours = 6), 
                                                          upload_to_s3=False)


psd_df = pd.read_parquet(psd_path)
bb_df = pd.read_parquet(broadband_path)

plot_spec(psd_df)
plot_bb(bb_df)

plt.savefig('broadband.png')
