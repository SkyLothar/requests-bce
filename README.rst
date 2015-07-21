BCE using python-requests
============================

Version
-------
v0.0.1

.. image:: https://img.shields.io/travis/skylothar/requests-bce.svg?style=flat-square
    :target: https://travis-ci.org/SkyLothar/requests-bce

.. image:: https://img.shields.io/coveralls/skylothar/requests-bce/master.svg?style=flat-square
    :target: https://coveralls.io/r/SkyLothar/requests-bce

.. image:: https://requires.io/github/SkyLothar/requests-bce/requirements.svg?branch=master
    :target: https://requires.io/github/SkyLothar/requests-bce/requirements/?branch=master

.. image:: https://img.shields.io/pypi/v/requests-aliyun.svg?style=flat-square
    :target: https://pypi.python.org/pypi/requests-bce/
    :alt: Supported Python versions

.. image:: https://img.shields.io/github/license/skylothar/requests-bce.svg?style=flat-square
    :target: https://pypi.python.org/pypi/requests-bce/
    :alt: License



BCE authentication for the awesome requests!
--------------------------------------------
support auth version: v1

- [x] BCM


How to Install
--------------
Just

.. code-block:: bash

   pip install requests-bce


How to Use
----------
Just pass the auth object to requests

.. code-block:: python

    >>> import requests
    >>> from bceauth import V1Auth
    >>> req = requests.post(
    ...     "http://example.com/path/to/file",
    ...     auth=V1Auth("access-key", "secret-key")
    ... )
    <Response [200]>

Or set the auth attribute to the session object

.. code-block:: python

    >>> import requests
    >>> from bceauth import V1Auth
    >>> session = requests.session()
    >>> session.auth = V1Auth("access-key", "secret-key")
    >>> req = session.get("http://example.com/path/to/file")
    <Response [200]>
