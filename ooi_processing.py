import argparse
import datetime
import logging
import os
import sys

from ooipy.request import hydrophone_request

from create_spectrogram import create_spec_name, save_spectrogram

if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s:%(message)s", stream=sys.stdout, level=logging.INFO
    )
    parser = argparse.ArgumentParser(
        description="Creates spectrogram for each segment."
    )
    parser.add_argument(
        "--node",
        help="Alphanumeric node id (e.g. PC01A)",
        default="PC01A",
        choices=[
            "LJ01D",
            "LJ01A",
            "PC01A",
            "PC03A",
            "LJ01C",
            "LJ03A",
            "AXABA1",
            "AXCC1",
            "AXEC2",
            "HYS14",
            "HYSB1",
        ],
    )
    parser.add_argument(
        "-s",
        "--start_time",
        help="Start time formatted as Y-m-dTH-M-S",
    )
    parser.add_argument(
        "-e",
        "--end_time",
        help="End time formatted as Y-m-dTH-M-S",
    )
    parser.add_argument(
        "-l",
        "--segment_length",
        type=float,
        default=5,
        help="Segment length in minutes. Default is %(default)s.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="spectrograms",
        help="Path to the output directory for spectrograms. Default is %(default)s.",
    )
    parser.add_argument(
        "-n",
        "--nfft",
        type=int,
        default=256,
        help="The number of data points used in each block for the FFT. A power 2 is most efficient. Default is %(default)s.",
    )
    args = parser.parse_args()

    if args.end_time is None:
        end_time = datetime.datetime.combine(
            datetime.datetime.today(), datetime.datetime.min.time()
        )
    else:
        end_time = datetime.datetime.strptime(args.end_time, "%Y-%m-%dT%H-%M-%S")

    if args.start_time is None:
        start_time = end_time - datetime.timedelta(days=1)
    else:
        start_time = datetime.datetime.strptime(args.start_time, "%Y-%m-%dT%H-%M-%S")

    segment_length = datetime.timedelta(minutes=args.segment_length)

    while start_time < end_time:
        segment_end = min(start_time + segment_length, end_time)
        hydrophone_data = hydrophone_request.get_acoustic_data(
            start_time, segment_end, args.node, verbose=True
        )
        if hydrophone_data is None:
            logging.info(f"Could not get data from {start_time} to {segment_end}")
            start_time = segment_end
            continue
        datestr = start_time.strftime("%Y-%m-%dT%H-%M-%S-%f")[:-3]
        wav_name = f"{datestr}.wav"
        hydrophone_data.wav_write(wav_name)
        spec_fname = create_spec_name(wav_name, args.output)
        save_spectrogram(wav_name, spec_fname)
        os.remove(wav_name)
        start_time = segment_end
