ARG DIST_ID=debian
ARG DIST_RELEASE=stable-slim

FROM ${DIST_ID}:${DIST_RELEASE}
ARG DIST_CODENAME

VOLUME /src
VOLUME /deps
VOLUME /localrepo

# Install build-essential because packages implicitly depend on it
# Install eatmydata to accelerate the build process
# Install and configure tzdata that is missing and unconfigured on focal
RUN echo "force-unsafe-io" > /etc/dpkg/dpkg.cfg.d/02apt-speedup \
 && apt-get update -y \
 && echo -e '13\n33\n' \
  | apt-get install -qy --no-install-recommends \
    tzdata \
 && apt-get dist-upgrade -y \
 && apt-get install -y --no-install-recommends \
    build-essential \
    eatmydata \
    </dev/null \
 && apt-get dist-upgrade -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/bin/bash", "/entrypoint"]
ENV DIST_CODENAME="${DIST_CODENAME}"

COPY entrypoint /
