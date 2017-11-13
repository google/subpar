# Copyright 2017 Google Inc. All Rights Reserved.
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

"""Integration test program for Subpar.

Test that pkg_resources correctly identifies distribution packages
inside a .par file.
"""


import atexit
import os
import shutil
import tempfile


def main():
    print('In pkg_resources test main()')
    try:
        import pkg_resources
        import setuptools
        # We can't query pkg_resources' version so query setuptools instead
        version = pkg_resources.parse_version(setuptools.__version__)
        minimum = pkg_resources.parse_version('36.6.0')
        if (version < minimum):
            print('Skipping test, pkg_resources module is too old')
            return
    except ImportError:
        print('Skipping test, pkg_resources module is not available')
        return

    ws = pkg_resources.working_set

    # Set a safe extraction dir (the default is unsafe)
    extraction_tmpdir = tempfile.mkdtemp()
    atexit.register(lambda: shutil.rmtree(
        extraction_tmpdir, ignore_errors=True))
    pkg_resources.set_extraction_path(extraction_tmpdir)

    # Informational for debugging
    distributions = list(ws)
    assert distributions

    # Test package that doesn't exist.
    # I hereby promise never to release a package with this name.
    nonexistent_name = 'subpar-package-does-not-exist-blorg'
    req = pkg_resources.Requirement.parse(nonexistent_name)
    dist = ws.find(req)
    assert not dist

    # Package exists, has code at the top level directory
    portpicker_spec = 'portpicker==1.2.0'
    req = pkg_resources.Requirement.parse(portpicker_spec)
    # Extract single file
    fn = pkg_resources.resource_filename(req, 'data_file.txt')
    with open(fn) as f:
        actual = f.read()
        assert actual == 'Dummy data file for portpicker\n', actual
    # Extract all
    dirname = pkg_resources.resource_filename(req, '')
    expected = [
        # The __init__.py file shouldn't be here, but is, as an
        # unfortunately side effect of Bazel runfiles behavior.
        # https://github.com/google/subpar/issues/51
        '__init__.py',
        'data_file.txt',
        'portpicker-1.2.0.dist-info',
        'portpicker.py',
    ]
    for fn in expected:
        assert os.path.exists(os.path.join(dirname, fn)), fn
    # Import module and check that we got the right one
    module = __import__(req.name)
    assert module.x == req.name, (module, vars(module))

    # Package exists, has code in a subdir
    yapf_spec = 'yapf==0.19.0'
    req = pkg_resources.Requirement.parse(yapf_spec)
    # Extract single file
    fn = pkg_resources.resource_filename(req, 'data_file.txt')
    with open(fn) as f:
        actual = f.read()
        assert actual == 'Dummy data file for yapf\n', actual
    # Extract all
    dirname = pkg_resources.resource_filename(req, '')
    expected = [
        # The __init__.py file shouldn't be here, but is, as an
        # unfortunately side effect of Bazel runfiles behavior.
        '__init__.py',
        'data_file.txt',
        'yapf',
        'yapf-0.19.0.dist-info',
    ]
    for fn in expected:
        assert os.path.exists(os.path.join(dirname, fn)), fn
    # Import module and check that we got the right one
    module = __import__(req.name)
    assert module.x == req.name, (module, vars(module))
    print("Pass")


if __name__ == '__main__':
    main()
