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

import io
import os
import sys
import unittest
import zipfile

from subpar.compiler import test_utils
from subpar.runtime import support

# `import pip` can cause arbitrary sys.path changes,
# especially if using the Debian `python-pip` package or
# similar.  Do it first to get those changes out of the
# way.
old_sys_path = sys.path
try:
    mock_sys_path = list(sys.path)
    sys.path = mock_sys_path
    import pip  # noqa
except ImportError:
    pass
finally:
    sys.path = old_sys_path


# We assume this test isn't run as a par file.
class SupportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create zipfile for tests to read
        tmpdir = test_utils.mkdtemp()
        zipfile_name = os.path.join(tmpdir, '_support_test_sample.par')

        z = zipfile.ZipFile(zipfile_name, 'w')
        entry_name = '_support_test_helper_script.py'
        entry_data = b'print("Hello world")'
        z.writestr(entry_name, entry_data)

        z.close()

        cls.zipfile_name = zipfile_name
        cls.entry_name = entry_name
        cls.entry_data = entry_data

        # Create mock loader object
        class MockLoader(object):
            pass
        mock_loader = MockLoader()
        mock_loader.archive = zipfile_name
        mock_loader.prefix = ''
        main = sys.modules.get('__main__')
        old_loader = getattr(main, '__loader__', None)
        main.__loader__ = mock_loader

        cls.mock_loader = mock_loader
        cls.old_loader = old_loader

    @classmethod
    def tearDownClass(cls):
        # Cleanup zipfile
        os.remove(cls.zipfile_name)

        # Cleanup loader mock
        main = sys.modules.get('__main__')
        main.__loader__ = cls.old_loader

    def test__log(self):
        old_stderr = sys.stderr
        try:
            mock_stderr = io.StringIO()
            sys.stderr = mock_stderr
            # pylint: disable=protected-access,no-self-use
            support._log('Test Log Message')
            if sys.flags.verbose:
                expected = 'Test Log Message\n'
            else:
                expected = ""
            self.assertEqual(mock_stderr.getvalue(), expected)
        finally:
            sys.stderr = old_stderr

    def test__find_archive(self):
        # pylint: disable=protected-access
        archive_path = support._find_archive()

        self.assertNotEqual(archive_path, None)
        self.assertTrue(zipfile.is_zipfile(archive_path))

    def test__extract_files(self):
        # Extract zipfile
        extract_path = support._extract_files(self.zipfile_name)

        # Check results
        self.assertTrue(os.path.isdir(extract_path))
        extracted_file = os.path.join(extract_path, self.entry_name)
        self.assertTrue(os.path.isfile(extracted_file))
        with open(extracted_file, 'rb') as f:
            actual_data = f.read()
            self.assertEqual(actual_data, self.entry_data)

    def test__version_check(self):
        class MockModule(object):
            pass

        class MockOldWorkingSet(object):
            def add(self, dist, entry=None, insert=True):
                pass

        class MockNewWorkingSet(object):
            def add(self, dist, entry=None, insert=True, replace=False):
                pass

        pkg_resources = MockModule()
        self.assertFalse(support._version_check_pkg_resources(pkg_resources))

        pkg_resources.WorkingSet = MockOldWorkingSet()
        self.assertFalse(support._version_check_pkg_resources(pkg_resources))

        pkg_resources.WorkingSet = MockNewWorkingSet()
        self.assertTrue(support._version_check_pkg_resources(pkg_resources))

    def test_setup(self):
        # Run setup() without file extraction
        old_sys_path = sys.path
        try:
            mock_sys_path = list(sys.path)
            mock_sys_path[0] = self.zipfile_name
            sys.path = mock_sys_path
            success = support.setup(import_roots=['some_root', 'another_root'],
                                    zip_safe=True)
            self.assertTrue(success)
        finally:
            sys.path = old_sys_path

        # Check results
        self.assertTrue(
            mock_sys_path[1].endswith('some_root'),
            mock_sys_path)
        self.assertTrue(
            mock_sys_path[2].endswith('another_root'),
            mock_sys_path)
        # If we have no pkg_resources, or a really old version of
        # pkg_resources, setup skips some things
        module = sys.modules.get('pkg_resources', None)
        if module and support._version_check_pkg_resources(module):
            self.assertEqual(mock_sys_path[3:], sys.path[1:])

    def test_setup__extract(self):
        # Run setup() with file extraction
        old_sys_path = sys.path
        try:
            mock_sys_path = list(sys.path)
            mock_sys_path[0] = self.zipfile_name
            sys.path = mock_sys_path
            success = support.setup(import_roots=['some_root'], zip_safe=False)
            self.assertTrue(success)
        finally:
            sys.path = old_sys_path

        # Check results
        self.assertNotEqual(mock_sys_path[0], self.zipfile_name)
        self.assertTrue(
            os.path.isdir(mock_sys_path[0]),
            mock_sys_path)


if __name__ == '__main__':
    unittest.main()
