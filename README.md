# Subpar

Subpar is a utility for creating self-contained python executables.  It is
designed to work well with [Bazel](http://bazel.io).

## Setup

* Add the following to your WORKSPACE file:

```python
git_repository(
    name = "subpar",
    remote = "https://github.com/google/subpar",
    commit = "HEAD",
)
```

* Add the following to the top of any BUILD files that declare `par_binary()`
  rules:

```python
load("@subpar//:subpar.bzl", "par_binary")
```

## Usage

`par_binary()` is a drop-in replacement for `py_binary()` that also builds a
self-contained, single-file executable for the application, with a `.par` file
extension.

The .par file is created alongside the python stub and .runfiles
directories that py_binary() creates, but is independent of them.
It can be copied to other directories or machines, and executed
directly without needing the .runfiles directory.  The body of the
.par file contains all the srcs, deps, and data files listed.

## Limitations:

* C extension modules in 'deps' is not yet supported
* Automatic re-extraction of '.runfiles' is not yet supported
* Python 3 is not yet supported
* Does not include a copy of the Python interpreter ('hermetic .par')

## Example

```python
par_binary(
    name = 'foo',
    srcs = ['foo.py', 'bar.py'],
    deps = ['//baz:some_py_lib'],
    data = ['quux.dat'],
)
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
