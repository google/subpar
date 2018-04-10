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
import subprocess
import sys
import time
import unittest
import zipfile

from subpar.compiler import error
from subpar.compiler import python_archive
from subpar.compiler import stored_resource
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
        self.main_file = test_utils.temp_file(b'print("Hello World!")',
                                              suffix='.py')
        manifest_content = '%s %s\n' % (
            os.path.basename(self.main_file.name), self.main_file.name)
        self.manifest_file = test_utils.temp_file(
            manifest_content.encode('utf8'))
        self.output_dir = os.path.join(self.tmpdir, 'output')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.output_filename = os.path.join(self.output_dir, 'output.par')
        self.interpreter = sys.executable
        self.import_roots = []
        self.date_time_tuple = (1980, 1, 1, 0, 0, 0)
        self.timestamp = 315532800
        self.zip_safe = True

    def _construct(self, manifest_filename=None):
        return python_archive.PythonArchive(
            main_filename=self.main_file.name,
            interpreter=self.interpreter,
            import_roots=self.import_roots,
            manifest_filename=(manifest_filename or self.manifest_file.name),
            manifest_root=os.getcwd(),
            output_filename=self.output_filename,
            timestamp=self.timestamp,
            zip_safe=self.zip_safe,
        )

    def test_create_manifest_not_found(self):
        par = self._construct(
            manifest_filename=os.path.join(self.input_dir, 'doesnotexist'))
        with self.assertRaises(IOError):
            par.create()

    def test_create_manifest_parse_error(self):
        with test_utils.temp_file(b'blah blah blah\n') as manifest_file:
            par = self._construct(manifest_filename=manifest_file.name)
            with self.assertRaises(error.Error):
                par.create()

    def test_create_manifest_contains___main___py(self):
        with test_utils.temp_file(b'__main__.py\n') as manifest_file:
            par = self._construct(manifest_filename=manifest_file.name)
            with self.assertRaises(error.Error):
                par.create()

    def test_create_source_file_not_found(self):
        with test_utils.temp_file(b'foo.py doesnotexist.py\n') as manifest_file:
            par = self._construct(manifest_filename=manifest_file.name)
            with self.assertRaises((IOError, OSError)):
                par.create()

    def test_create_permission_denied_creating_temp_file(self):
        os.rmdir(self.output_dir)
        with self.assertRaises(OSError):
            par = self._construct()
            par.create()

    def test_create_permission_denied_creating_final_file(self):
        par = self._construct()
        saved = par.write_zip_data

        def mock(*args):
            par.output_filename = "/nonexistent" + par.output_filename
            return saved(*args)

        par.write_zip_data = mock
        with self.assertRaises(OSError):
            par.create()

    def test_create(self):
        par = self._construct()
        par.create()
        self.assertTrue(os.path.exists(self.output_filename))
        self.assertEqual(
            subprocess.check_output([self.output_filename]), b'Hello World!\n')

    def test_create_deterministic(self):
        par1 = self._construct()
        self.output_filename = self.output_filename + '2'
        par2 = self._construct()

        par1.create()
        # Sleep for 3 seconds, which is greater than the 2-second
        # granularity of zip timestamps
        time.sleep(3)
        par2.create()

        # The two par files should be bit-for-bit identical
        content1 = open(par1.output_filename, 'rb').read()
        content2 = open(par2.output_filename, 'rb').read()
        self.assertEqual(content1, content2)

    def test_create_temp_parfile(self):
        par = self._construct()
        with par.create_temp_parfile() as t:
            self.assertTrue(os.path.exists(t.name))
        # t closed but not deleted
        self.assertTrue(os.path.exists(t.name))

    def test_generate_boilerplate(self):
        par = self._construct()
        boilerplate = par.generate_boilerplate(['foo', 'bar'])
        self.assertIn('Boilerplate', boilerplate)
        self.assertIn("import_roots=['foo', 'bar']", boilerplate)

    def test_generate_main(self):
        par = self._construct()
        boilerplate = 'BOILERPLATE\n'
        cases = [
            # Insert at beginning
            (b'spam = eggs\n',
             b'BOILERPLATE\nspam = eggs\n'),
            # Insert in the middle
            (b'# a comment\nspam = eggs\n',
             b'# a comment\nBOILERPLATE\nspam = eggs\n'),
            # Insert after the end
            (b'# a comment\n',
             b'# a comment\nBOILERPLATE\n'),
            # Blank lines
            (b'\n \t\n',
             b'\n \t\nBOILERPLATE\n'),
            # Future import
            (b'from __future__ import print_function\n',
             b'from __future__ import print_function\nBOILERPLATE\n'),
            # Module docstrings
            (b"'Single-quote Module docstring'\n",
             b"'Single-quote Module docstring'\nBOILERPLATE\n"),
            (b'"Double-quote Module docstring"\n',
             b'"Double-quote Module docstring"\nBOILERPLATE\n'),
            (b"'''Triple-single-quote module \"'\n\n docstring'''\n",
             b"'''Triple-single-quote module \"'\n\n docstring'''\nBOILERPLATE\n"),
            (b'"""Triple-double-quote module "\'\n\n docstring"""\n',
             b'"""Triple-double-quote module "\'\n\n docstring"""\nBOILERPLATE\n'),
        ]
        for main_content, expected in cases:
            with test_utils.temp_file(main_content) as main_file:
                actual = par.generate_main(main_file.name, boilerplate)
            self.assertEqual(expected, actual.content)

    def test_scan_manifest(self):
        par = self._construct()
        manifest = {'foo.py': '/something/foo.py', 'bar.py': None}
        resources = par.scan_manifest(manifest)
        self.assertIn('foo.py', resources)
        self.assertIn('bar.py', resources)

    def test_scan_manifest_adds_workspace_roots(self):
        par = self._construct()
        manifest = {'foo': None, 'bar/': None, 'baz/quux': None}
        resources = par.scan_manifest(manifest)
        self.assertIn(b"import_roots=['bar', 'baz']",
                      resources['__main__.py'].content)

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
        with test_utils.temp_file(b'blah blah\n') as shadowing_support_file:
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
        # Create simple .par file
        par = self._construct()
        with par.create_temp_parfile() as output_file:
            stored_name = os.path.basename(self.main_file.name)
            resource = stored_resource.StoredFile(
                stored_name, self.date_time_tuple, self.main_file.name)
            resources = {resource.zipinfo.filename: resource}
            par.write_zip_data(output_file, resources)
        output_file.close()

        # Check that it's a valid zipfile
        self.assertTrue(zipfile.is_zipfile(output_file.name))

        # Check that the file was stored correctly
        z = zipfile.ZipFile(output_file.name)
        zipinfo = z.getinfo(stored_name)
        self.assertEqual(zipinfo.date_time, self.date_time_tuple)

    def test_create_final_from_temp(self):
        par = self._construct()
        t = par.create_temp_parfile()
        t.close()
        par.create_final_from_temp(t.name)
        self.assertFalse(os.path.exists(t.name))
        self.assertTrue(os.path.exists(self.output_filename))


class ModuleTest(unittest.TestCase):
    """Test module scope functions"""

    def setUp(self):
        self.date_time_tuple = (1980, 1, 1, 0, 0, 0)

    def test_remove_if_present(self):
        tmpdir = test_utils.mkdtemp()
        filename = os.path.join(tmpdir, 'afile')
        with open(filename, 'wb') as f:
            f.write(b'dontcare')
        # File exists
        self.assertTrue(os.path.exists(filename))
        python_archive.remove_if_present(filename)
        self.assertFalse(os.path.exists(filename))
        # File doesn't exist
        python_archive.remove_if_present(filename)
        self.assertFalse(os.path.exists(filename))

    def test_fetch_support_file(self):
        resource = python_archive.fetch_support_file(
            'support.py', self.date_time_tuple)
        self.assertEqual(resource.zipinfo.filename, 'subpar/runtime/support.py')


if __name__ == '__main__':
    unittest.main()
