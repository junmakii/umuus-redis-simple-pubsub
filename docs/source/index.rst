
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
    4) "{"x": 2.0, "y": 3.0}"

    1) "pmessage"
    2) "*"
    3) "example:func:on_completed:12345678"
    4) "{"data": 6.0}"

    ----

    $ redis-cli PUBLISH 'example:func:on_next:12345678'   '{"x": 2.0, "y": "3.0"}'

    1) "pmessage"
    2) "*"
    3) "example:func:on_error:12345678"
    4) "{'error': TypeError("can't multiply sequence by non-int of type 'float'")}"


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

Table of Contents
-----------------
.. toctree::
   :maxdepth: 2
   :glob:

   *

