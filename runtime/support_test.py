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
import sys
import unittest
import mock
import tempfile
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

    # patch zipfile because there is no real zipfile
    @mock.patch('zipfile.ZipFile')
    def test_setup(self, ZipFileMock):
        # test when there are no .so files in the archive
        ZipFileMock.return_value.__enter__.return_value.namelist.return_value = [
            'some_root/main.py',
            'another_root/main.py'
        ]
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
            sys.path = old_sys_path

        # Check results
        self.assertTrue(mock_sys_path[1].endswith('subpar/runtime/some_root'),
                        mock_sys_path)
        self.assertTrue(
            mock_sys_path[2].endswith('subpar/runtime/another_root'),
            mock_sys_path)
        self.assertEqual(mock_sys_path[0], sys.path[0])
        self.assertEqual(mock_sys_path[3:], sys.path[1:])

        # Make sure nothing got extracted, since there are no shared object files
        ZipFileMock.return_value.__enter__.return_value.extract.assert_not_called()

    @mock.patch.object(tempfile, 'mkdtemp', return_value='/some_tmp_dir')
    @mock.patch('zipfile.ZipFile')
    def test_setup_with_shared_objects(self, ZipFileMock, mkdtemp_mock):
        ZipFileMock.return_value.__enter__.return_value.namelist.return_value = [
            'some_root/main.py',
            'some_root/file.so',
            'another_root/main.py'
        ]
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
            sys.path = old_sys_path

        # Check results
        # some_root should be extracted to the tmp dir since
        # it has shared object files
        self.assertEqual(mock_sys_path[1], '/some_tmp_dir/some_root')
        calls = [
            mock.call('some_root/main.py', '/some_tmp_dir'),
            mock.call('some_root/file.so', '/some_tmp_dir')
        ]
        ZipFileMock.return_value.__enter__.return_value.extract.assert_has_calls(calls)

        # another_root should just be added to sys.path since
        # there is no reason to extract it
        self.assertTrue(
            mock_sys_path[2].endswith('subpar/runtime/another_root'),
            mock_sys_path)
        self.assertEqual(mock_sys_path[0], sys.path[0])
        self.assertEqual(mock_sys_path[3:], sys.path[1:])


if __name__ == '__main__':
    unittest.main()
