FROM ubuntu:trusty

# Touch this to update all apt packages
ENV REFRESHED_AT 2016-10-11:17:20:00

# So we can update apt repositories
RUN apt-get update -q && apt-get install -qy \
    apt-transport-https \
    curl \
    python \
    python3 \
    software-properties-common

# Java 8 for Bazel
RUN add-apt-repository ppa:webupd8team/java
RUN echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true \
    | /usr/bin/debconf-set-selections
RUN apt-get update -q && apt-get install -qy \
    oracle-java8-installer

# Bazel.  Instructions from https://www.bazel.io/versions/master/docs/install.html
RUN echo "deb [arch=amd64] http://storage.googleapis.com/bazel-apt stable jdk1.8" \
    | sudo tee /etc/apt/sources.list.d/bazel.list \
    && curl https://storage.googleapis.com/bazel-apt/doc/apt-key.pub.gpg \
    | sudo apt-key add -
RUN apt-get update -q && apt-get install -qy \
    bazel
