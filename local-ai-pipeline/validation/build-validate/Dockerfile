FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG DTS_SCHEMA_VERSION=2026.4

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      bash \
      bc \
      bison \
      build-essential \
      ca-certificates \
      device-tree-compiler=1.7.0-2build1 \
      file \
      flex \
      gcc-aarch64-linux-gnu=4:13.2.0-7ubuntu1 \
      gettext-base \
      git=1:2.43.0-1ubuntu7.3 \
      kmod \
      libelf-dev \
      libssl-dev \
      make=4.3-4.1build2 \
      openssl \
      perl=5.38.2-3.2ubuntu0.2 \
      pkg-config \
      python3=3.12.3-0ubuntu2.1 \
      python3-dev \
      python3-git \
      python3-pip=24.0+dfsg-1ubuntu1.3 \
      python3-ply \
      python3-venv \
      rsync \
      sparse=0.6.4-4ubuntu3 \
      swig \
      xz-utils \
      yamllint=1.33.0-1 \
    && python3 -m pip install --break-system-packages "dtschema==${DTS_SCHEMA_VERSION}" \
    && rm -rf /var/lib/apt/lists/*

COPY proof_runner.py /usr/local/bin/kernel-proof-runner
RUN chmod +x /usr/local/bin/kernel-proof-runner

WORKDIR /workspace
ENTRYPOINT ["/usr/local/bin/kernel-proof-runner"]
