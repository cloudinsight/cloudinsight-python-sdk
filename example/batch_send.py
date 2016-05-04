from cloudinsight import statsd

# Sometimes you may want ensure that the metric have same timestamp, this is
# the case.

# You can use context manager. The Default buffer size is 50, you can specify
# the max_buffer_size parameter when you init a new onestatsd instance.
with statsd as batch:
    batch.gauge('user.online', 12)
    batch.gauge('user.active', 43)
    batch.increment('page.view', 23)

# Or explictly call method.
statsd.open_buffer()
# Also you can specify the buffer size.
#statsd.open_buffer(max_buffer_size=50)
statsd.gauge('user.online', 12)
statsd.gauge('user.active', 43)
statsd.increment('page.view', 23)
statsd.close_buffer()
