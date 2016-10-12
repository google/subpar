#!/bin/bash
set -euo pipefail

CMD="bazel test --symlink_prefix=/ --spawn_strategy=standalone //..."
while getopts "i" opt; do
  case $opt in
    i)
      CMD="/bin/bash"
      ;;
    \?)
      exit 1
      ;;
  esac
done

if [ ! -e .git ]; then
  echo "ERROR: Run $0 from root of the repository" 1>&2
  exit 1
fi

docker build -q -t subpar/bazel scripts/docker
# --spawn_strategy=standalone
#   To work around problems using Bazel sandbox inside Docker
docker run -it \
       -v $PWD:/opt/subpar:ro \
       -w /opt/subpar \
       subpar/bazel \
       $CMD
