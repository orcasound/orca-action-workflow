"""Unit tests for OOI workflow"""

import datetime
import os
import shutil
from os import path

import pytest

from ooi_processing import save_ooi_spectrograms


@pytest.mark.parametrize(
    "start_time_str, end_time_str, segment_length_float, node, output_dir, expected_files_count",
    [
        ("2017-03-10T00-00-00", "2017-03-10T00-05-00", None, None, None, 1),
        ("2017-03-10T00-00-00", "2017-03-10T00-05-00", 1, None, None, 5),
        ("2017-03-10T00-00-00", "2017-03-10T00-05-00", 1, None, "long/path/", 5),
        ("2017-03-10T00-05-00", "2017-03-10T00-00-00", 1, None, None, 0),
    ],
)
def test_ooi_spectrograms(
    start_time_str,
    end_time_str,
    segment_length_float,
    node,
    output_dir,
    expected_files_count,
):
    start_time = datetime.datetime.strptime(start_time_str, "%Y-%m-%dT%H-%M-%S")
    end_time = datetime.datetime.strptime(end_time_str, "%Y-%m-%dT%H-%M-%S")
    if segment_length_float is None:
        segment_length_float = 5.0
    if node is None:
        node = "PC01A"
    if output_dir is None:
        output_dir = "spectrograms"
    segment_length = datetime.timedelta(minutes=segment_length_float)
    save_ooi_spectrograms(start_time, end_time, segment_length, node, output_dir)
    if expected_files_count > 0:
        assert expected_files_count == len(
            [
                name
                for name in os.listdir(output_dir)
                if path.isfile(path.join(output_dir, name))
            ]
        )
        shutil.rmtree(output_dir)
    else:
        assert not path.exists(output_dir)
