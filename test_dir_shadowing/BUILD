# Integration test for Subpar.
#
# This test is not in the `tests` directory because the bug only
# manifests when the code is in a directory structure rooted at the
# workspace, and consisting of two direcotories with the same name,
# E.g. `<workspace>/X/X` for some `X`.

package(default_visibility = ["//tests:__subpackages__"])

load("//:subpar.bzl", "par_binary")

exports_files([
    "test_dir_shadowing_main_PY2_filelist.txt",
    "test_dir_shadowing_main_PY3_filelist.txt",
])

py_library(
    name = "test_dir_shadowing",
    srcs = [
        "test_dir_shadowing/dir_shadowing_lib.py",
    ],
    data = [
        "test_dir_shadowing/dir_shadowing_lib_dat.txt",
    ],
    imports = ["."],
)

par_binary(
    name = "test_dir_shadowing_main",
    srcs = [
        "test_dir_shadowing/dir_shadowing_main.py",
    ],
    data = [
        "test_dir_shadowing/dir_shadowing_main_dat.txt",
    ],
    main = "test_dir_shadowing/dir_shadowing_main.py",
    deps = [
        ":test_dir_shadowing",
    ],
)
