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

"""Build self-contained python executables."""

load("//:debug.bzl", "dump")

def _parfile_impl(ctx):
    """Implementation of parfile() rule"""
    # Find the main entry point
    py_files = ctx.files.main
    if len(py_files) == 0:
        fail('Expected exactly one .py file, found none', 'main')
    elif len(py_files) > 1:
        fail('Expected exactly one .py file, found these: [%s]' % py_files, 'main')
    main_py_file = py_files[0]
    if main_py_file not in ctx.attr.src.data_runfiles.files:
        fail('Main entry point [%s] not listed in srcs' % main_py_file, 'main')

    # Find the list of things that must be built before this thing is built
    # TODO: also handle ctx.attr.src.data_runfiles.symlinks
    inputs = list(ctx.attr.src.default_runfiles.files)

    # Make a manifest of files to store in the .par file.  The
    # runfiles manifest is not quite right, so we make our own.
    sources_map = {}
    # First, add the zero-length __init__.py files
    for empty in ctx.attr.src.default_runfiles.empty_filenames:
        stored_path = _prepend_workspace(empty, ctx)
        local_path = ''
        sources_map[stored_path] = local_path
    # Now add the regular (source and generated) files
    for input_file in inputs:
        stored_path = _prepend_workspace(input_file.short_path, ctx)
        local_path = input_file.path
        sources_map[stored_path] = local_path
    # Now make a nice sorted list
    sources_lines = []
    for k,v in sorted(sources_map.items()):
        sources_lines.append('%s %s' % (k, v))
    sources_content = '\n'.join(sources_lines) + '\n'

    # Write the list to the manifest file
    sources_file = ctx.new_file(ctx.label.name + '_SOURCES')
    ctx.file_action(
        output=sources_file,
        content=sources_content,
        executable=False)

    # Find the list of directories to add to sys.path
    # TODO(b/29227737): Use 'imports' provider from Bazel
    stub_file = ctx.attr.src.files_to_run.executable.path

    # Inputs to the action, but don't actually get stored in the .par file
    extra_inputs = [
        sources_file,
        ctx.attr.src.files_to_run.executable,
        ctx.attr.src.files_to_run.runfiles_manifest,
        ]

    # Assemble command line for .par compiler
    args = [
        '--manifest_file', sources_file.path,
        '--outputpar', ctx.outputs.executable.path,
        '--stub_file', stub_file,
        main_py_file.path,
    ]
    ctx.action(
        inputs=inputs + extra_inputs,
        outputs=[ctx.outputs.executable],
        progress_message='Building par file %s' % ctx.label,
        executable=ctx.executable.compiler,
        arguments=args,
        mnemonic='PythonCompile',
    )

    # .par file itself has no runfiles and no providers
    return struct()

def _prepend_workspace(path, ctx):
    """Given a path, prepend the workspace name as the parent directory"""
    # It feels like there should be an easier, less fragile way.
    if path.startswith('../'):
        # External workspace
        stored_path = path[len('../'):]
    else:
        # Main workspace
        stored_path = ctx.workspace_name + '/' + path
    return stored_path

# Rule to create a parfile given a py_binary() as input
parfile = rule(
    attrs = {
        "src": attr.label(mandatory = True),
        "main": attr.label(
            mandatory = True,
            allow_files = True,
            single_file = True,
        ),
        "imports": attr.string_list(default = []),
        "default_python_version": attr.string(mandatory = True),
        "compiler": attr.label(
            default = Label("//compiler:compiler.par"),
            executable = True,
        ),
    },
    executable = True,
    implementation = _parfile_impl,
)

"""A self-contained, single-file Python program, with a .par file extension.

You probably want to use par_binary() instead of this.

Args:
  src: A py_binary() target
  main: The name of the source file that is the main entry point of
    the application.

    See [py_binary.main](http://www.bazel.io/docs/be/python.html#py_binary.main)

  imports: List of import directories to be added to the PYTHONPATH.

    See [py_binary.imports](http://www.bazel.io/docs/be/python.html#py_binary.imports)

  default_python_version: A string specifying the default Python major version to use when building this par file.

    See [py_binary.default_python_version](http://www.bazel.io/docs/be/python.html#py_binary.default_python_version)

  compiler: Internal use only.

TODO(b/27502830): A directory foo.par.runfiles is also created. This
is a bug, don't use or depend on it.

"""

def par_binary(name, **kwargs):
    """An executable Python program.

    par_binary() is a drop-in replacement for py_binary() that also
    builds a self-contained, single-file executable for the
    application, with a .par file extension.

    See [py_binary](http://www.bazel.io/docs/be/python.html#py_binary)
    for arguments and usage.

    """
    native.py_binary(name=name, **kwargs)
    main = kwargs.get('main', name + '.py')
    imports = kwargs.get('imports')
    default_python_version = kwargs.get('default_python_version', 'PY2')
    parfile(name=name + '.par', src=name, main=main, imports=imports,
            default_python_version=default_python_version)
