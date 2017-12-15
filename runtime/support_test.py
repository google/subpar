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

    def test__version_check(self):
        class MockModule(object): pass

        class MockOldWorkingSet(object):
            def add(self, dist, entry=None, insert=True): pass

        class MockNewWorkingSet(object):
            def add(self, dist, entry=None, insert=True, replace=False): pass

        pkg_resources = MockModule()
        self.assertFalse(support._version_check_pkg_resources(pkg_resources))

        pkg_resources.WorkingSet = MockOldWorkingSet()
        self.assertFalse(support._version_check_pkg_resources(pkg_resources))

        pkg_resources.WorkingSet = MockNewWorkingSet()
        self.assertTrue(support._version_check_pkg_resources(pkg_resources))

    def test_setup(self):
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
        # If we have no pkg_resources, or a really old version of
        # pkg_resources, setup skips some things
        module = sys.modules.get('pkg_resources', None)
        if module and support._version_check_pkg_resources(module):
            self.assertEqual(mock_sys_path[3:], sys.path[1:])


if __name__ == '__main__':
    unittest.main()
