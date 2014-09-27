
mezzanine-invites
=================

A `Mezzanine`_ application that allows site registration via alphanumeric
invite codes. It is designed to enable a quick sign up process for invited
potential site users.

Usage
-----

A site admin creates an Invite Code linked with at least the invitee's email
address and possibly also their full name and phone number. This code's key (a
short alphanumeric token) is sent to the invitee and, if they choose to use
it, the first login with the code will create a new site user.

An Invite Code must be used to register within the number of days given by
the ``INVITE_CODE_USAGE_WINDOW`` setting (default 14 days), and once
registered, the code is valid for the number of days given by
``INVITE_CODE_EXPIRY_DAYS`` (default 30 days).

The code is always of the form::

    <Three or more uppercase letters><three digits>

For example, **ABCXYZ123**. The default code length is 9 but this is
configurable via the ``INVITE_CODE_LENGTH`` setting.


The ``send_invite`` view
------------------------

Include ``invites.urls`` in your ``URL_CONF`` to get a staff-only view called
``send-invite`` which will display a form with email, name and phone fields.
Click **Send Invite** to send an email with the unique code to the recipient.

The ``invite`` management command
---------------------------------

Create a code with the Django management command ``invite``::

    ./bin/django invite

which will prompt for an email address for the invitee.

You can also specify the email as a paramter::

    ./bin/django invite --email=joe.soap@lux.com

Invitation Codes are associated with a given ``Site``, so if there are multiple
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

The ``INVITE_CODE_LENGTH`` setting determines the length of the invite code.
It ought to be an integer greater than or equal to 6 and less than or equal
to 30.

The ``INVITE_CODE_USAGE_WINDOW`` setting determines how many days before an
Invite Token must be used.

Once used to register with a site the ``INVITE_CODE_EXPIRY_DAYS`` setting
determines how many days before the Invite Token becomes invalid.

In order for the invite code to be acceptable as a login token, add the
``InviteAuthBackend`` to the list of ``AUTHENTICATION_BACKENDS`` in settings::

    AUTHENTICATION_BACKENDS = (
        "mezzanine.core.auth_backends.MezzanineBackend",
        "invites.auth.InviteAuthBackend",
    )

Caution
-------

::

    This is an inherently less secure means of authentication compared to
    the regular username/password flow. The Invite Code Token gives immediate
    site access and yet:

        + may have been sent in a plain text email
        + exists in the database in plain text form
        + does not require knowledge of the associated username
        + may not be very strong cryptographically

    In addition, for the convenience of (possibly unsophisticated) users, on
    first usage of an Invite Token, the newly created user's password is set
    to this same token. This enables a user to immediately use the regular
    'username/password' login form if they so wish but leaves them with a less
    secure password than otherwise.

    This inherent risk is mitigated by the INVITE_CODE_EXPIRY_DAYS setting
    and by a 'set_unusable_password' call if the password hasn't been changed
    within the expiry time. In strict environments, both the
    INVITE_CODE_EXPIRY_DAYS and INVITE_CODE_USAGE_WINDOW settings should be
    low numbers. Once expired, a user will be forced to set up their own
    password by the standard means. There ought to be additional out-of-band
    checks for those users who haven't created a different password, ie. for
    whom `check_password(<INVITE-TOKEN>)` is True.


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



