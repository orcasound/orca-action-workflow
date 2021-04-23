An experiment of GitHub Actions cron job pinging the [OOI raw archive](https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/08-HYDBBA103) at 12:00 UTC every day.

The `script.py` takes all the files from the previous day and creates spectrograms for them. Note that this can take a couple of hours. One can add additional preprocessing of the files, for example, calculate the power spectrum.

* currently there is a delay in upload of the new data around from 12:00am UTC time to about 6-7 am. This is being investigated.
