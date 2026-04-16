# Github Actions Automation for Ambient-Sound-Analysis

The following details the github actions scripts used for automatic data processing for [ambient-sound-analysis](https://github.com/orcasound/ambient-sound-analysis)

## Automated pipeline for sound file to Power Spectral Density (PSD) parquet files

See: git_action_psd_upload.py

### Purpose

The purpose of this github actions workflow is to asyncronously automate the processing of .ts sound files into a PSD and broadband parquet dataframe and publish the parquet files to an S3 bucket. The store of a PSD and broadband dataframe facilitates retrospective analyses of sound pollution and Orca call signals and their relationships.

### Script/Workflow Features

* Partitioning of parquet files by Hydrophone and date for the two datasets: PSD and Broadband.
* Bookmarking class, (similar to AWS glue bookmarking), that uses a json file uploaded to S3 as a bookmark to track data processed.
* Parallelization of data processing per hydrophone by using Github workflow matrix strategy.

### Script process
```mermaid
flowchart TB
    n3["bookmark available?"] -- no --> n5["start_time = create bookmark for 1 hr earlier"]
    n4["start_time = load bookmark"] --> n6["end_time = now"]
    n5 --> n6
    n9["NoiseAnalysisPipeline for start_time to end_time"] --> n17["bookmark = end_time"]
    n18["For every hydrophone"] --> n3
    n6 --> n9
    n3 -- yes --> n19["bookmark &lt; 6 hours ago?"]
    n19 -- yes --> n4
    n19 -- no --> n20["start_time = 1 hr earlier"]

    n3@{ shape: rounded}
    n5@{ shape: rounded}
    n4@{ shape: rounded}
    n6@{ shape: rounded}
    n9@{ shape: rounded}
    n17@{ shape: rounded}
    n18@{ shape: rounded}
    n19@{ shape: rounded}
    n20@{ shape: rounded}
```
### Note on Orca-hls-utils
Currently using [this fork](https://github.com/ayushmall0710/orca-hls-utils/commit/18e72ed8f81391629ad64462172c56711134c970) of orca-hls-utils because of bugs in get_next_clip() and with time zone handling.


## Automated pipeline for ship monitor data to ship metrics parquet files

see git_action_ship_metrics_upload.py

### Purpose

The purpose of this GitHub Actions workflow is to asynchronously automate the process of combining broadband sound data with ship monitoring data to calculate ship metrics and publish the resulting Parquet files to an S3 bucket. These stored ship metrics enable further analysis of ship noise within the Orcasound Lab monitoring area.

### Script/Workflow Features

* Load ship tracking data. The start_time and end_time are parsed from the weekly .zip file provided by M2. They are typically defined as follows, though they may vary slightly depending on the source file:
    - start_time: current_date - 8 days
    - end_time: current_date - 1 day
* Load sound broadband data between start_time and end_time
* Calculate metrics
    - Sound related metrics will be None if there are no sound data between start_time and end_time
* Upload to S3 and bookmark the last processed time

