from cloudinsight import statsd

# Record a metric at a sample rate 50%(eg. 50% of the time the metirc will be recorded).
# Default sample rate is 100%, means record every metric.
statsd.gauge('users.online', 123, sample_rate=0.5)
