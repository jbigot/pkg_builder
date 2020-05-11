import atexit
from hashlib import sha256
from os import link
from pathlib import Path
from shutil import copy2, rmtree
import socket
from tempfile import mkdtemp
from time import sleep
from urllib.error import URLError
from urllib.request import urlopen


class Downloader:
    def __init__(self, verbose=False, cancellation_point=lambda: None):
        self._verbose = verbose
        self._downloaded = {}
        self._download_dir = Path(mkdtemp(prefix='DOWNLOAD_DIR.'))
        atexit.register(rmtree, self._download_dir)
        self._cancellation_point = cancellation_point

    def download(self, url, path):
        self._cancellation_point()
        if url in self._downloaded:
            while self._downloaded[url] is None:
                sleep(0.01)
                self._cancellation_point()
                if self._verbose:
                    print("Downloading " + url + " : in cache!")
        else:
            self._downloaded[url] = None
            temp_path = self._download_dir / sha256(bytes(url, 'UTF8')).hexdigest()
            if self._verbose:
                print("Downloading " + url + " ...")
            for timeout in [1, 2, 3, 5, 7]:
                try:
                    with urlopen(url, timeout=timeout) as raw_src, temp_path.open('wb') as raw_dst:
                        raw_dst.write(raw_src.read())
                    break
                except URLError as err:
                    if timeout == 7:
                        raise URLError('while downloading ' + url + ': ' + str(err))
                except socket.timeout as err:
                    if timeout == 7:
                        raise URLError('while downloading ' + url + ': ' + str(err))
            if self._verbose:
                print("Downloading " + url + " done!")
            self._downloaded[url] = temp_path
        try:
            link(self._downloaded[url], path)
        except OSError:
            copy2(self._downloaded[url], path)
