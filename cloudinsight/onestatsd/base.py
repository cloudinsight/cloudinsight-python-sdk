#!/usr/bin/env python
"""
OneStatsd is a Python client for OneStatsd, a Statsd fork for Cloud Insight.
"""

import logging
from random import random
import socket

try:
    from itertools import imap
except ImportError:
    imap = map


log = logging.getLogger('onestatsd')


class OneStatsd(object):
    OK, WARNING, CRITICAL, UNKNOWN = (0, 1, 2, 3)

    def __init__(self, host='localhost', port=8251, max_buffer_size=50,
                 constant_tags=None, use_ms=False):
        """
        Initialize a OneStatsd object.

        >>> statsd = OneStatsd()

        :param host: the host of the OneStatsd server.
        :type host: string

        :param port: the port of the OneStatsd server.
        :type port: integer

        :param max_buffer_size: Maximum number of metrics to buffer before sending to the server
        if sending metrics in batch
        :type max_buffer_size: integer

        :param constant_tags: Tags to attach to every metric reported by this client
        :type constant_tags: list of strings

        :param use_ms: Report timed values in milliseconds instead of seconds (default False)
        :type use_ms: boolean
        """
        self.host = host
        self.port = int(port)
        self.socket = None
        self.max_buffer_size = max_buffer_size
        self._send = self._send_to_server
        self.encoding = 'utf-8'
        self.constant_tags = constant_tags
        self.use_ms = use_ms

    def __enter__(self):
        self.open_buffer(self.max_buffer_size)
        return self

    def __exit__(self, type, value, traceback):
        self.close_buffer()

    def get_socket(self):
        """
        Return a connected socket.

        Note: connect the socket before assigning it to the class instance to
        avoid bad thread race conditions.
        """
        if not self.socket:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect((self.host, self.port))
            self.socket = sock
        return self.socket

    def open_buffer(self, max_buffer_size=50):
        """
        Open a buffer to send a batch of metrics in one packet.

        You can also use this as a context manager.

        >>> with OneStatsd() as batch:
        >>>     batch.gauge('users.online', 123)
        >>>     batch.gauge('active.connections', 1001)
        """
        self.max_buffer_size = max_buffer_size
        self.buffer = []
        self._send = self._send_to_buffer

    def close_buffer(self):
        """
        Flush the buffer and switch back to single metric packets.
        """
        self._send = self._send_to_server
        self._flush_buffer()

    def gauge(self, metric, value, tags=None, sample_rate=1):
        """
        Record the value of a gauge, optionally setting a list of tags and a
        sample rate.

        >>> statsd.gauge('users.online', 123)
        >>> statsd.gauge('active.connections', 1001, tags=["protocol:http"])
        """
        return self._report(metric, 'g', value, tags, sample_rate)

    def increment(self, metric, value=1, tags=None, sample_rate=1):
        """
        Increment a counter, optionally setting a value, tags and a sample
        rate.

        >>> statsd.increment('page.views')
        >>> statsd.increment('files.transferred', 124)
        """
        self._report(metric, 'c', value, tags, sample_rate)

    def decrement(self, metric, value=1, tags=None, sample_rate=1):
        """
        Decrement a counter, optionally setting a value, tags and a sample
        rate.

        >>> statsd.decrement('files.remaining')
        >>> statsd.decrement('active.connections', 2)
        """
        self._report(metric, 'c', -value, tags, sample_rate)

    def _report(self, metric, metric_type, value, tags, sample_rate):
        if sample_rate != 1 and random() > sample_rate:
            return

        payload = [metric, ":", value, "|", metric_type]
        if sample_rate != 1:
            payload.extend(["|@", sample_rate])

        # Append all client level tags to every metric
        if self.constant_tags:
            if tags:
                tags += self.constant_tags
            else:
                tags = self.constant_tags

        if tags:
            payload.extend(["|#", ",".join(tags)])

        encoded = "".join(imap(str, payload))
        self._send(encoded)

    def _send_to_server(self, packet):
        try:
            # If set, use socket directly
            (self.socket or self.get_socket()).send(packet.encode(self.encoding))
        except socket.error:
            log.info("Error submitting packet, will try refreshing the socket")
            self.socket = None
            try:
                self.get_socket().send(packet.encode(self.encoding))
            except socket.error:
                log.exception("Failed to send packet with a newly binded socket")

    def _send_to_buffer(self, packet):
        self.buffer.append(packet)
        if len(self.buffer) >= self.max_buffer_size:
            self._flush_buffer()

    def _flush_buffer(self):
        self._send_to_server("\n".join(self.buffer))
        self.buffer = []


statsd = OneStatsd()
