import sys
import time

from twisted.internet import reactor
from twisted.python import log
from twisted.python.compat import urllib_parse
from twisted.web import proxy, http

log.startLogging(sys.stdout)


class ProxyRequest(proxy.ProxyRequest):
    _transferred_bytes = 0

    def write(self, data):
        self.__class__._transferred_bytes += len(data)
        proxy.ProxyRequest.write(self, data)

    def process(self):
        try:
            _range = 'bytes=' + urllib_parse.parse_qs(
                urllib_parse.urlparse(self.uri).query).get(
                'range', [None])[0]
        except TypeError:
            pass
        else:
            if self.getHeader('range') and self.getHeader('range') != _range:
                self.setResponseCode(416, "Requested Range not satisfiable")
                self.finish()
                return
            else:
                self.requestHeaders.addRawHeader('range', _range)
        if self.uri == b'/stats':
            data = {
                'uptime': round(
                    (time.time() - startTime),
                    2),
                'transferred_bytes': str(
                    self.__class__._transferred_bytes)}
            self.write(b'%a' % data)
            self.finish()
            return
        try:
            proxy.ProxyRequest.process(self)
        except KeyError:
            print("HTTPS is not supported at the moment!")


class Proxy(proxy.Proxy):
    requestFactory = ProxyRequest


class ProxyFactory(http.HTTPFactory):
    protocol = Proxy


if __name__ == "__main__":
    startTime = time.time()
    reactor.listenTCP(8080, ProxyFactory())
    reactor.run()
