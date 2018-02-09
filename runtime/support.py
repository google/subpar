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

import atexit
import os
import pkgutil
import shutil
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
    """Find the path to the currently executing .par file

    We don't handle the case where prefix is non-empty.
    """
    main = sys.modules.get('__main__')
    if not main:
        _log('# __main__ module not found')
        return None
    main_loader = getattr(main, '__loader__')
    if not main_loader:
        _log('# __main__.__loader__ not set')
        return None
    prefix = getattr(main_loader, 'prefix')
    if prefix != '':
        _log('# unexpected prefix for __main__.__loader__ is %s' %
             main_loader.prefix)
        return None
    archive_path = getattr(main_loader, 'archive')
    if not archive_path:
        _log('# missing archive for __main__.__loader__')
        return None
    return archive_path


def _extract_files(archive_path):
    """Extract the contents of this .par file to disk.

    This creates a temporary directory, and registers an atexit
    handler to clean that directory on program exit.  Extraction and
    cleanup will potentially use significant time and disk space.

    Returns:
        Directory where contents were extracted to.
    """
    extract_dir = tempfile.mkdtemp()

    def _extract_files_cleanup():
        shutil.rmtree(extract_dir, ignore_errors=True)
    atexit.register(_extract_files_cleanup)
    _log('# extracting %s to %s' % (archive_path, extract_dir))

    zip_file = zipfile.ZipFile(archive_path, mode='r')
    zip_file.extractall(extract_dir)
    zip_file.close()

    return extract_dir


def _version_check_pkg_resources(pkg_resources):
    """Check that pkg_resources supports the APIs we need."""
    # Check that pkg_resources is new enough.
    #
    # Determining the version of an arbitrarily old version of
    # pkg_resources is tough, since it doesn't have a version literal,
    # and the accompanying setuptools package computes its version
    # dynamically from metadata that might not exist.  Also setuptools
    # might not exist, especially in the case of the pip-vendored copy
    # of pkg_resources.
    #
    # We do a feature detection instead.  We examine
    # pkg_resources.WorkingSet.add, and see if it has at least the
    # third default argument ('replace').
    try:
        if sys.version_info[0] < 3:
            defaults = pkg_resources.WorkingSet.add.im_func.func_defaults
        else:
            defaults = pkg_resources.WorkingSet.add.__defaults__
        return len(defaults) >= 3
    except AttributeError:
        return False


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

    if not _version_check_pkg_resources(pkg_resources):
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
            fspath = fspath.rstrip(os.sep)
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


def _initialize_import_path(import_roots, import_prefix):
    """Add extra entries to PYTHONPATH so that modules can be imported."""
    # We try to match to order of Bazel's stub
    full_roots = [
        os.path.join(import_prefix, import_root)
        for import_root in import_roots]
    sys.path[1:1] = full_roots
    _log('# adding %s to sys.path' % full_roots)


def setup(import_roots, zip_safe):
    """Initialize subpar run-time support

    Args:
      import_root (list): subdirs inside .par file to add to the
                          module import path at runtime.
      zip_safe (bool): If False, extract the .par file contents to a
                       temporary directory, and import everything from
                       that directory.

    Returns:
      True if setup was successful, else False
    """
    archive_path = _find_archive()
    if not archive_path:
        warnings.warn('Failed to initialize .par file runtime support',
                      UserWarning)
        return False
    if os.path.abspath(sys.path[0]) != os.path.abspath(archive_path):
        warnings.warn('Failed to initialize .par file runtime support. ' +
                      'archive_path was %r, sys.path was %r' % (
                          archive_path, sys.path),
                      UserWarning)
        return False

    # Extract files to disk if necessary
    if not zip_safe:
        extract_dir = _extract_files(archive_path)
        # sys.path[0] is the name of the executing .par file.  Point
        # it to the extract directory instead, so that Python searches
        # there for imports.
        sys.path[0] = extract_dir
        import_prefix = extract_dir
    else:  # Import directly from .par file
        extract_dir = None
        import_prefix = archive_path

    # Initialize import path
    _initialize_import_path(import_roots, import_prefix)

    # Add hook for package metadata
    _setup_pkg_resources('pkg_resources')
    _setup_pkg_resources('pip._vendor.pkg_resources')

    return True
