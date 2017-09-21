# Test package for Subpar

package(default_visibility = ["//tests:__subpackages__"])

load("//:subpar.bzl", "par_binary")

exports_files([
    "b_PY2_filelist.txt",
    "b_PY3_filelist.txt",
])

par_binary(
    name = "b",
    srcs = [
        "b.py",
        "//:__init__.py",
        "//tests:__init__.py",
        "//tests/package_b:__init__.py",
    ],
    data = ["b_dat.txt"],
    main = "b.py",
    srcs_version = "PY2AND3",
    deps = [
        "//tests/package_a:a",
        "//tests/package_a:a_lib",
    ],
)
