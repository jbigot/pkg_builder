ARG DIST_ID=fedora
ARG DIST_RELEASE=31

FROM ${DIST_ID}:${DIST_RELEASE}

VOLUME /src
VOLUME /localrepo

RUN dnf upgrade -y \
 || yum upgrade -y \
 && dnf install -y --setopt=tsflags=nodocs \
    rpm-build \
    'dnf-command(builddep)' \
    nosync \
 || yum install -y --setopt=tsflags=nodocs \
    rpm-build \
    yum-utils \
 && dnf clean all -y --enablerepo='*' \
 || yum clean all -y --enablerepo='*' \
 && dnf upgrade -y \
 || yum upgrade -y \
 && rm -f /*.log ${HOME}/*

ENTRYPOINT ["/bin/bash", "/usr/local/bin/entrypoint"]

COPY entrypoint /usr/local/bin/
