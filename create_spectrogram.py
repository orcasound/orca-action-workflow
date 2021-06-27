import argparse
import logging

import matplotlib.pyplot as plt
from scipy.io import wavfile


def create_spectrogram(input_wav, plot_path=None, NFFT=256):
    """Plots power spectral density spectrogram.

    Args:
        `input_wav`: Path to the input .wav file.
        `plot_path`: Path to the output spectrogram file. Default is `input_wav` with .png extension.
        `NFFT`: The number of data points used in each block for the FFT. A power 2 is most efficient.
    Returns:
        None
    """
    samplerate, data = wavfile.read(input_wav)
    noverlap = NFFT // 2 if NFFT <= 128 else 128

    plt.subplot(211)
    plt.title("Channel 0 above, Channel 1 below")
    plt.specgram(data[:, 0], Fs=samplerate, NFFT=NFFT, noverlap=noverlap)
    plt.ylabel("Frequency")

    plt.subplot(212)
    plt.specgram(data[:, 1], Fs=samplerate, NFFT=NFFT, noverlap=noverlap)
    plt.xlabel("Time")
    plt.ylabel("Frequency")

    if plot_path is None:
        plot_path = input_wav.replace(".wav", ".png")
    plt.savefig(plot_path)

    plt.cla()
    plt.close("all")
    logging.info("Finished " + input_wav)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plots power spectral density spectrogram."
    )
    parser.add_argument("input", help="Path to the input .wav file.")
    parser.add_argument(
        "-o",
        "--output",
        help="Path to the output spectrogram file. Default is `input` with .png extension.",
    )
    parser.add_argument(
        "-n",
        "--nfft",
        type=int,
        help="The number of data points used in each block for the FFT. A power 2 is most efficient. Default is 256.",
        default=256,
    )
    args = parser.parse_args()

    create_spectrogram(args.input, args.output, args.nfft)
