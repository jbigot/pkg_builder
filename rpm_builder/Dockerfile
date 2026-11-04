ARG DIST_ID=fedora
ARG DIST_IMAGE=${DIST_ID}
ARG DIST_RELEASE=latest

FROM ${DIST_IMAGE}:${DIST_RELEASE}

VOLUME /src
VOLUME /output
VOLUME /localrepo

ARG DIST_ID

RUN EXTRA_PKGS="" \
  ; EXTRA_REPOS="" \
  ; case "${DIST_ID}" in \
    "fedora" ) \
      EXTRA_PKGS="nosync" \
  ;; \
    "almalinux" | "rocky" ) \
      EXTRA_REPOS="epel-release" \
  ;; \
    esac \
 && dnf upgrade -y \
 && dnf install -y --setopt=tsflags=nodocs --setopt=install_weak_deps=False --best \
    'dnf-command(builddep)' \
    openssl \
    rpm-build \
    ${EXTRA_PKGS} \
 && if [ -n "${EXTRA_REPOS}" ] \
  ; then \
      dnf config-manager --set-enabled crb 2>/dev/null \
      || dnf config-manager --set-enabled powertools \
  &&  dnf install -y --setopt=tsflags=nodocs ${EXTRA_REPOS} \
  ; fi \
 && dnf upgrade -y \
 && dnf clean all -y --enablerepo='*' \
 && rm -f /*.log ${HOME}/*

ENTRYPOINT ["/bin/bash", "-l", "/entrypoint"]

COPY entrypoint /
