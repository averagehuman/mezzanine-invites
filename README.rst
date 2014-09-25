
mezzanine-invites
=================

A `Mezzanine`_ application that allows site registration via alphanumeric
invite codes. The code is always of the form::

    [zero or more uppercase letters]<three digits>

For example, ABCXYZ123. The default code length is 9 but this is
configurable via the `INVITE_CODE_LENGTH` setting.

Usage
-----

Via the `send_invite` view
~~~~~~~~~~~~~~~~~~~~~~~~~~

Include `invites.urls` in your URL_CONF to get a staff-only view called
*send-invite* which will display a form with email, name and phone fields.
Click `Send Invite` to send an email with the unique code to the recipient.

Via the `invite` management command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a code with the Django management command 'invite'::

    ./bin/django invite

which will prompt for an email address for the invitee.

You can also specify the email as a paramter::

    ./bin/django invite --email=joe.soap@lux.com

Invitation Codes are associated with a given `Site`, so if there are multiple
sites,then you need to specify which by domain name::

    ./bin/django invite --domain=example.com

Once created you will be asked if you want to send the invitation right away.
If you decline then the code will simply be printed out.

Email Backend
-------------

To send emails, an appropriate email backend must be configured. See the
`Django email docs`_ for more information.


Settings
--------

The `INVITE_CODE_LENGTH` setting determines the length of the invite code.
It ought to be an integer greater or equal than 3.

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

in settings.

If Invite Codes are not reusable after the first use, then it is up to the
application to ensure that the invited user subsequently has some other means
of authorisation. The simplest way to do this may be to have a custom
`AUTH_USER_MODEL` with an email field as a primary key (ie. with unique=True),
since in this case login can always be possible via the usual 'recover password'
mechanism.


Source and Issues
-----------------

Source is on `github`_.

.. _github: https://github.com/averagehuman/mezzanine-invites
.. _mezzanine: http://mezzanine.jupo.org
.. _django email docs: https://docs.djangoproject.com/en/dev/topics/email/

Testing with tox/pytest
~~~~~~~~~~~~~~~~~~~~~~~

Run tests with::

    make test

which is just an alias for::

    python setup.py test



