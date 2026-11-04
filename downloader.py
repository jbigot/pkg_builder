import atexit
from concurrent.futures import Future, TimeoutError as FutureTimeoutError
from hashlib import sha256
from os import link
from pathlib import Path
from shutil import copy2, copyfileobj, rmtree
from tempfile import mkdtemp
from threading import Lock
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


class Downloader:
    def __init__(self, verbose=False, cancellation_point=lambda: None):
        self._verbose = verbose
        self._downloaded = {}
        self._lock = Lock()
        self._download_dir = Path(mkdtemp(prefix='DOWNLOAD_DIR.'))
        atexit.register(rmtree, self._download_dir)
        self._cancellation_point = cancellation_point

    def _fetch(self, url):
        temp_path = self._download_dir / sha256(bytes(url, 'UTF8')).hexdigest()
        if self._verbose:
            print("Downloading " + url + " ...")
        for timeout in [1, 2, 3, 5, 7]:
            self._cancellation_point()
            try:
                with urlopen(url, timeout=timeout) as raw_src, temp_path.open('wb') as raw_dst:
                    copyfileobj(raw_src, raw_dst)
                break
            except (URLError, TimeoutError) as err:
                # a client error such as 404 will not go away by retrying
                if timeout == 7 or (isinstance(err, HTTPError) and err.code < 500):
                    raise URLError('while downloading ' + url + ': ' + str(err))
        if self._verbose:
            print("Downloading " + url + " done!")
        return temp_path

    def download(self, url, path):
        self._cancellation_point()
        # the first caller for an URL downloads it, the others wait for its result, error included
        with self._lock:
            result = self._downloaded.get(url)
            owner = result is None
            if owner:
                result = self._downloaded[url] = Future()
        if owner:
            try:
                result.set_result(self._fetch(url))
            except BaseException as err:
                result.set_exception(err)
        elif self._verbose:
            print("Downloading " + url + " : in cache!")
        while True:
            try:
                downloaded = result.result(timeout=0.1)
                break
            except FutureTimeoutError:
                self._cancellation_point()
        try:
            link(downloaded, path)
        except OSError:
            copy2(downloaded, path)
