from cloudinsight import OneStatsd

# default statsd address is localhost:8251
statsd = OneStatsd('localhost', 8251)

statsd.increment('page.views')
statsd.gauge('users.online', 123)
