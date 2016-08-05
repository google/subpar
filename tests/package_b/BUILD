# Test package for Subpar

package(default_visibility = ["//tests:__subpackages__"])

load("//:subpar.bzl", "par_binary")

exports_files([
    "b_PY2_filelist.txt",
    "b_PY3_filelist.txt",
])

[par_binary(
    name = "b_%s" % version,
    srcs = ["b.py"],
    data = ["b_dat.txt"],
    default_python_version = version,
    main = "b.py",
    srcs_version = "PY2AND3",
    deps = [
        "//tests/package_a:a_%s" % version,
        "//tests/package_a:a_lib",
    ],
) for version in [
    "PY2",
    "PY3",
]]
