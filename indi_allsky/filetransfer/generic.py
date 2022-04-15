from pathlib import Path
import logging

logger = logging.getLogger('indi_allsky')


class GenericFileTransfer(object):
    def __init__(self, timeout=5.0):
        self.timeout = float(timeout)

        self.port = 0
        self.client = None


    def __del__(self):
        pass


    def connect(self, hostname, username, password, port=None):
        if port:
            logger.info('Port override to %d', port)
            self.port = port

        logger.info('Connecting to %s as %s with %s', hostname, username, self.__class__.__name__)
        self.client = self._connect(hostname, username, password)


    def close(self):
        self._close()


    def put(self, localfile, remotefile):
        logger.info('Uploading %s to %s', localfile, remotefile)

        localfile_p = Path(localfile)
        remotefile_p = Path(remotefile)

        self._put(localfile_p, remotefile_p)

