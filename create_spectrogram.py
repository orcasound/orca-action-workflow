import argparse
import logging

import matplotlib.pyplot as plt
from scipy.io import wavfile


def plot_psd(data, samplerate, NFFT=256, noverlap=128):
    """Plots power spectral density spectrogram.

    Args:
        `data`: Array or sequence containing the data.
        `samplerate`: The sampling frequency (samples per time unit).
        `NFFT`: The number of data points used in each block for the FFT. A power 2 is most efficient.
        `noverlap`: The number of points of overlap between blocks.
    """
    plt.specgram(data, Fs=samplerate, NFFT=NFFT, noverlap=noverlap)
    plt.ylabel("Frequency [Hz]")
    cbar = plt.colorbar()
    cbar.set_label("DB")


def save_spectrogram(input_wav, plot_path=None, NFFT=256):
    """Saves power spectral density spectrogram to file.

    Args:
        `input_wav`: Path to the input .wav file.
        `plot_path`: Path to the output spectrogram file. Default is `input_wav` with .png extension.
        `NFFT`: The number of data points used in each block for the FFT. A power 2 is most efficient.
    Returns:
        None
    """
    samplerate, data = wavfile.read(input_wav)
    noverlap = NFFT // 2 if NFFT <= 128 else 128

    title = input_wav.removesuffix(".wav")
    plt.title(title)
    if len(data.shape) == 1:
        plot_psd(data, samplerate, NFFT, noverlap)
    else:
        plt.subplot(211)
        plot_psd(data[:, 0], samplerate, NFFT, noverlap)
        title = f"{title}\nChannel 0 above, Channel 1 below"
        plt.title(title)

        plt.subplot(212)
        plot_psd(data[:, 1], samplerate, NFFT, noverlap)

    plt.xlabel("Time [s]")

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

    save_spectrogram(args.input, args.output, args.nfft)
