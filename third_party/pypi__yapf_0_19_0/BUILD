# Test package for Subpar

package(default_visibility = ["//visibility:public"])

py_library(
    name = "files",
    srcs = [],
    data = [
        "yapf/__init__.py",
        "data_file.txt",
    ] + glob(["yapf-0.19.0.dist-info/**"]),
    imports = ["."],
)
