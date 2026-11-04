
import csv
from datetime import date
from functools import total_ordering
from io import TextIOWrapper
import json
import re
from typing import Iterator, List
from urllib.request import urlopen


@total_ordering
class ReleaseInfo:
    def __init__(self, distrib, name: str, id: str, order: int, codename: str = None,
                 cpe: str = None, suite: str = None, release_date: date = date.max,
                 eol_date: date = date.max):
        self.distrib = distrib
        self.name = name
        self.id = id
        self._order = order
        self.codename = codename
        self.cpe = cpe
        self.suite = suite
        self.release_date = release_date
        self.eol_date = eol_date

    def uid(self):
        return self.distrib.uid() + '-' + self.id + \
            ('' if self.codename is None else '-' + self.codename)

    def released(self):
        return self.release_date <= date.today()

    def eoled(self):
        return self.eol_date <= date.today()

    def supported(self):
        return self.released() and not self.eoled()

    def __lt__(self, other):
        if other.distrib != self.distrib:
            return NotImplemented
        return self._order < other._order

    def __eq__(self, other):
        if other.distrib != self.distrib:
            return NotImplemented
        return self._order == other._order

    def __hash__(self):
        return hash(self.uid())

    def __str__(self):
        return str(self.distrib) + " " + self.name


class DistInfo:
    def __init__(self, name: str, id: str, id_like=list(), docker_image: str = None):
        self.name = name
        self.id = id
        self.docker_image = id if docker_image is None else docker_image
        self.id_like = list([id] + list(id_like))
        self._releases = set()

    def uid(self):
        return self.id

    def add_release(self, *args, **kwargs):
        self._releases.add(ReleaseInfo(self, *args, **kwargs))

    def releases(self, id: str = None, codename: str = None, cpe: str = None, suite: str = None,
                 release_date: date = None, eol_date: date = None, released: bool = None,
                 supported: bool = None, eoled: bool = None, after: ReleaseInfo = None,
                 before: ReleaseInfo = None) -> List[ReleaseInfo]:
        def __filter_func(rel: ReleaseInfo):
            if id is not None and rel.id != str(id):
                return False
            if codename is not None and rel.codename != str(codename):
                return False
            if cpe is not None and rel.cpe != str(cpe):
                return False
            if suite is not None and rel.suite != str(suite):
                return False
            if release_date is not None and rel.release_date != date(
                    release_date):
                return False
            if eol_date is not None and rel.eol_date != date(eol_date):
                return False
            if released is not None and rel.released() != bool(released):
                return False
            if supported is not None and rel.supported() != bool(supported):
                return False
            if eoled is not None and rel.eoled() != bool(eoled):
                return False
            if after is not None and not rel > after:
                return False
            if before is not None and not rel < before:
                return False
            return True
        return sorted(filter(__filter_func, self._releases))

    def __hash__(self):
        return hash(self.uid())

    def __str__(self):
        return self.name


__distribs = None


def distributions(id: str = None, id_like: set = set()) -> Iterator[DistInfo]:
    def __filter_func(dist: DistInfo):
        if id is not None and dist.id != id:
            return False
        if not set(id_like) <= set(dist.id_like):
            return False
        return True
    return filter(__filter_func, __distribs)


def __debubun_rel(distribution: DistInfo) -> DistInfo:
    with urlopen('https://debian.pages.debian.net/distro-info-data/' +
                 distribution.id + '.csv') as rel_data:
        csv_data = csv.reader(TextIOWrapper(rel_data), dialect='unix')
        # skip the title line:
        # version,codename,series,created,release,eol,eol-server
        next(csv_data)
        for order, rel in enumerate(csv_data):
            release = ReleaseInfo(distribution,
                                  rel[1] if rel[0] == '' else rel[0] +
                                  ' (' + rel[1] + ')',
                                  re.sub(r'[^0-9.].*', '', rel[0]),
                                  order,
                                  rel[2])
            if len(rel) > 4:
                release.release_date = date.fromisoformat(rel[4].strip())
            if len(rel) > 5:
                release.eol_date = date.fromisoformat(rel[5].strip())
            distribution._releases.add(release)
    return distribution


def __fedora_rel(distribution: DistInfo) -> DistInfo:
    # Bodhi, Fedora's update system, lists every release with its state and dates
    page, pages = 1, 1
    while page <= pages:
        with urlopen('https://bodhi.fedoraproject.org/releases/?exclude_archived=False'
                     '&rows_per_page=100&page=' + str(page)) as rel_data:
            rel_data = json.load(rel_data)
        pages = rel_data['pages']
        page += 1
        for rel in rel_data['releases']:
            if rel['id_prefix'] != 'FEDORA' or not re.fullmatch(r'F[0-9]+', rel['name']):
                continue
            released = rel['state'] in ('current', 'archived')
            if rel.get('released_on'):
                release_date = date.fromisoformat(rel['released_on'][:10])
            else:
                release_date = date.min if released else date.max
            if rel.get('eol'):
                eol_date = date.fromisoformat(rel['eol'][:10])
            else:
                eol_date = date.min if rel['state'] == 'archived' else date.max
            distribution.add_release(rel['version'], rel['version'], int(rel['version']),
                                     cpe='cpe:/o:fedoraproject:fedora:' + rel['version'],
                                     suite='rawhide' if rel['branch'] == 'rawhide' else None,
                                     release_date=release_date, eol_date=eol_date)
    return distribution


def __endoflife_dist(product: str, id: str, id_like=list(), docker_image: str = None) -> DistInfo:
    # endoflife.date gathers the major releases of the distribution with their dates from its
    # vendor's own pages
    with urlopen('https://endoflife.date/api/v1/products/' + product) as rel_data:
        rel_data = json.load(rel_data)['result']
    distribution = DistInfo(rel_data['label'], id, id_like=id_like, docker_image=docker_image)
    cpe = next(i['id'] for i in rel_data['identifiers']
               if i['type'] == 'cpe' and i['id'].startswith('cpe:/'))
    for rel in rel_data['releases']:
        distribution.add_release(rel['name'], rel['name'], int(rel['name']),
                                 cpe=cpe + ':' + rel['name'],
                                 release_date=date.fromisoformat(rel['releaseDate'])
                                 if rel.get('releaseDate') else date.max,
                                 eol_date=date.fromisoformat(rel['eolFrom'])
                                 if rel.get('eolFrom') else date.max)
    return distribution


def __init_distribs():
    global __distribs
    if __distribs is not None:
        return
    __distribs = set()

    debian = __debubun_rel(DistInfo("Debian GNU/Linux", 'debian'))
    # the archive keeps stable, oldstable and oldoldstable as aliases of the three latest releases,
    # whether they are still under regular security support or only under LTS
    for release, suite in zip(
            reversed(debian.releases(released=True)),
            ['stable', 'oldstable', 'oldoldstable']):
        release.suite = suite
    debian.releases(released=False)[0].suite = 'testing'
    debian.releases(codename='sid')[0].suite = 'unstable'
    debian.releases(codename='rc-buggy')[0].suite = 'experimental'
    __distribs.add(debian)

    ubuntu = __debubun_rel(DistInfo("Ubuntu", 'ubuntu', id_like=['debian']))
    devel = ubuntu.releases(released=False)
    if len(devel):
        devel[0].suite = 'devel'
    __distribs.add(ubuntu)

    __distribs.add(__endoflife_dist('almalinux', 'almalinux',
                                    id_like=['rhel', 'centos', 'fedora']))
    __distribs.add(__endoflife_dist('rocky-linux', 'rocky', id_like=['rhel', 'centos', 'fedora'],
                                    docker_image='rockylinux/rockylinux'))

    __distribs.add(__fedora_rel(DistInfo("Fedora", 'fedora')))


__init_distribs()
