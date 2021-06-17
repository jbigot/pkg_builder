
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
        return self.distrib.uid()+'-'+self.id+('' if self.codename is None else '-'+self.codename)

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
        return str(self.distrib)+" "+self.name


class DistInfo:
    def __init__(self, name: str, id: str, id_like=list()):
        self.name = name
        self.id = id
        self.id_like = list([id]+list(id_like))
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
            if release_date is not None and rel.release_date != date(release_date):
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
                 distribution.id+'.csv') as rel_data:
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

    centos = DistInfo("CentOS Linux", 'centos', id_like=['rhel', 'fedora'])
    centos.add_release("8", '8', 8, cpe='cpe:/o:centos:centos:8',
                       release_date=date(2019,  9, 24), eol_date=date(2021, 12, 31))
    centos.add_release("7", '7', 7, cpe='cpe:/o:centos:centos:7',
                       release_date=date(2014,  7,  7), eol_date=date(2024,  6, 30))
    centos.add_release("6", '6', 6, cpe='cpe:/o:centos:centos:6',
                       release_date=date(2011,  7, 10), eol_date=date(2020, 11, 30))
    __distribs.add(centos)

    fedora = DistInfo("Fedora", 'fedora')
    fedora.add_release("35", '35', 35, suite='rawhide',
                       release_date=date(2021,  10, 26))
    fedora.add_release("34", '34', 34, cpe='cpe:/o:fedoraproject:fedora:34',
                       release_date=date(2021,  4, 27))
    fedora.add_release("33", '33', 33, cpe='cpe:/o:fedoraproject:fedora:33',
                       release_date=date(2020, 10, 27))
    fedora.add_release("32", '32', 32, cpe='cpe:/o:fedoraproject:fedora:32',
                       release_date=date(2020,  4, 28), eol_date=date(2021,  5, 18))
    fedora.add_release("31", '31', 31, cpe='cpe:/o:fedoraproject:fedora:31',
                       release_date=date(2019, 10, 29), eol_date=date(2020, 11, 24))
    fedora.add_release("30", '30', 30, cpe='cpe:/o:fedoraproject:fedora:30',
                       release_date=date(2019,  5,  7), eol_date=date(2020,  5, 26))
    __distribs.add(fedora)

    redhat = DistInfo("Red Hat Enterprise Linux", 'rhel', id_like=['fedora'])
    redhat.add_release("8.4 (Ootpa)", '8.4', 804, cpe='cpe:/o:redhat:enterprise_linux:8.4', 
                       release_date=date(2021,  5, 18), eol_date=date(2023,  5, 30))
    redhat.add_release("8.3 (Ootpa)", '8.3', 803, cpe='cpe:/o:redhat:enterprise_linux:8.3', 
                       release_date=date(2020, 11,  3))
    redhat.add_release("8.2 (Ootpa)", '8.2', 802, cpe='cpe:/o:redhat:enterprise_linux:8.2', 
                       release_date=date(2020,  4, 28), eol_date=date(2022,  4, 30))
    redhat.add_release("8.1 (Ootpa)", '8.1', 801, cpe='cpe:/o:redhat:enterprise_linux:8.1', 
                       release_date=date(2019, 11,  5), eol_date=date(2021, 11, 30))
    redhat.add_release("8.0 (Ootpa)", '8.0', 800, cpe='cpe:/o:redhat:enterprise_linux:8.0', 
                       release_date=date(2019,  5,  7), eol_date=date(2019, 11,  5))
    redhat.add_release("7.9 (Maipo)", '7.9', 709, cpe='cpe:/o:redhat:enterprise_linux:7.9', 
                       release_date=date(2020,  9, 29), eol_date=date(2024,  6, 30))
    redhat.add_release("7.8 (Maipo)", '7.8', 708, cpe='cpe:/o:redhat:enterprise_linux:7.8', 
                       release_date=date(2020,  3, 31), eol_date=date(2020,  9, 29))
    redhat.add_release("7.7 (Maipo)", '7.7', 707, cpe='cpe:/o:redhat:enterprise_linux:7.7', 
                       release_date=date(2019,  8,  6), eol_date=date(2021,  8, 30))
    redhat.add_release("7.6 (Maipo)", '7.6', 706, cpe='cpe:/o:redhat:enterprise_linux:7.6', 
                       release_date=date(2018, 10, 30), eol_date=date(2021,  5, 31))
    redhat.add_release("7.5 (Maipo)", '7.5', 705, cpe='cpe:/o:redhat:enterprise_linux:7.5', 
                       release_date=date(2018,  4, 10), eol_date=date(2020,  4, 30))
    redhat.add_release("7.4 (Maipo)", '7.4', 704, cpe='cpe:/o:redhat:enterprise_linux:7.4', 
                       release_date=date(2017,  7, 31), eol_date=date(2019,  8, 31))
    redhat.add_release("7.3 (Maipo)", '7.3', 703, cpe='cpe:/o:redhat:enterprise_linux:7.3', 
                       release_date=date(2016, 11,  3), eol_date=date(2018, 11, 30))
    redhat.add_release("7.2 (Maipo)", '7.2', 702, cpe='cpe:/o:redhat:enterprise_linux:7.2', 
                       release_date=date(2015, 11, 19), eol_date=date(2017, 11, 30))
    redhat.add_release("7.1 (Maipo)", '7.1', 701, cpe='cpe:/o:redhat:enterprise_linux:7.1', 
                       release_date=date(2015,  3,  5), eol_date=date(2017,  3, 31))
    redhat.add_release("7.0 (Maipo)", '7.0', 700, cpe='cpe:/o:redhat:enterprise_linux:7.0', 
                       release_date=date(2014,  6,  9), eol_date=date(2015,  3,  5))
    __distribs.add(redhat)


__init_distribs()
