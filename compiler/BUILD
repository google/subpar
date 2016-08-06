# Utility for creating self-contained python executables.

package(default_visibility = ["//visibility:public"])

py_library(
    name = "compiler_lib",
    srcs = [
        "__init__.py",
        "cli.py",
        "error.py",
        "manifest_parser.py",
        "python_archive.py",
        "stored_resource.py",
        "//:__init__.py",
    ],
    data = [
        "//runtime:support",
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

py_binary(
    name = "compiler3",
    srcs = ["compiler.py"],
    default_python_version = "PY3",
    main = "compiler.py",
    srcs_version = "PY2AND3",
    deps = [":compiler_lib"],
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
