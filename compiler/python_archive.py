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

"""Build a single-file executable from multiple python source files.

The final product is a hybrid file.  The start of the file is a Unix
shell script or similar, the end of the file is a ZIP archive.  This
actually works.

It is inspired by the TinyPar tool by Springer, which is inspired by
the Autopar tool by Greiman.  It is less capable than either of these
tools, but is not tied to internal Google tools or infrastructure.
The command line flags and environment variables are intended to match
those two tools.

See also https://www.python.org/dev/peps/pep-0441/

"""

import io
import logging
import os
import pkgutil
import re
import sys
import tempfile
import zipfile

from subpar.compiler import error
from subpar.compiler import manifest_parser
from subpar.compiler import stored_resource

# Boilerplate code added to __main__.py
_boilerplate_template = """\
# Boilerplate added by subpar/compiler/python_archive.py
from %(runtime_package)s import support as _
_.setup(import_roots=%(import_roots)s)
del _
# End boilerplate
"""

# Fully qualified names of subpar packages
_subpar_package = 'subpar'
_compiler_package = _subpar_package + '.compiler'
_runtime_package = _subpar_package + '.runtime'

# List of files from the runtime package to include in every .par file
_runtime_support_files = ['support.py',]

# List of zero-length files to include in every .par file
_runtime_init_files = [
    'subpar/__init__.py',
    'subpar/runtime/__init__.py',
]


class PythonArchive(object):
    """Contains all the necessary information to generate a .par file"""

    # pylint: disable=too-many-arguments
    def __init__(self,
                 main_filename,
                 import_roots,
                 interpreter,
                 manifest_filename,
                 manifest_root,
                 output_filename,
                ):
        self.main_filename = main_filename

        self.import_roots = import_roots
        self.interpreter = interpreter
        self.manifest_filename = manifest_filename
        self.manifest_root = manifest_root
        self.output_filename = output_filename

        self.compression = zipfile.ZIP_DEFLATED

    def create(self):
        """Create a .par file on disk

        Raises:
            Error, IOError, SystemError
        """
        logging.info('Compiling under python %s...', sys.version)
        logging.info('Making parfile [%s]...', self.output_filename)
        remove_if_present(self.output_filename)

        # Assemble list of files to include
        logging.debug('Compiling file list from [%s]', self.manifest_filename)
        manifest = manifest_parser.parse(self.manifest_filename)

        # Validate manifest and add various extra files to the list
        stored_resources = self.scan_manifest(manifest)

        # Create parfile in temporary file
        temp_parfile = self.create_temp_parfile()
        try:
            logging.debug('Writing parfile to temp file [%s]...',
                          temp_parfile.name)
            self.write_bootstrap(temp_parfile)
            self.write_zip_data(temp_parfile, stored_resources)
            temp_parfile.close()
            # Flushed and closed tempfile, may now rename it safely
            self.create_final_from_temp(temp_parfile.name)
        finally:
            remove_if_present(temp_parfile.name)
        logging.info('Success!')

    def create_temp_parfile(self):
        """Create the first part of a parfile.

        Returns:
            A file-like object with a 'name' attribute
        """
        # Create in same directory as final filename so we can atomically rename
        output_dir = os.path.dirname(self.output_filename)
        return tempfile.NamedTemporaryFile(dir=output_dir, delete=False)

    def generate_boilerplate(self, import_roots):
        """Generate boilerplate to be insert into __main__.py

        We don't know the encoding of the main source file, so
        require that the template be pure ascii, which we can safely
        insert.

        Returns:
            A string containing only ascii characters
        """
        boilerplate_contents = _boilerplate_template % {
            'runtime_package': _runtime_package,
            'import_roots': str(import_roots),
        }
        return boilerplate_contents.encode('ascii').decode('ascii')

    def generate_main(self, main_filename, boilerplate_contents):
        """Generate the contents of the __main__.py file

        We take the module that is specified as the main entry point,
        and insert some boilerplate to invoke import helper code.

        Returns:
            A StoredResource
        """
        # Read main source file, in unknown encoding.  We use latin-1
        # here, but any single-byte encoding that doesn't raise errors
        # would work.
        output_lines = []
        with io.open(main_filename, 'rt', encoding='latin-1') as main_file:
            output_lines = list(main_file)

        # Find a good place to insert the boilerplate, which is the
        # first line that is not a comment, blank line, or future
        # import.
        skip_regex = re.compile('''(#.*)|(\\s+)|(from\\s+__future__\\s+import)''')
        idx = 0
        while idx < len(output_lines):
            if not skip_regex.match(output_lines[idx]):
                break
            idx += 1

        # Insert boilerplate (might be beginning, middle or end)
        output_lines[idx:idx] = [boilerplate_contents]
        contents = ''.join(output_lines).encode('latin-1')
        return stored_resource.StoredContent('__main__.py', contents)

    def scan_manifest(self, manifest):
        """Return a dict of StoredResources based on an input manifest.

        Returns:
            A dict of store_filename to StoredResource
        """

        # Extend the list of import roots to include workspace roots
        top_roots = set()
        for stored_path in manifest.keys():
            if '/' in stored_path:  # Zip file paths use / on all platforms
                top_dir = stored_path.split('/', 1)[0]
                if top_dir not in top_roots:
                    top_roots.add(top_dir)
        import_roots = list(self.import_roots) + sorted(top_roots)

        # Include some files that every .par file needs at runtime
        stored_resources = {}
        for support_file in _runtime_support_files:
            resource = fetch_support_file(support_file)
            stored_filename = resource.stored_filename
            stored_resources[stored_filename] = resource

        # Scan manifest
        for stored_path, local_path in manifest.items():
            if local_path is None:
                stored_resources[stored_path] = stored_resource.EmptyFile(
                    stored_path)
            else:
                stored_resources[stored_path] = stored_resource.StoredFile(
                    stored_path, local_path)

        # Copy main entry point to well-known name
        if '__main__.py' in stored_resources:
            raise error.Error(
                ('Configuration error for [%s]: Manifest file included a '
                 'file named __main__.py, which is not allowed') %
                self.manifest_filename)
        stored_resources['__main__.py'] = self.generate_main(
            self.main_filename, self.generate_boilerplate(import_roots))

        # Add an __init__.py for each parent package of the support files
        for stored_filename in _runtime_init_files:
            if stored_filename in stored_resources:
                logging.debug('Skipping __init__.py already present [%s]',
                              stored_filename)
                continue
            stored_resources[stored_filename] = stored_resource.EmptyFile(
                stored_filename)

        return stored_resources

    def write_bootstrap(self, temp_parfile):
        """Write the first part of the parfile

        This tells the operating system (well, UNIX) how to execute the file.
        """
        logging.debug('Writing boilerplate...')
        boilerplate = '#!%s\n' % self.interpreter
        temp_parfile.write(boilerplate.encode('ascii'))

    def write_zip_data(self, temp_parfile, stored_resources):
        """Write the second part of a parfile, consisting of ZIP data

        Args:
            stored_resources: A dictionary mapping relative path to the
            content to store at that path.
        """

        logging.debug('Storing Files...')
        with zipfile.ZipFile(temp_parfile, 'w', self.compression) as z:
            items = sorted(stored_resources.items())
            for relative_path, resource in items:
                assert resource.stored_filename == relative_path
                resource.store(z)

    def create_final_from_temp(self, temp_parfile_name):
        """Move newly created parfile to its final filename."""
        # Python 2 doesn't have os.replace, so use os.rename which is
        # not atomic in all cases.
        os.chmod(temp_parfile_name, 0o0755)
        os.rename(temp_parfile_name, self.output_filename)


def remove_if_present(filename):
    """Delete any existing file"""
    if os.path.exists(filename):
        os.remove(filename)


def fetch_support_file(name):
    """Read a file from the runtime package

    Args:
        name: filename in runtime package's directory

    Returns:
        A StoredResource representing the content of that file
    """
    stored_filename = os.path.join(_subpar_package, 'runtime', name)
    content = pkgutil.get_data(_subpar_package, 'runtime/' + name)
    # content is None means the file wasn't found.  content == '' is
    # valid, it means the file was found and was empty.
    if content is None:
        raise error.Error(
            'Internal error: Can\'t find runtime support file [%s]' % name)
    return stored_resource.StoredContent(stored_filename, content)
