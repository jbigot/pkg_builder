ARG DIST_NAME=debian
ARG DIST_RELEASE=stable-slim

FROM ${DIST_NAME}:${DIST_RELEASE}
ARG DIST_NAME
ARG VERSION_ID
ARG VERSION_CODENAME
ENV DIST_NAME ${DIST_NAME}
ENV VERSION_ID ${VERSION_ID}
ENV VERSION_CODENAME ${VERSION_CODENAME}

# Install build-essential because packages don't depend on it
# Install curl & ca-certificates to be able to download the orig file
# Install devscripts & equivs to get mk-build-deps
# Install and configure tzdata that is missing and unconfigured on focal
RUN apt-get update -qy \
 && echo -e '13\n33\n' \
  | apt-get install -qy --no-install-recommends \
    tzdata \
 && echo 'Etc/UTC' > /etc/timezone \
 && apt-get install -qy --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    devscripts \
    equivs \
    m4 \
    </dev/null \
 && apt-get clean

VOLUME /src
VOLUME /out
VOLUME /etc/apt/sources.list.d
WORKDIR /src

ENTRYPOINT ["/bin/bash", "/usr/local/bin/entrypoint"]

COPY entrypoint /usr/local/bin/
COPY 99priority /etc/apt/preferences.d/
RUN chmod +x /usr/local/bin/entrypoint
