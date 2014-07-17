
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

In order for the invite code to be acceptable as a login token, add the
`InviteAuthBackend` to the list of AUTHENTICATION_BACKENDS in settings::

    AUTHENTICATION_BACKENDS = (
        "mezzanine.core.auth_backends.MezzanineBackend",
        "invites.auth.InviteAuthBackend",
    )

Then, once a valid code is entered, a new user is automatically created and
logged in.

By default, the invite code is reusable as a login token - if this is not
desirable then set::

    INVITE_CODES_ARE_REUSABLE = False

in settings. It is then up to the application to ensure that the invited
user subsequently updates their account with a valid username/password,
in order for regular logins to be possible.


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



