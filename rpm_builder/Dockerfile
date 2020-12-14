ARG DIST_ID=fedora
ARG DIST_RELEASE=31

FROM ${DIST_ID}:${DIST_RELEASE}

VOLUME /src
VOLUME /localrepo

RUN dnf upgrade -y \
 || yum upgrade -y \
 && dnf install -y --setopt=tsflags=nodocs --setopt=install_weak_deps=False --best \
    rpm-build \
    'dnf-command(builddep)' \
    nosync \
 || yum install -y --setopt=tsflags=nodocs \
    rpm-build \
    yum-utils \
 && dnf upgrade -y \
 || yum upgrade -y \
 && dnf clean all -y --enablerepo='*' \
 || yum clean all -y --enablerepo='*' \
 && rm -f /*.log ${HOME}/*

ENTRYPOINT ["/bin/bash", "/usr/local/bin/entrypoint"]
ENV LD_PRELOAD="/usr/lib64/nosync/nosync.so"

COPY entrypoint /usr/local/bin/
