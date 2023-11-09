# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from pathlib import Path
import sys
import tempfile
import unittest

if os.environ.get('ROSBAG2_PY_TEST_WITH_RTLD_GLOBAL', None) is not None:
    # This is needed on Linux when compiling with clang/libc++.
    # TL;DR This makes class_loader work when using a python extension compiled with libc++.
    #
    # For the fun RTTI ABI details, see https://whatofhow.wordpress.com/2015/03/17/odr-rtti-dso/.
    sys.setdlopenflags(os.RTLD_GLOBAL | os.RTLD_LAZY)

from common import get_rosbag_options  # noqa
import rosbag2_py  # noqa
from rosbag2_py import (
    bag_rewrite,
    RecordOptions,
    StorageOptions,
)  # noqa

RESOURCES_PATH = Path(os.environ['ROSBAG2_PY_TEST_RESOURCES_DIR'])


class TestConvert(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.TemporaryDirectory()
        cls.tmp_path = Path(cls.tmpdir.name)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.tmpdir.cleanup()
        except OSError:
            pass

    def test_empty_args(self):
        with self.assertRaises(RuntimeError):
            bag_rewrite([], [])

    def test_basic_convert(self):
        # This test is just to test that the rosbag2_py wrapper parses input
        # It is not a comprehensive test of bag_rewrite.
        bag_a_path = RESOURCES_PATH / 'convert_a'
        bag_b_path = RESOURCES_PATH / 'convert_b'
        output_uri_1 = self.tmp_path / 'converted_1'
        output_uri_2 = self.tmp_path / 'converted_2'
        input_options = [
            StorageOptions(uri=str(bag_a_path)),
            StorageOptions(uri=str(bag_b_path), storage_id='sqlite3'),
        ]
        output_options = [
            (
                StorageOptions(uri=str(output_uri_1)),
                RecordOptions(topics=['a_empty'])
            ),
            (
                StorageOptions(uri=str(output_uri_2)),
                RecordOptions(exclude='.*empty.*')
            ),
        ]

        bag_rewrite(input_options, output_options)
        self.assertTrue(output_uri_1.exists() and output_uri_1.is_dir())
        self.assertTrue((output_uri_1 / 'metadata.yaml').exists())
        self.assertTrue(output_uri_2.exists() and output_uri_2.is_dir())
        self.assertTrue((output_uri_2 / 'metadata.yaml').exists())
