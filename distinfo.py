
import csv
from datetime import date
from functools import total_ordering
from io import TextIOWrapper
from itertools import count, repeat
import re
from typing import Iterator, List
from urllib.request import urlopen


@total_ordering
class ReleaseInfo:
    def __init__(self, distrib, name: str, id: str, order: int, codename: str = None, cpe: str = None, suite: str = None, release_date: date = date.max, eol_date: date = date.max):
        self.distrib = distrib
        self.name = name
        self.id = id
        self.order = order
        self.codename = codename
        self.cpe = cpe
        self.suite = suite
        self.release_date = release_date
        self.eol_date = eol_date

    def uid(self):
        return self.distrib.uid()+'@'+self.id+('' if self.codename is None else '@'+self.codename)

    def released(self):
        return self.release_date <= date.today()

    def supported(self):
        return self.released() and self.eol_date > date.today()

    def __lt__(self, other):
        if other.distrib != self.distrib:
            return NotImplemented
        return self.order < other.order

    def __eq__(self, other):
        if other.distrib != self.distrib:
            return NotImplemented
        return self.order == other.order

    def __hash__(self):
        return hash(self.uid())

    def __str__(self):
        return str(self.distrib)+" "+self.name


class DistInfo:
    def __init__(self, name: str, id: str, id_like=list()):
        self.name = name
        self.id = id
        self.id_like = list([id]+list(id_like))
        self._releases = set()

    def uid(self):
        return self.id

    def releases(self, id: str = None, codename: str = None, cpe: str = None, suite: str = None, release_date: date = None, eol_date: date = None, released: bool = None, supported: bool = None) -> List[ReleaseInfo]:
        def __filter_func(rel: DistInfo):
            if id is not None and rel.id != str(id):
                return False
            if codename is not None and rel.codename != str(codename):
                return False
            if cpe is not None and rel.cpe != str(cpe):
                return False
            if suite is not None and rel.suite != str(suite):
                return False
            if release_date is not None and rel.release_date != date(release_date):
                return False
            if eol_date is not None and rel.eol_date != date(eol_date):
                return False
            if released is not None and rel.released() != bool(released):
                return False
            if supported is not None and rel.supported() != bool(supported):
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
    with urlopen('https://salsa.debian.org/debian/distro-info-data/-/raw/master/'+distribution.id+'.csv') as rel_data:
        csv_data = csv.reader(TextIOWrapper(rel_data), dialect='unix')
        # skip the title line: version,codename,series,created,release,eol,eol-server
        next(csv_data)
        for order, rel in enumerate(csv_data):
            release = ReleaseInfo(distribution,
                                  rel[1] if rel[0] == '' else rel[0] +
                                  ' ('+rel[1]+')',
                                  re.sub(r'[^0-9.].*', '', rel[0]),
                                  order,
                                  rel[2])
            if len(rel) > 4:
                release.release_date = date.fromisoformat(rel[4].strip())
            if len(rel) > 5:
                release.eol_date = date.fromisoformat(rel[5].strip())
            distribution._releases.add(release)
    return distribution


def __init_distribs():
    global __distribs
    if __distribs is not None:
        return
    __distribs = set()

    debian = __debubun_rel(DistInfo("Debian GNU/Linux", 'debian'))
    for release, suite in zip(
            reversed(debian.releases(supported=True)),
            map(lambda n: 'old'*n+'stable', count(0))):
        release.suite = suite
    debian.releases(released=False)[0].suite = 'testing'
    debian.releases(codename='sid')[0].suite = 'unstable'
    debian.releases(codename='experimental')[0].suite = 'rc-buggy'
    __distribs.add(debian)

    ubuntu = __debubun_rel(DistInfo("Ubuntu", 'ubuntu', id_like=['debian']))
    devel = ubuntu.releases(released=False)
    if len(devel):
        devel[0].suite = 'devel'
    __distribs.add(ubuntu)

    fedora = DistInfo("Fedora", 'fedora')
    fedora._releases.add(ReleaseInfo(fedora, "Rawhide", 'rawhide', 33))
    fedora._releases.add(ReleaseInfo(fedora, "32", '32', 32,
                                     cpe='cpe:/o:fedoraproject:fedora:32', suite='branched'))
    fedora._releases.add(ReleaseInfo(fedora, "31", '31', 31,
                                     cpe='cpe:/o:fedoraproject:fedora:31', release_date=date(2019, 10, 29)))
    fedora._releases.add(ReleaseInfo(fedora, "30", '30', 30,
                                     cpe='cpe:/o:fedoraproject:fedora:30', release_date=date(2019,  5,  7)))
    __distribs.add(fedora)


__init_distribs()
