from setuptools import setup, find_packages
import sys

setup(
    name = "cloudinsight",
    version = "0.1.0",
    author = "Cloud Insight",
    author_email = "support@oneapm.com",
    description = "Python SDK for Cloud Insight.",
	packages=[
		'cloudinsight',
		'cloudinsight.onestatsd',
	],
    keywords = "oneapm oneapm_ci cloudinsight",
    url = "http://www.oneapm.com/ci/feature.html"
)
