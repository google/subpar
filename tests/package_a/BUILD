# Test package for Subpar

load("@rules_python//python:defs.bzl", "py_library")
load("//:subpar.bzl", "par_binary")

package(default_visibility = ["//tests:__subpackages__"])

exports_files([
    "a_PY2_filelist.txt",
    "a_PY3_filelist.txt",
])

par_binary(
    name = "a",
    srcs = [
        "a.py",
        "//:__init__.py",
        "//tests:__init__.py",
        "//tests/package_a:__init__.py",
    ],
    data = ["a_dat.txt"],
    main = "a.py",
    srcs_version = "PY2AND3",
)

py_library(
    name = "a_lib",
    srcs = ["a_lib.py"],
    data = ["a_lib_dat.txt"],
    srcs_version = "PY2AND3",
)
