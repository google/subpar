load("@rules_python//python:defs.bzl", "py_library", "py_test")

package(default_visibility = ["//compiler:__pkg__"])

py_library(
    name = "support",
    srcs = [
        "__init__.py",
        "support.py",
        "//:__init__.py",
    ],
    srcs_version = "PY2AND3",
)

py_test(
    name = "support_test",
    size = "small",
    srcs = ["support_test.py"],
    main = "support_test.py",
    srcs_version = "PY2AND3",
    deps = [
        ":support",
        "//compiler:test_utils",
    ],
)
