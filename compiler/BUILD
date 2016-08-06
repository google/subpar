# Utility for creating self-contained python executables.

package(default_visibility = ["//visibility:public"])

load("//:subpar.bzl", "parfile")

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
    srcs_version = "PY2AND3",
)

py_library(
    name = "test_utils",
    srcs = ["test_utils.py"],
    srcs_version = "PY2AND3",
)

py_binary(
    name = "compiler",
    srcs = ["compiler.py"],
    default_python_version = "PY2",
    main = "compiler.py",
    srcs_version = "PY2AND3",
    deps = [":compiler_lib"],
)

# Compile the compiler while carefully avoiding a circular dependency
parfile(
    name = "compiler.par",
    src = ":compiler",
    compiler = ":compiler",
    default_python_version = "PY2",
    main = "compiler.py",
)

[py_test(
    name = "%s_%s_test" % (src_name, version),
    size = "small",
    srcs = [src_name + "_test.py"],
    default_python_version = version,
    main = src_name + "_test.py",
    srcs_version = "PY2AND3",
    deps = [
        ":compiler_lib",
        ":test_utils",
    ],
) for src_name in [
    "cli",
    "manifest_parser",
    "python_archive",
    "stored_resource",
] for version in [
    "PY2",
    "PY3",
]]
