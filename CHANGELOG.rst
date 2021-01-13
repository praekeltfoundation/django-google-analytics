Changelog
=========

5.0.2
----------
# Default to HTTPS to avoid redirect

5.0.1
----------
# Remove djcelery
Upgrade python 3.8

4.4.2
----------
# Add support for Django 3.1

4.4.1
----------
# Add Django 3.0 and Python 3.8 support

4.4.0
----------
# Add django 2.2+ support, drop support for python 2

4.3.10
----------
# Add gclid parameter for Campaign auto-tagging

4.3.9
----------
# Reset security settings

4.3.8
----------
# Add non-interactive (ni) parameter for GA tracking

4.3.7
----------
#. Ensure that the correct Campaign parameters are being sent to GA

4.3.6
----------
#.Ensure correct user IP is pulled from proxy header if it exists

4.3.5
----------
#.Remove self referral traffic

4.3.4
----------
#.Remove dr from URL logging

4.3.3
----------
#.Add user agent for GA logging

4.3.2
----------
#.Add leading text for GA logging

4.3.1
----------
#. Enable GA logging setting

4.3.0
----------
#. Add custom parameters to build_ga_params

4.2.0
----------
#. Add uid to GA params

4.1.0
----------
#. Add support for Python 3

4.0.0
-----
#. Supports Django 1.11

3.0.0
-----
#. Now only supports Django 1.10

2.1.6
-----
#. Fix encoding for title

2.1.5
-----
#. Fix encoding in URL

2.1.4
-----
#. get language from request utils.py

2.1.3
-----
#. fix header name for Accepts-Language in tasks.py

2.1.2
-----
#. ensure we fill in the page title if it's available

2.1.1
-----
#. bug - build_ga_params expects account to be supplied
#. replace httplib2 with requests

2.1.0
-----
#. Allow uip to be overridden using custom header

2.0.3
-----
#. Use x-forwarded-for for ip address

2.0.2
-----
#. Django 1.6 not required

2.0.1
-----
#. Use correct URL for GA Measurement Protocol v1

2.0.0
-----
#. Upgrade to GA Measurement Protocol v1

1.0.0
-----
#. Make compatible with Django 1.6

0.0.5
-----
#. Removed Jmbo dependency, renamed.

0.0.4
-----
#. Better packaging.

0.0.3
-----
#. Fork, rename, re-license from panomena-analytics.
