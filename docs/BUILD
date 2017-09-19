# To regenerate html docs, run:
#   ./update_docs.sh

load("@io_bazel_skydoc//skylark:skylark.bzl", "skylark_doc", "skylark_library")

skylark_library(
    name = "subpar-rules",
    srcs = [
        "@subpar//:debug.bzl",
        "@subpar//:subpar.bzl",
    ],
)

skylark_doc(
    name = "docs-md",
    format = "markdown",
    overview = True,
    site_root = ".",
    deps = ["subpar-rules"],
)

skylark_doc(
    name = "docs-html",
    format = "html",
    overview = True,
    site_root = ".",
    deps = ["subpar-rules"],
)
