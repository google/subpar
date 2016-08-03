#!/usr/bin/python2

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
import stat
import subprocess
import unittest
import zipfile

from subpar.compiler import error
from subpar.compiler import stored_resource
from subpar.compiler import python_archive
from subpar.compiler import test_utils


# pylint: disable=too-many-instance-attributes
class PythonArchiveTest(unittest.TestCase):
    """Test PythonArchive class"""

    def setUp(self):
        # Setup directory structure and files
        self.tmpdir = test_utils.mkdtemp()
        self.input_dir = os.path.join(self.tmpdir, 'input')
        if not os.path.exists(self.input_dir):
            os.makedirs(self.input_dir)
        self.manifest_filename = os.path.join(self.input_dir, 'manifest')
        self.main_file = test_utils.temp_file('print("Hello World!")',
                                              suffix='.py')
        self.manifest_file = test_utils.temp_file(
            '%s %s\n' %
            (os.path.basename(self.main_file.name), self.main_file.name))
        self.output_dir = os.path.join(self.tmpdir, 'output')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.output_filename = os.path.join(self.output_dir, 'output.par')
        self.interpreter = '/usr/bin/python2'
        self.import_roots = []

    def _construct(self, manifest_filename=None):
        return python_archive.PythonArchive(
            main_filename=self.main_file.name,
            interpreter=self.interpreter,
            import_roots=self.import_roots,
            manifest_filename=(manifest_filename or self.manifest_file.name),
            manifest_root=os.getcwd(),
            output_filename=self.output_filename,
        )

    def test_create_manifest_not_found(self):
        par = self._construct(
            manifest_filename=os.path.join(self.input_dir, 'doesnotexist'))
        with self.assertRaises(IOError):
            par.create()

    def test_create_manifest_parse_error(self):
        with test_utils.temp_file('blah blah blah\n') as manifest_file:
            par = self._construct(manifest_filename=manifest_file.name)
            with self.assertRaises(error.Error):
                par.create()

    def test_create_manifest_contains___main___py(self):
        with test_utils.temp_file('__main__.py\n') as manifest_file:
            par = self._construct(manifest_filename=manifest_file.name)
            with self.assertRaises(error.Error):
                par.create()

    def test_create_source_file_not_found(self):
        with test_utils.temp_file('foo.py doesnotexist.py\n') as manifest_file:
            par = self._construct(manifest_filename=manifest_file.name)
            with self.assertRaises(OSError):
                par.create()

    def test_create_permission_denied_creating_temp_file(self):
        st = os.stat(self.output_dir)
        try:
            os.chmod(self.output_dir, stat.S_IREAD)
            with self.assertRaises(OSError):
                par = self._construct()
                par.create()
        finally:
            os.chmod(self.output_dir, st.st_mode)

    def test_create_permission_denied_creating_final_file(self):
        st = os.stat(self.output_dir)
        try:
            par = self._construct()
            saved = par.write_zip_data

            def mock(*args):
                os.chmod(self.output_dir, stat.S_IREAD)
                return saved(*args)

            par.write_zip_data = mock
            with self.assertRaises(OSError):
                par.create()
        finally:
            os.chmod(self.output_dir, st.st_mode)

    def test_create(self):
        par = self._construct()
        par.create()
        self.assertTrue(os.path.exists(self.output_filename))
        self.assertEqual(
            subprocess.check_output([self.output_filename]), 'Hello World!\n')

    def test_create_temp_parfile(self):
        par = self._construct()
        with par.create_temp_parfile() as t:
            self.assertTrue(os.path.exists(t.name))
        # t closed but not deleted
        self.assertTrue(os.path.exists(t.name))

    def test_scan_manifest(self):
        par = self._construct()
        manifest = {'foo.py': '/something/foo.py', 'bar.py': None,}
        resources = par.scan_manifest(manifest)
        self.assertIn('foo.py', resources)
        self.assertIn('bar.py', resources)

    def test_scan_manifest_adds_main(self):
        par = self._construct()
        resources = par.scan_manifest({})
        self.assertIn('__main__.py', resources)

    def test_scan_manifest_adds_support(self):
        par = self._construct()
        resources = par.scan_manifest({})
        # Adds explicit source files
        self.assertIn('subpar/runtime/support.py', resources)
        # Adds package init files
        self.assertIn('subpar/__init__.py', resources)

    def test_scan_manifest_has_collision(self):
        par = self._construct()
        # Support file already present in manifest, use manifest version
        with test_utils.temp_file('blah blah\n') as shadowing_support_file:
            manifest = {
                'foo.py': '/something/foo.py',
                'subpar/runtime/support.py': shadowing_support_file.name,
            }
            resources = par.scan_manifest(manifest)
            self.assertEqual(
                resources['subpar/runtime/support.py'].local_filename,
                shadowing_support_file.name)

    def test_write_bootstrap(self):
        par = self._construct()
        with par.create_temp_parfile() as t:
            par.write_bootstrap(t)
            t.seek(0)
            actual = t.read()
            self.assertNotEqual(actual, '')

    def test_write_zip_data(self):
        par = self._construct()
        with par.create_temp_parfile() as t:
            resource = stored_resource.StoredFile(
                os.path.basename(self.main_file.name), self.main_file.name)
            resources = {resource.stored_filename: resource,}
            par.write_zip_data(t, resources)
        self.assertTrue(zipfile.is_zipfile(t.name))

    def test_create_final_from_temp(self):
        par = self._construct()
        t = par.create_temp_parfile()
        t.close()
        par.create_final_from_temp(t.name)
        self.assertFalse(os.path.exists(t.name))
        self.assertTrue(os.path.exists(self.output_filename))


class ModuleTest(unittest.TestCase):
    """Test module scope functions"""

    def test_remove_if_present(self):
        tmpdir = test_utils.mkdtemp()
        filename = os.path.join(tmpdir, 'afile')
        with open(filename, 'wb') as f:
            f.write('dontcare')
        # File exists
        self.assertTrue(os.path.exists(filename))
        python_archive.remove_if_present(filename)
        self.assertFalse(os.path.exists(filename))
        # File doesn't exist
        python_archive.remove_if_present(filename)
        self.assertFalse(os.path.exists(filename))


if __name__ == '__main__':
    unittest.main()
