import pandas as pd
from orcasound_noise.pipeline.pipeline import NoiseAnalysisPipeline
from orcasound_noise.utils import Hydrophone
import datetime as dt


#Example 1: Port Townsend, 1 Hz Frequency, 60-second samples
if __name__ == '__main__':
    pipeline = NoiseAnalysisPipeline(Hydrophone.PORT_TOWNSEND,
                                     delta_f=10, bands=None,
                                     delta_t=60, mode='safe')

psd_path, broadband_path = pipeline.generate_parquet_file(dt.datetime(2023, 3, 23, 7), 
                                                          dt.datetime(2023, 3, 23, 8), 
                                                          upload_to_s3=False)

plot_spec(psd_df)
plot_bb(bb_df)

plt.savefig('broadband.png')
