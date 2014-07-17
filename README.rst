
mezzanine-invites
=================

A `Mezzanine`_ application that allows site registration via alphanumeric
invite codes.

Usage
-----

Create a code with the Django management command 'invite'::

    ./bin/django invite --domain=mysite.com

Optionally, associate the code with an email address::

    ./bin/django invite --domain=mysite.com --email=joe.soap@lux.com


Source and Issues
'''''''''''''''''

Source is on `github`_.

.. _github: https://github.com/averagehuman/mezzanine-invites
.. _mezzanine: http://mezzanine.jupo.org

Testing with tox/pytest
'''''''''''''''''''''''

Run tests with::

    make test

which is just an alias for::

    python setup.py test



