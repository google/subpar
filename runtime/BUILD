package(default_visibility = ["//compiler:__pkg__"])

py_library(
    name = "support",
    srcs = [
        "support.py",
        "//:__init__.py",
    ],
)

py_test(
    name = "support_test",
    size = "small",
    srcs = ["support_test.py"],
    deps = [
        ":support",
    ],
)
