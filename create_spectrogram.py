import argparse
import logging
from os import path
from pathlib import Path

import matplotlib.pyplot as plt
from scipy.io import wavfile


def create_spec_name(wav_name, output_dir=None):
    """Creates appropriate path to the spectrogram from input .wav file and output directory.

    Args:
        `wav_name`: Path to the input .wav file.
        `output_dir`: Path to the output directory.
    Returns:
        Path to the output spectrogram.
    """
    spec_name = path.splitext(path.basename(wav_name))[0]
    if output_dir is not None:
        spec_name = path.join(path.normpath(output_dir), spec_name)
    return f"{spec_name}.png"


def plot_psd(data, samplerate, nfft=256, noverlap=128):
    """Plots power spectral density spectrogram.

    Args:
        `data`: Array or sequence containing the data.
        `samplerate`: The sampling frequency (samples per time unit).
        `nfft`: The number of data points used in each block for the FFT. A power 2 is most efficient.
        `noverlap`: The number of points of overlap between blocks.
    """
    plt.specgram(data, Fs=samplerate, NFFT=nfft, noverlap=noverlap, vmin=-200, vmax=100)
    plt.ylabel("Frequency [Hz]")
    cbar = plt.colorbar()
    cbar.set_label("DB")


def save_spectrogram(input_wav, plot_path=None, nfft=256):
    """Saves power spectral density spectrogram to file.

    Args:
        `input_wav`: Path to the input .wav file.
        `plot_path`: Path to the output spectrogram file. Default is `input_wav` with .png extension.
        `nfft`: The number of data points used in each block for the FFT. A power 2 is most efficient.
    Returns:
        Path to the spectrogram.
    """
    samplerate, data = wavfile.read(input_wav)
    noverlap = nfft // 2 if nfft <= 128 else 128

    title = path.splitext(path.basename(input_wav))[0]
    plt.title(title)
    if len(data.shape) == 1:
        plot_psd(data, samplerate, nfft, noverlap)
    else:
        plt.subplot(211)
        plot_psd(data[:, 0], samplerate, nfft, noverlap)
        title = f"{title}\nChannel 0 above, Channel 1 below"
        plt.title(title)

        plt.subplot(212)
        plot_psd(data[:, 1], samplerate, nfft, noverlap)

    plt.xlabel("Time [s]")

    if plot_path is None:
        plot_path = f"{path.splitext(input_wav)[0]}.png"
    else:
        Path(path.dirname(plot_path)).mkdir(parents=True, exist_ok=True)
    plt.savefig(plot_path)

    plt.cla()
    plt.close("all")
    logging.info("Finished " + input_wav)
    return plot_path


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

    save_spectrogram(args.input, args.output, args.nfft)
