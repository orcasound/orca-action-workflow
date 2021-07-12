import argparse
import glob
import logging
import sys
from datetime import datetime
from os import path
from pathlib import Path

import ffmpeg
import m3u8

from create_spectrogram import save_spectrogram


def convert_with_ffmpeg(input_file, output_file):
    """Converts input file using ffmpeg."""
    try:
        input = ffmpeg.input(input_file)
        output = ffmpeg.output(input, output_file)
        output.run(capture_stdout=True, capture_stderr=True)
    except ffmpeg.Error as e:
        logging.error(e.stdout.decode("utf8"))
        logging.error(e.stderr.decode("utf8"))
        raise e


def create_readable_name(directory, timestamp):
    """Creates human readable `.wav` file name from `output_dir` and Unix timestamp.

    Resulting name will look like `directory`/%Y-%m-%dT%H-%M-%S.wav"""
    return path.join(
        directory,
        f"{datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H-%M-%S-%f')[:-3]}.wav",
    )


def convert2wav(input_dir, output_dir):
    """Converts all `.ts` files from `live.m3u8` to `.wav`.

    All files will have the following format: `%Y-%m-%dT%H-%M-%S.wav`

    Args:
        `input_dir`: Path to the input directory with `.m3u8` playlist and `.ts` files. Should contain Unix timestamp of the stream start.
        `output_dir`: Path to the output directory.
    Returns:
        None
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    playlist = m3u8.load(path.join(input_dir, "live.m3u8"))
    timestamp = float(path.basename(input_dir))
    segments = playlist.data["segments"]
    old_name = path.join(input_dir, segments[0]["uri"])
    convert_with_ffmpeg(old_name, create_readable_name(output_dir, timestamp))
    for idx, segment in enumerate(segments[1:], start=1):
        timestamp += segments[idx - 1]["duration"]
        old_name = path.join(input_dir, segment["uri"])
        convert_with_ffmpeg(old_name, create_readable_name(output_dir, timestamp))


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s:%(message)s", stream=sys.stdout, level=logging.INFO
    )
    parser = argparse.ArgumentParser(
        description="Creates spectrogram for each .ts file in the input directory."
    )
    parser.add_argument(
        "input_dir",
        help="Path to the input directory with `.m3u8` playlist and `.ts` files. Should contain Unix timestamp of the stream start.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to the output directory for spectrograms. Default is `input_dir`.",
    )
    parser.add_argument(
        "-n",
        "--nfft",
        type=int,
        help="The number of data points used in each block for the FFT. A power 2 is most efficient. Default is 256.",
        default=256,
    )
    args = parser.parse_args()

    convert2wav(path.normpath(args.input_dir), "wav")

    for input_wav in sorted(glob.glob("wav/*.wav")):
        output_fname = None
        if args.output is not None:
            Path(args.output).mkdir(parents=True, exist_ok=True)
            file_name = path.splitext(path.basename(input_wav))[0]
            output_fname = f"{path.normpath(args.output)}/{file_name}"
        save_spectrogram(input_wav, output_fname, args.nfft)
