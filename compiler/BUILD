# Utility for creating self-contained python executables.

package(default_visibility = ["//visibility:public"])

py_library(
    name = "compiler_lib",
    srcs = [
        "cli.py",
        "error.py",
        "manifest_parser.py",
        "python_archive.py",
        "stored_resource.py",
        "//:__init__.py",
    ],
    data = [
        "//runtime:support.py",
    ],
)

py_library(
    name = "test_utils",
    srcs = ["test_utils.py"],
)

py_binary(
    name = "compiler",
    srcs = ["compiler.py"],
    deps = [":compiler_lib"],
)

[py_test(
    name = src_name + "_test",
    size = "small",
    srcs = [src_name + "_test.py"],
    deps = [
        ":compiler_lib",
        ":test_utils",
    ],
) for src_name in [
    "cli",
    "manifest_parser",
    "python_archive",
    "stored_resource",
]]
