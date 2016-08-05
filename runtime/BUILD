package(default_visibility = ["//compiler:__pkg__"])

py_library(
    name = "support",
    srcs = [
        "support.py",
        "//:__init__.py",
    ],
    srcs_version = "PY2AND3",
)

py_test(
    name = "support_PY2_test",
    size = "small",
    srcs = ["support_test.py"],
    default_python_version = "PY2",
    main = "support_test.py",
    srcs_version = "PY2AND3",
    deps = [
        ":support",
    ],
)

py_test(
    name = "support_PY3_test",
    size = "small",
    srcs = ["support_test.py"],
    default_python_version = "PY3",
    main = "support_test.py",
    srcs_version = "PY2AND3",
    deps = [
        ":support",
    ],
)
