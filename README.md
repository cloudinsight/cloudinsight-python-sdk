Cloud Insight Python SDK
================

Installation
------------
To install from pip:

		pip install -i http://pypi.oneapm.com/simple --trusted-host pypi.oneapm.com --upgrade cloudinsight

To install from source:

    python setup.py install


Quick Start Guide
-----------------

``` python
# Import the module. In this manner, you'll connect to OneStatsd at localhost:8251
from cloudinsight import statsd
# or specify your OneStatsd address.
# from cloudinsight import OneStatsd
# statsd = OneStatsd('localhost', 8251) #, constant_tags=['k1:v1', 'k2:v2'])
# once constant_tags is spedified, every metric will carry the tags

# Increment a counter by default value 1.
statsd.increment('page.views')

# Increment a counter by value you specified.
statsd.increment('page.views', 100)

# Record a metric at a sample rate 50%(eg. 52% of the time the metirc will be recorded).
statsd.gauge('users.online', 123, sample_rate=0.5)
statsd.increment('page.views', sample_rage=0.5)

# Record a tagged metric.
statsd.gauge('users.online', 123, tags=['gender:male','region:north'])
```

See document at: http://docs-ci.oneapm.com/api/python.html
