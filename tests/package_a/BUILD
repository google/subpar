# Test package for Subpar

package(default_visibility = ["//tests:__subpackages__"])

load("//:subpar.bzl", "par_binary")

exports_files([
    "a_PY2_filelist.txt",
    "a_PY3_filelist.txt",
])

[par_binary(
    name = "a_%s" % version,
    srcs = [
        "a.py",
    ],
    data = ["a_dat.txt"],
    default_python_version = version,
    main = "a.py",
    srcs_version = "PY2AND3",
) for version in [
    "PY2",
    "PY3",
]]

py_library(
    name = "a_lib",
    srcs = ["a_lib.py"],
    data = ["a_lib_dat.txt"],
    srcs_version = "PY2AND3",
)
