from cloudinsight import statsd

# Increment a counter by default value 1.
statsd.increment('page.views')

# Increment a counter by value you specified.
statsd.increment('page.views', 100)

# Decrement a counter by default value 1.
statsd.decrement('page.views')

# Record a gauge metric.
statsd.gauge('users.online', 123)
