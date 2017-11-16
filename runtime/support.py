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

"""Runtime support code for executables created by Subpar.

1. Third-party modules require some PYTHONPATH manipulation.

2. Python can natively import python modules from a zip archive, but
   C extension modules require some help.

3. Resources stored in a .par file may need to be exposed as OS-level
   files instead of Python File objects.

We hook into the pkg_resources module, if present, to achieve 2 and 3.

Limitations:

A. Retrieving resources from packages

It should be possible to do this:
    fn = pkg_resources.resource_filename('mypackage', 'myfile')
But instead one must do
    fn = pkg_resources.resource_filename(
             pkg_resources.Requirement.parse.spec('mypackage'),
             'myfile')

B. Extraction dir

You should explicitly set the default extraction directory, via
`pkg_resources.set_extraction_path(my_directory)`, since the default
is not safe.  For example:

    tmpdir = tempfile.mkdtemp()
    pkg_resources.set_extraction(tmpdir)

You should arrange for that directory to be deleted at some point.
Note that pkg_resources.cleanup_resources() is an unimplemented no-op,
so use something else.  For example:

    atexit.register(lambda: shutil.rmtree(tmpdir, ignore_errors=True))

"""

import os
import pkgutil
import sys
import tempfile
import warnings
import zipfile
import zipimport


def _log(msg):
    """Print a debugging message in the same format as python -vv output"""
    if sys.flags.verbose:
        sys.stderr.write(msg)
        sys.stderr.write('\n')


def _find_archive():
    """Find the path to the currently executing .par file"""
    main = sys.modules.get('__main__')
    if not main:
        _log('# __main__ module not found')
        return None
    main_file = getattr(main, '__file__', None)
    if not main_file:
        _log('# __main__.__file__ not set')
        return None
    archive_path = os.path.dirname(main_file)
    if archive_path == '':
        _log('# unexpected __main__.__file__ is %s' % main_file)
        return None
    return archive_path


def _setup_pkg_resources(pkg_resources_name):
    """Setup hooks into the `pkg_resources` module

    This enables the pkg_resources module to find metadata from wheels
    that have been included in this .par file.

    The functions and classes here are scoped to this function, since
    we might have multitple pkg_resources modules, or none.
    """

    try:
        __import__(pkg_resources_name)
        pkg_resources = sys.modules.get(pkg_resources_name)
        if pkg_resources is None:
            return
    except ImportError:
        # Skip setup
        return

    class DistInfoMetadata(pkg_resources.EggMetadata):
        """Metadata provider for zip files containing .dist-info

        In find_dist_info_in_zip(), we call
        metadata.resource_listdir(directory_name).  However, it doesn't
        work with EggMetadata, because _zipinfo_name() expects the
        directory name to end with a /, but metadata._listdir() which
        expects the directory to _not_ end with a /.

        Therefore this class exists.
        """

        def _zipinfo_name(self, fspath):
            """Overrides EggMetadata._zipinfo_name"""
            # Convert a virtual filename (full path to file) into a
            # zipfile subpath usable with the zipimport directory
            # cache for our target archive
            while fspath.endswith(os.sep):
                fspath = fspath[:-1]
            if fspath == self.loader.archive:
                return ''
            if fspath.startswith(self.zip_pre):
                return fspath[len(self.zip_pre):]
            raise AssertionError(
                "%s is not a subpath of %s" % (fspath, self.zip_pre)
            )

        def _parts(self, zip_path):
            """Overrides EggMetadata._parts"""
            # Convert a zipfile subpath into an egg-relative path part
            # list.
            fspath = self.zip_pre + zip_path
            if fspath == self.egg_root:
                return []
            if fspath.startswith(self.egg_root + os.sep):
                return fspath[len(self.egg_root) + 1:].split(os.sep)
            raise AssertionError(
                "%s is not a subpath of %s" % (fspath, self.egg_root)
            )

    def find_dist_info_in_zip(importer, path_item, only=False):
        """Find dist-info style metadata in zip files.

        importer: PEP 302-style Importer object
        path_item (str): filename or pseudo-filename like:
            /usr/somedirs/main.par
            or
            /usr/somedirs/main.par/pypi__portpicker_1_2_0
        only (bool): We ignore the `only` flag because it's not clear
            what it should actually do in this case.

        Yields pkg_resources.Distribution objects
        """
        metadata = DistInfoMetadata(importer)
        for subitem in metadata.resource_listdir('/'):
            basename, ext = os.path.splitext(subitem)
            if ext.lower() == '.dist-info':
                # Parse distribution name
                match = pkg_resources.EGG_NAME(basename)
                project_name = 'unknown'
                if match:
                    project_name = match.group('name')
                # Create metadata object
                subpath = os.path.join(path_item, subitem)
                submeta = DistInfoMetadata(
                    zipimport.zipimporter(path_item))
                # Override pkg_resources defaults to avoid
                # "resource_filename() only supported for .egg, not
                # .zip" message
                submeta.egg_name = project_name
                submeta.egg_info = subpath
                submeta.egg_root = path_item
                dist = pkg_resources.Distribution.from_location(
                    path_item, subitem, submeta)
                yield dist

    def find_eggs_and_dist_info_in_zip(importer, path_item, only=False):
        """Chain together our finder and the standard pkg_resources finder

        For simplicity, and since pkg_resources doesn't provide a public
        interface to do so, we hardcode the chaining (find_eggs_in_zip).
        """
        # Our finder
        for dist in find_dist_info_in_zip(importer, path_item, only):
            yield dist
        # The standard pkg_resources finder
        for dist in pkg_resources.find_eggs_in_zip(importer, path_item, only):
            yield dist
        return

    # This overwrites the existing registered finder.
    pkg_resources.register_finder(zipimport.zipimporter,
                                  find_eggs_and_dist_info_in_zip)

    # Note that the default WorkingSet has already been created, and
    # there is no public interface to easily refresh/reload it that
    # doesn't also have a "Don't use this" warning.  So we manually
    # add just the entries we know about to the existing WorkingSet.
    for entry in sys.path:
        importer = pkgutil.get_importer(entry)
        if isinstance(importer, zipimport.zipimporter):
            for dist in find_dist_info_in_zip(importer, entry, only=True):
                if isinstance(dist._provider, DistInfoMetadata):
                    pkg_resources.working_set.add(dist, entry, insert=False,
                                                  replace=True)


def setup(import_roots=None):
    """Initialize subpar run-time support"""
    # Add third-party library entries to sys.path
    archive_path = _find_archive()
    if not archive_path:
        warnings.warn('Failed to initialize .par file runtime support',
                      ImportWarning)
        return

    with zipfile.ZipFile(archive_path, 'r') as archive:
        filepaths = archive.namelist()

        module_name_to_files = {}
        modules_with_shared_objs = set()
        for filename in filepaths:
            module_name = filename[:filename.find('/')]
            files = module_name_to_files.get(module_name, [])
            files.append(filename)
            module_name_to_files[module_name] = files
            if module_name not in modules_with_shared_objs and filename.endswith('.so'):
                modules_with_shared_objs.add(module_name)

        # We try to match to order of Bazel's stub
        tmp_dir = tempfile.mkdtemp()
        for import_root in reversed(import_roots or []):
            # Check to see if there are .so files in the archive
            if import_root in modules_with_shared_objs:
                for f in module_name_to_files[import_root]:
                    archive.extract(f, tmp_dir)
                new_path = os.path.join(tmp_dir, import_root)
                _log('# extracted so files for %s to %s and adding the tmp dir to sys.path' % (import_root, tmp_dir))
                sys.path.insert(1, new_path)
            else:
                new_path = os.path.join(archive_path, import_root)
                _log('# adding %s to sys.path' % new_path)
                sys.path.insert(1, new_path)

    # Add hook for package metadata
    _setup_pkg_resources('pkg_resources')
    _setup_pkg_resources('pip._vendor.pkg_resources')
