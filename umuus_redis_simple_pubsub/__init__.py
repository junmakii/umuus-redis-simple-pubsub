#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Jun Makii <junmakii@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""Utilities, tools, and scripts for Python.

umuus-redis-simple-pubsub
=========================

Installation
------------

    $ pip install git+https://github.com/junmakii/umuus-redis-simple-pubsub.git

Example
-------

    $ umuus_redis_simple_pubsub

    >>> import umuus_redis_simple_pubsub

----

Usage
-----

    $ export UMUUS_REDIS_SIMPLE_PUBSUB=REDIS_CONFIG.json

    $ cat REDIS_CONFIG.json

    {
        "host": "redis",
        "port": 6379,
        "password": "12345678"
    }

    $ python -m umuus_redis_simple_pubsub run --options '{"module": "example"}'

    $ python -m umuus_redis_simple_pubsub run --options '{"paths": ["example:f", "example:g"]}'

    ----

    umuus_redis_simple_pubsub.from_modules(['example'])
    umuus_redis_simple_pubsub.from_paths(['example:f'])

    ----


    @umuus_redis_simple_pubsub.subscribe()
    def f(x, y):
        return x * y


    @umuus_redis_simple_pubsub.publish()
    def g(x, y):
        return x * y


    umuus_redis_simple_pubsub.run()

    ----

    $ redis-cli PSUBSCRIBE '*' &

    $ redis-cli PUBLISH 'example:func:on_next:12345678'   '{"x": 2.0, "y": 3.0}'

    1) "pmessage"
    2) "*"
    3) "example:func:on_next:12345678"
    4) "{\"x\": 2.0, \"y\": 3.0}"

    1) "pmessage"
    2) "*"
    3) "example:func:on_completed:12345678"
    4) "{\"data\": 6.0}"

    ----

    $ redis-cli PUBLISH 'example:func:on_next:12345678'   '{"x": 2.0, "y": "3.0"}'

    1) "pmessage"
    2) "*"
    3) "example:func:on_error:12345678"
    4) "{'error': TypeError(\"can't multiply sequence by non-int of type 'float'\")}"


----


@subscribe()
def f(x, y): return x * y


import threading; threading.Thread(target=lambda: listen()).start()

f.dispatch(x=2, y=2).wait()  # 4


Authors
-------

- Jun Makii <junmakii@gmail.com>

License
-------

GPLv3 <https://www.gnu.org/licenses/>

"""
import toolz
import time
import types
import os
import sys
import redis
import attr
import json
import uuid
import fire
import functools
import addict
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=(__name__ == '__main__' and 'DEBUG' or
           os.environ.get(__name__.upper().replace('.', '__') + '_LOG_LEVEL')
           or os.environ.get('LOGGING_LOG_LEVEL') or 'DEBUG'),
    stream=sys.stdout)
logger.setLevel(
    __name__ == '__main__' and 'DEBUG'
    or os.environ.get(__name__.upper().replace('.', '__') + '_LOG_LEVEL')
    or os.environ.get('LOGGING_MODULE_LOG_LEVEL') or 'WARNING')
__version__ = '0.1'
__url__ = 'https://github.com/junmakii/umuus-redis-simple-pubsub'
__author__ = 'Jun Makii'
__author_email__ = 'junmakii@gmail.com'
__author_username__ = 'junmakii'
__keywords__ = []
__license__ = 'GPLv3'
__scripts__ = []
__install_requires__ = [
    'addict>=2.2.0',
    'attrs>=18.2.0',
    'fire>=0.1.3',
    'toolz>=0.9.0',
    'redis>=3.0.1',
]
__dependency_links__ = []
__classifiers__ = []
__entry_points__ = {
    'console_scripts':
    ['umuus_redis_simple_pubsub = umuus_redis_simple_pubsub:main'],
    'gui_scripts': [],
}
__project_urls__ = {}
__setup_requires__ = []
__test_suite__ = ''
__tests_require__ = []
__extras_require__ = {}
__package_data__ = {}
__python_requires__ = ''
__include_package_data__ = True
__zip_safe__ = True
__static_files__ = {}
__extra_options__ = {}
__download_url__ = ''
__all__ = []

instance = redis.Redis(**json.load(open(os.environ.get(__name__.upper()))))
pubsub = instance.pubsub()
serializer = (
    lambda _: toolz.excepts(Exception, lambda _: json.dumps(_), lambda err: str(_))(_)
)
normalizer = (
    lambda _: toolz.excepts(Exception, lambda _: addict.Dict(json.loads(_)), lambda err: addict.Dict(message=_))(_)
)
subscriptions = []
encoding = sys.getdefaultencoding()


@attr.s()
class Subscription(object):
    fn = attr.ib()
    name = attr.ib(None)

    def __attrs_post_init__(self):
        self.name = to_keyname(self.fn)

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    def dispatch(self, *args, **kwargs):
        self.current_task_id = str(uuid.uuid4())
        instance.publish(self.name + ':on_next:' + self.current_task_id,
                         serializer(kwargs))
        return self

    def wait(self):
        pubsub = instance.pubsub()
        pubsub.psubscribe([self.name + ':*:' + self.current_task_id])
        while True:
            message = pubsub.get_message()
            if message and message.get('type') == 'pmessage':
                name, event, id = message['channel'].decode(encoding).rsplit(
                    ':', 2)
                data = normalizer(message['data'].decode(encoding))
                pubsub.unsubscribe()
                if event == 'on_completed':
                    return data.get('data')
                else:
                    raise Exception(data.get('error'))
                break
            time.sleep(0.1)


def to_keyname(fn):
    return fn.__module__ + ':' + fn.__qualname__


def listen():
    pubsub.psubscribe([_.name + ':*' for _ in subscriptions])
    while True:
        message = pubsub.get_message()
        if message and message.get('type') == 'pmessage':
            logger.info(message)
            try:
                name, event, id = message['channel'].decode(encoding).rsplit(
                    ':', 2)
                sub = next(
                    iter([_ for _ in subscriptions if _.name == name]), None)
                if event == 'on_next':
                    result = sub.fn(
                        **normalizer(message.get('data').decode(encoding)))
                    instance.publish(sub.name + ':on_completed:' + id,
                                     serializer(dict(data=result)))
            except Exception as err:
                instance.publish(sub.name + ':on_error:' + id,
                                 serializer(dict(error=err)))
        time.sleep(0.1)


@toolz.curry
def subscribe(fn):
    subscription = Subscription(fn)
    subscriptions.append(subscription)
    return subscription


def unsubscribe(fn):
    subscriptions.remove(fn)


@toolz.curry
def publish(fn):
    name = to_keyname(fn)

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            result = fn(*args, **kwargs)
            instance.publish(name + ':on_completed:' + str(uuid.uuid4()),
                             serializer(dict(data=result)))
            return result
        except Exception as err:
            instance.publish(name + ':on_error:' + str(uuid.uuid4()),
                             serializer(dict(error=err)))
            raise err

    return wrapper


def from_modules(modules):
    fns = [
        attr for module_name in modules
        for module in [__import__(module_name)]
        for key, attr in vars(module).items()
        if isinstance(attr, types.FunctionType) and not key.startswith('_')
    ]
    list(map(subscribe, fns))
    listen()


def from_paths(paths):
    fns = [
        function for path in paths
        for module_name, function_name in [path.split(':')]
        for module in [__import__(module_name)]
        for function in [getattr(module, function_name)]
    ]
    list(map(subscribe, fns))
    listen()


def run(options={}):
    options = addict.Dict(options)
    logger.info(options)
    if options.modules:
        from_modules(options.modules)
    if options.module:
        from_modules([options.module])
    elif options.paths:
        from_paths(options.paths)
    elif options.path:
        from_paths([options.path])


def main(argv=[]):
    fire.Fire()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
