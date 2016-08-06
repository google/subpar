# To regenerate html docs, run:
#   ./update_docs.sh

load("@io_bazel_skydoc//skylark:skylark.bzl", "skylark_doc", "skylark_library")

skylark_library(
    name = "subpar-rules",
    srcs = [
        "//:debug.bzl",
        "//:subpar.bzl",
    ],
)

skylark_doc(
    name = "docs-html",
    format = "markdown",
    deps = ["subpar-rules"],
)

skylark_doc(
    name = "docs-md",
    format = "html",
    deps = ["subpar-rules"],
)
