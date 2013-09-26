#!/usr/bin/env python

import requests

GITHUB_URL = 'https://api.github.com'

class GitHub:
  def __init__(self, access_token):
    self._authorization = 'token %s' % access_token

  def __getattr__(self, attr):
    return _Callable(self, '/%s' % attr)

  def _http(self, method, path, **kw):
    url = '%s%s' % (GITHUB_URL, path)
    if not 'headers' in kw:
      kw['headers'] = dict()
    kw['headers']['Authorization'] = self._authorization

    return getattr(requests, method)(url, **kw)


class _Executable:
  def __init__(self, gh, method, path):
    self._gh = gh
    self._method = method
    self._path = path

  def __call__(self, **kw):
    return self._gh._http(self._method, self._path, **kw).json()


class _Callable(object):
  def __init__(self, gh, name):
    self._gh = gh
    self._name = name

  def __call__(self, *args):
    if len(args) == 0:
      return self

    name = '%s/%s' % (self._name, '/'.join([str(arg) for arg in args]))
    return _Callable(self._gh, name)

  def __getattr__(self, attr):
    if attr in ['get', 'put', 'post', 'patch', 'delete']:
      return _Executable(self._gh, attr, self._name)

    name = '%s/%s' % (self._name, attr)
    return _Callable(self._gh, name)
