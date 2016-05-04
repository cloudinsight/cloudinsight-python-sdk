from cloudinsight import statsd

# This metric will carry tags gender:male and region:north
statsd.gauge('users.online', 123, tags=['gender:male','region:north'])


# If you wanna every metric you collect carry common tags, there is a easy way.
from cloudinsight import OneStatsd
statsd = OneStatsd('localhost', 8251, constant_tags=['k1:v1', 'k2:v2'])

# Every metric you collect will carry tag k1:v1 and k2:v2.
statsd.gauge('users.online', 123)
statsd.increment('page.views')
