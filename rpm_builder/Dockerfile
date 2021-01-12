ARG DIST_ID=fedora
ARG DIST_RELEASE=latest

FROM ${DIST_ID}:${DIST_RELEASE}

ARG DIST_ID=fedora
ARG DIST_RELEASE=latest

VOLUME /src
VOLUME /localrepo

RUN DNF=yum \
  ; WEAK_DEPS="" \
  ; BUILDDEP="" \
  ; case "${DIST_ID}" in \
    "fedora" ) \
      DNF=dnf \
  ;   WEAK_DEPS="--setopt=install_weak_deps=False --best" \
  ;   BUILDDEP="dnf-command(builddep) nosync" \
  ;; \
    *) \
      DNF=yum \
  ;   BUILDDEP="yum-utils" \
  ;; \
    esac \
 && ${DNF} upgrade -y \
 && ${DNF} install -y --setopt=tsflags=nodocs ${WEAK_DEPS} \
    rpm-build \
    ${BUILDDEP} \
 && ${DNF} upgrade -y \
 && ${DNF} clean all -y --enablerepo='*' \
 && rm -f /*.log ${HOME}/*

ENTRYPOINT ["/bin/bash", "-l", "/entrypoint"]
ENV LD_PRELOAD="/usr/lib64/nosync/nosync.so"

COPY entrypoint /
