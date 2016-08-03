# Test package for Subpar

package(default_visibility = ["//tests:__subpackages__"])

load("//:subpar.bzl", "par_binary")

exports_files(["a_filelist.txt"])

par_binary(
    name = "a",
    srcs = [
        "a.py",
        "//:__init__.py",
    ],
    data = ["a_dat.txt"],
)

py_library(
    name = "a_lib",
    srcs = ["a_lib.py"],
    data = ["a_lib_dat.txt"],
)
