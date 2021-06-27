import argparse
import glob
import logging
import sys
from os import path

from create_spectrogram import create_spectrogram

logging.basicConfig(
    format="%(levelname)s:%(message)s", stream=sys.stdout, level=logging.INFO
)

parser = argparse.ArgumentParser(
    description="Creates spectrogram for each .wav file in the input directory."
)
parser.add_argument("input_dir", help="Path to the input directory with .wav files.")
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

for input_path in sorted(glob.glob(f"{args.input_dir}/*.wav")):
    output_fname = None
    if args.output is not None:
        file_name = path.splitext(path.basename(input_path))[0]
        output_fname = f"{args.output}/{file_name}"
    create_spectrogram(input_path, output_fname, args.nfft)
