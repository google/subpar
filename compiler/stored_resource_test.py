# Copyright 2016 Google Inc. All Rights Reserved.
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
import unittest
import zipfile

from subpar.compiler import stored_resource
from subpar.compiler import test_utils


class StoredResourceTest(unittest.TestCase):
    """Test PythonArchive class"""

    def setUp(self):
        self.date_time_tuple = (1980, 1, 1, 0, 0, 0)

    def _write_and_check(self, resource, name, expected_content):
        # Write zipfile
        tmpdir = test_utils.mkdtemp()
        zipfile_name = os.path.join(tmpdir, 'baz.zip')
        z = zipfile.ZipFile(zipfile_name, 'w')
        resource.store(z)
        z.close()

        # Read and validate zipfile
        z = zipfile.ZipFile(zipfile_name, 'r')
        self.assertEqual(z.namelist(), [name])
        self.assertEqual(z.getinfo(name).date_time, self.date_time_tuple)
        with z.open(name) as infile:
            actual_content = infile.read()
        self.assertEqual(expected_content, actual_content)
        z.close()

    def test_StoredFile(self):
        expected_content = b'Contents of foo/bar'
        name = 'foo/bar'
        f = test_utils.temp_file(expected_content)
        resource = stored_resource.StoredFile(
            name, self.date_time_tuple, f.name)
        self._write_and_check(resource, name, expected_content)

    def test_StoredContent(self):
        expected_content = b'Contents of foo/bar'
        name = 'foo/bar'
        resource = stored_resource.StoredContent(
            name, self.date_time_tuple, expected_content)
        self._write_and_check(resource, name, expected_content)

    def test_EmptyFile(self):
        name = 'foo/bar'
        resource = stored_resource.EmptyFile(name, self.date_time_tuple)
        self._write_and_check(resource, name, b'')


if __name__ == '__main__':
    unittest.main()
