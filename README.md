An experiment of github action cron job pinging the [OOI raw archive](https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/08-HYDBBA103) about every 30 minutes (github cron actions do not work on a shorter interval).

The `script.py` takes the file that was last uploaded and creates a spectrogram. One can add additional preprocessing of the files, for example, calculate the power spectrum. This kind of periodic pinging can be used to detect loud events.

* currently there is a delay in upload of the new data around from 12:00am UTC time to about 6-7 am. This is being investigated.


