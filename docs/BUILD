# To regenerate html docs, run:
#   ../update_docs.sh

load("@bazel_skylib//:bzl_library.bzl", "bzl_library")
load("@io_bazel_skydoc//skylark:skylark.bzl", "skylark_doc")

bzl_library(
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
    srcs = [":subpar-rules"],
)

skylark_doc(
    name = "docs-html",
    format = "html",
    overview = True,
    site_root = ".",
    srcs = [":subpar-rules"],
)
