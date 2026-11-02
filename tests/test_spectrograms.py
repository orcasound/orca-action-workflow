"""Unit tests for various util functions relating to spectrogram creation"""

import os.path

import matplotlib.pyplot as plt
import numpy as np
import pytest

from create_spectrogram import create_spec_name, save_spectrogram


@pytest.mark.parametrize(
    "wav_name, output_dir, expected",
    [
        ("2021-01-01T00-00-00-000.wav", None, "2021-01-01T00-00-00-000.png"),
        (
            "2021-01-01T00-00-00-000.wav",
            "spectrograms",
            "spectrograms/2021-01-01T00-00-00-000.png",
        ),
        (
            "2021-01-01T00-00-00-000.wav",
            "long/path/to/output",
            "long/path/to/output/2021-01-01T00-00-00-000.png",
        ),
        (
            "2021-01-01T00-00-00-000.wav",
            "end/slash/",
            "end/slash/2021-01-01T00-00-00-000.png",
        ),
        ("no_extension", None, "no_extension.png"),
        ("file.not_wav", None, "file.png"),
    ],
)
def test_create_spec_name(wav_name: str, output_dir: str, expected: str):
    assert create_spec_name(wav_name, output_dir) == expected


@pytest.mark.parametrize(
    "wav_name, plot_path, example_path",
    [
        ("tests/ooi.wav", None, "tests/ooi_example.png"),
        ("tests/ooi.wav", "tests/path/to/output/ooi.png", "tests/ooi_example.png"),
        (
            "tests/orcasound.wav",
            "tests/path/to/output/orcasound.png",
            "tests/orcasound_example.png",
        ),
    ],
)
def test_save_spectrogram(wav_name: str, plot_path: str, example_path: str):
    spec_path = save_spectrogram(wav_name, plot_path)
    assert os.path.isfile(spec_path)
    assert np.array_equal(plt.imread(example_path), plt.imread(spec_path))
