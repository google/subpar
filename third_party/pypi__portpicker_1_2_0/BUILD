# Test package for Subpar

load("@rules_python//python:defs.bzl", "py_library")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "files",
    srcs = [],
    data = [
        "portpicker.py",
        "data_file.txt",
    ] + glob(["portpicker-1.2.0.dist-info/**"]),
    imports = ["."],
)
