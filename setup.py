
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def run_tests(self):
        import sys
        import shlex
        import pytest
        errno = pytest.main(['--doctest-modules'])
        if errno != 0:
            raise Exception('An error occured during installution.')
        install.run(self)


setup(
    packages=setuptools.find_packages('.'),
    version='0.1',
    url='https://github.com/junmakii/umuus-redis-simple-pubsub',
    author='Jun Makii',
    author_email='junmakii@gmail.com',
    keywords=[],
    license='GPLv3',
    scripts=[],
    install_requires=['addict>=2.2.0',
 'attrs>=18.2.0',
 'fire>=0.1.3',
 'toolz>=0.9.0',
 'redis>=3.0.1'],
    dependency_links=[],
    classifiers=[],
    entry_points={'console_scripts': ['umuus_redis_simple_pubsub = '
                     'umuus_redis_simple_pubsub:main'],
 'gui_scripts': []},
    project_urls={},
    setup_requires=[],
    test_suite='',
    tests_require=[],
    extras_require={},
    package_data={},
    python_requires='',
    include_package_data=True,
    zip_safe=True,
    name='umuus-redis-simple-pubsub',
    description="A simple decorator functions for Redis' Pub/Sub on Python.",
    long_description=("A simple decorator functions for Redis' Pub/Sub on Python.\n"
 '\n'
 'umuus-redis-simple-pubsub\n'
 '=========================\n'
 '\n'
 'Installation\n'
 '------------\n'
 '\n'
 '    $ pip install '
 'git+https://github.com/junmakii/umuus-redis-simple-pubsub.git\n'
 '\n'
 'Example\n'
 '-------\n'
 '\n'
 '    $ umuus_redis_simple_pubsub\n'
 '\n'
 '    >>> import umuus_redis_simple_pubsub\n'
 '\n'
 '----\n'
 '\n'
 'Usage\n'
 '-----\n'
 '\n'
 '    $ export UMUUS_REDIS_SIMPLE_PUBSUB=REDIS_CONFIG.json\n'
 '\n'
 '    $ cat REDIS_CONFIG.json\n'
 '\n'
 '    {\n'
 '        "host": "redis",\n'
 '        "port": 6379,\n'
 '        "password": "12345678"\n'
 '    }\n'
 '\n'
 '    $ python -m umuus_redis_simple_pubsub run --options \'{"module": '
 '"example"}\'\n'
 '\n'
 '    $ python -m umuus_redis_simple_pubsub run --options \'{"paths": '
 '["example:f", "example:g"]}\'\n'
 '\n'
 '    ----\n'
 '\n'
 "    umuus_redis_simple_pubsub.from_modules(['example'])\n"
 "    umuus_redis_simple_pubsub.from_paths(['example:f'])\n"
 '\n'
 '    ----\n'
 '\n'
 '\n'
 '    @umuus_redis_simple_pubsub.subscribe()\n'
 '    def f(x, y):\n'
 '        return x * y\n'
 '\n'
 '\n'
 '    @umuus_redis_simple_pubsub.publish()\n'
 '    def g(x, y):\n'
 '        return x * y\n'
 '\n'
 '\n'
 '    umuus_redis_simple_pubsub.run()\n'
 '\n'
 '    ----\n'
 '\n'
 "    $ redis-cli PSUBSCRIBE '*' &\n"
 '\n'
 '    $ redis-cli PUBLISH \'example:func:on_next:12345678\'   \'{"x": 2.0, '
 '"y": 3.0}\'\n'
 '\n'
 '    1) "pmessage"\n'
 '    2) "*"\n'
 '    3) "example:func:on_next:12345678"\n'
 '    4) "{"x": 2.0, "y": 3.0}"\n'
 '\n'
 '    1) "pmessage"\n'
 '    2) "*"\n'
 '    3) "example:func:on_completed:12345678"\n'
 '    4) "{"data": 6.0}"\n'
 '\n'
 '    ----\n'
 '\n'
 '    $ redis-cli PUBLISH \'example:func:on_next:12345678\'   \'{"x": 2.0, '
 '"y": "3.0"}\'\n'
 '\n'
 '    1) "pmessage"\n'
 '    2) "*"\n'
 '    3) "example:func:on_error:12345678"\n'
 '    4) "{\'error\': TypeError("can\'t multiply sequence by non-int of type '
 '\'float\'")}"\n'
 '\n'
 '\n'
 '----\n'
 '\n'
 '\n'
 '@subscribe()\n'
 'def f(x, y): return x * y\n'
 '\n'
 '\n'
 'import threading; threading.Thread(target=lambda: listen()).start()\n'
 '\n'
 'f.dispatch(x=2, y=2).wait()  # 4\n'
 '\n'
 '\n'
 'Authors\n'
 '-------\n'
 '\n'
 '- Jun Makii <junmakii@gmail.com>\n'
 '\n'
 'License\n'
 '-------\n'
 '\n'
 'GPLv3 <https://www.gnu.org/licenses/>'),
    cmdclass={"pytest": PyTest},
)
