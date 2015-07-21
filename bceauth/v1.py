# -*- coding:utf8 -*-

"""
bceauth.v1
~~~~~~~~~~

This module contains the authentication handlers for BCE AUTH Version 1
"""

import hashlib
import hmac
import logging
import mimetypes
import time

import requests

from . import url
from . import utils


logger = logging.getLogger(__name__)


class AuthV1(requests.auth.AuthBase):
    """Attach BCE V1 Authentication to the given request

    :param access_key: the access_key of your ecs account
    :param secret_key: the secret_key of your ecs account
    :param response_format: (optional) response format [`xml`/`json`(default)]
    :param ram: (optional) resource access managment string (default None)
    """

    TIME_FMT = "%Y-%m-%dT%H:%M:%SZ"
    EXPIRES_IN = 60
    BCE_HEADER_PREFIX = "x-bce-"
    DEFAULT_TYPE = "application/octstream"
    HEADERS_TO_SIGN = (
        "host",
        "content-length",
        "content-type",
        "content-md5"
    )

    def __init__(self, access_key, secret_key):
        self._access_key = utils.to_str(access_key)
        self._secret_key = utils.to_bytes(secret_key)

    def prefill_headers(self, request, parsed_url):
        # set host
        request.headers.setdefault("host", parsed_url.netloc)
        # set content-type
        content_type = request.headers.get("content-type")
        if content_type is None:
            content_type, __ = mimetypes.guess_type(parsed_url.path)
        request.headers["content-type"] = content_type or self.DEFAULT_TYPE
        # set content-md5
        if request.body is not None and "content-md5" not in request.headers:
            request.headers["content-md5"] = utils.cal_b64md5(request.body)

    def get_canonical_request(self, request, parsed_url):
        canonical_uri = utils.percent_quote(parsed_url.path, except_slash=True)
        canonical_query = utils.percent_encode(
            parsed_url.params.items(),
            sort=True
        )

        headers_to_sign = [
            (
                "{0}:{1}".format(
                    utils.percent_quote(key.strip()),
                    utils.percent_quote(val.strip())
                ),
                key
            )
            for key, val in request.headers.lower_items()
            if val and self.need_to_sign(key)
        ]
        headers_to_sign.sort()
        signed_headers_list = []
        canonical_headers_list = []
        for header_str, key in sorted(headers_to_sign):
            signed_headers_list.append(key)
            canonical_headers_list.append(header_str)

        signed_headers = ";".join(signed_headers_list)
        canonical_headers = "\n".join(canonical_headers_list)

        canonical_request = "\n".join([
            request.method,
            canonical_uri,
            canonical_query,
            canonical_headers
        ])
        return canonical_request, signed_headers

    def need_to_sign(self, key):
        return key in self.HEADERS_TO_SIGN \
            or key.startswith(self.BCE_HEADER_PREFIX)

    @property
    def access_key(self):
        return self._access_key

    @property
    def secret_key(self):
        return self._secret_key

    @property
    def timestamp(self):
        return time.strftime(self.TIME_FMT, time.gmtime())

    def get_sign_key(self, signed_headers, expires_in=None):
        auth_prefix = "/".join([
            "bce-auth-v1",
            self.access_key,
            time.strftime(self.TIME_FMT, time.gmtime()),
            utils.to_str(expires_in or self.EXPIRES_IN)
        ])

        sign_key = hmac.HMAC(
            self.secret_key, utils.to_bytes(auth_prefix), hashlib.sha256
        ).hexdigest()
        return auth_prefix, utils.to_bytes(sign_key)

    def get_auth_string(self, request):
        parsed_url = url.URL(request.url)
        self.prefill_headers(request, parsed_url)

        canonical_request, signed_headers = self.get_canonical_request(
            request, parsed_url
        )
        auth_prefix, sign_key = self.get_sign_key(
            signed_headers=signed_headers
        )
        signature = hmac.HMAC(
            sign_key, utils.to_bytes(canonical_request), hashlib.sha256
        ).hexdigest()

        auth_string = "/".join([
            auth_prefix, signed_headers, signature
        ])
        return auth_string

    def __call__(self, req):
        """Sign the request"""
        auth_string = self.get_auth_string(req)
        req.headers["Authorization"] = auth_string
        return req
