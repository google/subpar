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
import tempfile
import unittest
import zipfile

from subpar.runtime import support


class SupportTest(unittest.TestCase):

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
        path = support._find_archive()
        self.assertNotEqual(path, None)

    def test_setup(self):
        # mock out finding the archive to some other archive
        archive_path = self._make_archive([
            'some_root/main.py',
            'another_root/main.py'
        ])
        def mock_find_archive():
            return archive_path
        old_find_archive = support._find_archive
        support._find_archive = mock_find_archive

        # mock out sys path
        old_sys_path = sys.path
        mock_sys_path = list(sys.path)
        sys.path = mock_sys_path

        # `import pip` can cause arbitrary sys.path changes,
        # especially if using the Debian `python-pip` package or
        # similar.  Do it first to get those changes out of the
        # way.
        try:
            import pip  # noqa
        except ImportError:
            pass
        finally:
            sys.path = old_sys_path

        # Run setup()
        old_sys_path = sys.path
        try:
            mock_sys_path = list(sys.path)
            sys.path = mock_sys_path
            support.setup(import_roots=['some_root', 'another_root'])
        finally:
            support._find_archive = old_find_archive
            sys.path = old_sys_path

        # Check results
        self.assertTrue(mock_sys_path[1].endswith('{}/some_root'.format(archive_path)),
                        mock_sys_path)
        self.assertTrue(
            mock_sys_path[2].endswith('{}/another_root'.format(archive_path)),
            mock_sys_path)
        self.assertEqual(mock_sys_path[0], sys.path[0])
        self.assertEqual(mock_sys_path[3:], sys.path[1:])

    def test_setup_with_shared_objects(self):
        # mock out finding the archive to some other archive
        archive_path = self._make_archive([
            'some_root/main.py',
            'some_root/file.so',
            'another_root/main.py'
        ])
        def mock_find_archive():
            return archive_path
        old_find_archive = support._find_archive
        support._find_archive = mock_find_archive

        # mock out creating a tmp dir to a predictable tmp dir
        tempdir = tempfile.mkdtemp()
        def mock_mkdtemp():
            return tempdir
        old_mkdtemp = tempfile.mkdtemp
        tempfile.mkdtemp = mock_mkdtemp

        # mock out the sys path
        old_sys_path = sys.path
        mock_sys_path = list(sys.path)
        sys.path = mock_sys_path

        # `import pip` can cause arbitrary sys.path changes,
        # especially if using the Debian `python-pip` package or
        # similar.  Do it first to get those changes out of the
        # way.
        try:
            import pip  # noqa
        except ImportError:
            pass
        finally:
            sys.path = old_sys_path

        # Run setup()
        old_sys_path = sys.path
        try:
            mock_sys_path = list(sys.path)
            sys.path = mock_sys_path
            support.setup(import_roots=['some_root', 'another_root'])
        finally:
            support._find_archive = old_find_archive
            tempfile.mkdtemp = old_mkdtemp
            sys.path = old_sys_path

        # Check results
        # some_root should be extracted to the tmp dir since
        # it has shared object files
        self.assertEqual(mock_sys_path[1], '{}/some_root'.format(tempdir))
        files_in_tmp_dir = os.listdir('{}/some_root'.format(tempdir))
        self.assertIn('main.py', files_in_tmp_dir)
        self.assertIn('file.so', files_in_tmp_dir)

        # another_root should just be added to sys.path since
        # there is no reason to extract it
        self.assertTrue(
            mock_sys_path[2].endswith('{}/another_root'.format(archive_path)),
            mock_sys_path)
        self.assertEqual(mock_sys_path[0], sys.path[0])
        self.assertEqual(mock_sys_path[3:], sys.path[1:])

    def _make_archive(self, filenames):
        _, archive_file = tempfile.mkstemp(suffix='.zip')
        with zipfile.ZipFile(archive_file, 'w') as archive:
            for f in filenames:
                archive.writestr(f, 'print("hello world")')
        return archive_file


if __name__ == '__main__':
    unittest.main()
