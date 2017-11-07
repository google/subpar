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

We try a succession of different strategies until we find one that
works.

TODO: Strategy: FUSE filesystem
TODO: Strategy: dlopen_with_offset
TODO: Strategy: extract all files to a temp dir
TODO: Strategy: Do nothing if archive doesn't have any C extension modules

"""

import os
import pkgutil
import sys
import warnings
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

        def _listdir(self, fspath):
            """List of resource names in the directory (like ``os.listdir()``)

            Overrides EggMetadata._listdir()
            """

            zipinfo_name = self._zipinfo_name(fspath)
            while zipinfo_name.endswith('/'):
                zipinfo_name = zipinfo_name[:-1]
            result = self._index().get(zipinfo_name, ())
            return list(result)


    def find_dist_info_in_zip(importer, path_item, only=False):
        """Find dist-info style metadata in zip files.

        We ignore the `only` flag because it's not clear what it should
        actually do in this case.
        """
        metadata = DistInfoMetadata(importer)
        for subitem in metadata.resource_listdir('/'):
            if subitem.lower().endswith('.dist-info'):
                subpath = os.path.join(path_item, subitem)
                submeta = pkg_resources.EggMetadata(zipimport.zipimporter(subpath))
                submeta.egg_info = subpath
                dist = pkg_resources.Distribution.from_location(path_item, subitem, submeta)
                yield dist
        return


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
                pkg_resources.working_set.add(dist, entry, insert=False,
                                              replace=False)


def setup(import_roots=None):
    """Initialize subpar run-time support"""
    # Add third-party library entries to sys.path
    archive_path = _find_archive()
    if not archive_path:
        warnings.warn('Failed to initialize .par file runtime support',
                      ImportWarning)
        return

    # We try to match to order of Bazel's stub
    for import_root in reversed(import_roots or []):
        new_path = os.path.join(archive_path, import_root)
        _log('# adding %s to sys.path' % new_path)
        sys.path.insert(1, new_path)

    # Add hook for package metadata
    _setup_pkg_resources('pkg_resources')
    _setup_pkg_resources('pip._vendor.pkg_resources')
