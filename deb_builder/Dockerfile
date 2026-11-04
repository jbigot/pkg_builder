ARG DIST_ID=debian
ARG DIST_RELEASE=stable-slim

FROM ${DIST_ID}:${DIST_RELEASE}
ARG DIST_CODENAME

VOLUME /src
VOLUME /deps
VOLUME /localrepo

# Install build-essential because packages implicitly depend on it
# Install eatmydata to accelerate the build process
# Install tzdata, missing on some releases, without its interactive configuration
RUN export DEBIAN_FRONTEND=noninteractive \
 && echo "force-unsafe-io" > /etc/dpkg/dpkg.cfg.d/02apt-speedup \
 && apt-get update -y \
 && apt-get install -qy --no-install-recommends \
    tzdata \
 && apt-get dist-upgrade -y \
 && apt-get install -y --no-install-recommends \
    build-essential \
    eatmydata \
    tini \
 && apt-get dist-upgrade -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/usr/bin/tini", "--", "/bin/bash", "-l", "/entrypoint"]
ENV DIST_CODENAME="${DIST_CODENAME}"
ENV LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libeatmydata.so

COPY entrypoint /
