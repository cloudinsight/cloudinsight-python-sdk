# -*- coding: utf-8 -*-
"""
Tests for onestatsd.py
"""

from collections import deque
import six
import socket
import time

from nose import tools as t

from cloudinsight.onestatsd.base import OneStatsd
from cloudinsight import statsd


class FakeSocket(object):
    """ A fake socket for testing. """

    def __init__(self):
        self.payloads = deque()

    def send(self, payload):
        assert type(payload) == six.binary_type
        self.payloads.append(payload)

    def recv(self):
        try:
            return self.payloads.popleft().decode('utf-8')
        except IndexError:
            return None

    def __repr__(self):
        return str(self.payloads)


class BrokenSocket(FakeSocket):

    def send(self, payload):
        raise socket.error("Socket error")


class TestOneStatsd(object):

    def setUp(self):
        self.statsd = OneStatsd()
        self.statsd.socket = FakeSocket()

    def recv(self):
        return self.statsd.socket.recv()

    def test_gauge(self):
        self.statsd.gauge('gauge', 123.4)
        assert self.recv() == 'gauge:123.4|g'

    def test_counter(self):
        self.statsd.increment('page.views')
        t.assert_equal('page.views:1|c', self.recv())

        self.statsd.increment('page.views', 11)
        t.assert_equal('page.views:11|c', self.recv())

        self.statsd.decrement('page.views')
        t.assert_equal('page.views:-1|c', self.recv())

        self.statsd.decrement('page.views', 12)
        t.assert_equal('page.views:-12|c', self.recv())

    def test_tagged_gauge(self):
        self.statsd.gauge('gt', 123.4, tags=['country:china', 'age:45', 'blue'])
        t.assert_equal('gt:123.4|g|#country:china,age:45,blue', self.recv())

    def test_tagged_counter(self):
        self.statsd.increment('ct', tags=['country:canada', 'red'])
        t.assert_equal('ct:1|c|#country:canada,red', self.recv())

    def test_sample_rate(self):
        self.statsd.increment('c', sample_rate=0)
        assert not self.recv()
        for i in range(10000):
            self.statsd.increment('sampled_counter', sample_rate=0.3)
        self.assert_almost_equal(3000, len(self.statsd.socket.payloads), 150)
        t.assert_equal('sampled_counter:1|c|@0.3', self.recv())

    def test_tags_and_samples(self):
        for i in range(100):
            self.statsd.gauge('gst', 23, tags=["sampled"], sample_rate=0.9)

        def test_tags_and_samples(self):
            for i in range(100):
                self.statsd.gauge('gst', 23, tags=["sampled"], sample_rate=0.9)
            t.assert_equal('gst:23|g|@0.9|#sampled')

    # Test Client level contant tags
    def test_gauge_constant_tags(self):
        self.statsd.constant_tags=['bar:baz', 'foo']
        self.statsd.gauge('gauge', 123.4)
        assert self.recv() == 'gauge:123.4|g|#bar:baz,foo'

    def test_counter_constant_tag_with_metric_level_tags(self):
        self.statsd.constant_tags=['bar:baz', 'foo']
        self.statsd.increment('page.views', tags=['extra'])
        t.assert_equal('page.views:1|c|#extra,bar:baz,foo', self.recv())

    @staticmethod
    def assert_almost_equal(a, b, delta):
        assert 0 <= abs(a - b) <= delta, "%s - %s not within %s" % (a, b, delta)

    def test_socket_error(self):
        self.statsd.socket = BrokenSocket()
        self.statsd.gauge('no error', 1)
        assert True, 'success'

    def test_batched(self):
        self.statsd.open_buffer()
        self.statsd.gauge('page.views', 123)
        self.statsd.close_buffer()

        t.assert_equal('page.views:123|g', self.recv())

    def test_context_manager(self):
        fake_socket = FakeSocket()
        with OneStatsd() as statsd:
            statsd.socket = fake_socket
            statsd.gauge('page.views', 123)

        t.assert_equal('page.views:123|g', fake_socket.recv())

    def test_batched_buffer_autoflush(self):
        fake_socket = FakeSocket()
        with OneStatsd() as statsd:
            statsd.socket = fake_socket
            for i in range(51):
                statsd.increment('mycounter')
            t.assert_equal('\n'.join(['mycounter:1|c' for i in range(50)]), fake_socket.recv())

        t.assert_equal('mycounter:1|c', fake_socket.recv())

    def test_module_level_instance(self):
        t.assert_true(isinstance(statsd, OneStatsd))

    def test_instantiating_does_not_connect(self):
        onepound = OneStatsd()
        t.assert_equal(None, onepound.socket)

    def test_accessing_socket_opens_socket(self):
        onepound = OneStatsd()
        try:
            t.assert_not_equal(None, onepound.get_socket())
        finally:
            onepound.socket.close()

    def test_accessing_socket_multiple_times_returns_same_socket(self):
        onepound = OneStatsd()
        fresh_socket = FakeSocket()
        onepound.socket = fresh_socket
        t.assert_equal(fresh_socket, onepound.get_socket())
        t.assert_not_equal(FakeSocket(), onepound.get_socket())

if __name__ == '__main__':
    statsd = statsd
    while True:
        statsd.gauge('test.gauge', 1)
        statsd.increment('test.count', 2)
        time.sleep(0.05)
