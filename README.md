# Subpar (deprecated)

[![Build Status](https://travis-ci.org/google/subpar.svg?branch=master)](https://travis-ci.org/google/subpar)

Subpar is a utility for creating self-contained python executables.  It is
designed to work well with [Bazel](https://bazel.build/).

## Status

This project is unmaintained and considered deprecated.
Historically, subpar was the only way to produce a deployable Python artifact in Bazel. 
This is no longer true; `--build_python_zip` and the `python_zip_file` output_group allows you to create executable Python zip artifacts with the standard `py_binary` rule.
`rules_docker` can also be used to build container images that launch `py_binary`.

## Setup

* Add the following to your WORKSPACE file:

```python
git_repository(
    name = "subpar",
    remote = "https://github.com/google/subpar",
    tag = "1.0.0",
)
```

* Add the following to the top of any BUILD files that declare `par_binary()`
  rules:

```python
load("@subpar//:subpar.bzl", "par_binary")
```

## Usage

`par_binary()` is a drop-in replacement for `py_binary()` in your BUILD files
that also builds a self-contained, single-file executable for the application,
with a `.par` file extension.

To build the `.par` file associated with a `par_binary(name=myname)` rule, do

``` shell
bazel build //my/package:myname.par
```

The .par file is created alongside the python stub and .runfiles
directories that py_binary() creates, but is independent of them.
It can be copied to other directories or machines, and executed
directly without needing the .runfiles directory. The body of the
.par file contains all the srcs, deps, and data files listed.

## Limitations:

* C extension modules in 'deps' is not yet supported
* Automatic re-extraction of '.runfiles' is not yet supported
* Does not include a copy of the Python interpreter ('hermetic .par')

## Example

Given a `BUILD` file with the following:

```python
load("@subpar//:subpar.bzl", "par_binary")

par_binary(
    name = 'foo',
    srcs = ['foo.py', 'bar.py'],
    deps = ['//baz:some_py_lib'],
    data = ['quux.dat'],
)
```

Run the following build command:

``` shell
bazel build //package:foo.par
```

This results in the following files being created by bazel build:

```
bazel-bin/
    package/
        foo
        foo.par
        foo.runfiles/
            ...
```

The .par file can be copied, moved, or renamed, and still run like a
compiled executable file:

```
$ scp bazel-bin/package/foo.par my-other-machine:foo.par
$ ssh my-other-machine ./foo.par
```

## System Requirements

* Python Versions: CPython versions 2.7.6+
* Operating Systems: Debian-derived Linux, including Ubuntu and Goobuntu.

# DISCLAIMER

This is not an official Google product, it is just code that happens
to be owned by Google.
