
mezzanine-invites
=================

A `Mezzanine`_ application that allows site registration via alphanumeric
invite codes. It is designed to enable a quick sign up process for invited
potential site users.

Development - `<https://github.com/averagehuman/mezzanine-invites>`_

Requirements
------------

Has been tested with **Django 1.7** and the latest **Mezzanine 3.1.*
development branch (master)** using both **Python 2.7** and **Python 3.3**.

Mezzanine versions **3.1.10** and earlier may also work if you can ignore or
workaround `Issue 1114`_.

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
determines how many days before the Invite Token becomes invalid as a login
token.

In order for the invite code to be acceptable as a login token, add the
``InviteAuthBackend`` to the list of ``AUTHENTICATION_BACKENDS`` in settings::

    AUTHENTICATION_BACKENDS = (
        "mezzanine.core.auth_backends.MezzanineBackend",
        "invites.auth.InviteAuthBackend",
    )

You can in fact just have ``InviteAuthBackend`` as the sole backend since it
is a subclass of the ``MezzanineBackend`` and will fall back to the latter's 
authentication::

    AUTHENTICATION_BACKENDS = (
        "invites.auth.InviteAuthBackend",
    )

The difference between the two setups is that if ``MezzanineBackend`` is
picking up the standard username/password login then it won't authenticate the
*first* use of an Invite Code or, obviously, create the newly-registered user,
whereas ``InviteAuthBackend`` will do both of those things.

Note, however, that if you have ``mezzanine.accounts`` in your
``INSTALLED_APPS`` setting, then ``MezzanineBackend`` will be added to the
list of backends anyway by the ``set_dynamic_settings`` call in your settings
module.


Templates
---------

The following templates are required.

+ invites/send_invite.html
+ invites/send_invite_email.txt
+ invites/send_invite_email.html

There are further templates to handle the default login scenario - a login
page that has two forms, one a standard **username/password/captcha** form,
and the other a **quick login** form requiring only the invite code.

+ accounts/account_form.html
+ accounts/account_login.html


Caution
-------

This is an inherently less secure means of authentication compared to
the regular username/password flow. The Invite Code Token gives immediate
site access and yet:

    + may have been sent in a plain text email
    + exists in the database in plain text form
    + does not require knowledge of the associated username
    + may not be very strong cryptographically

This inherent risk is mitigated by the ``INVITE_CODE_EXPIRY_DAYS`` setting.
In strict environments, both the ``INVITE_CODE_EXPIRY_DAYS`` and
``INVITE_CODE_USAGE_WINDOW`` settings should be low numbers. Once expired, a
user will still be registered and active but will not be able to login until
they have set up their own password by the standard means, eg. via a
**Forgotten Password** form.

Setting ``INVITE_CODE_EXPIRY_DAYS`` to **0** will cause Invite Codes to be
effectively "one-shot" tokens.

To expire a code that becomes invalid while that code's user is logged-in and
has an active session, a middleware component might be implemented to check
code expiry on each request and logout the user if necessary.

Source and Issues
-----------------

Source is on `github`_.

.. _github: https://github.com/averagehuman/mezzanine-invites
.. _mezzanine: http://mezzanine.jupo.org
.. _django email docs: https://docs.djangoproject.com/en/dev/topics/email/
.. _issue 1114: https://github.com/stephenmcd/mezzanine/issues/1114

Testing with tox/pytest
~~~~~~~~~~~~~~~~~~~~~~~

Run tests with::

    make test

which is just an alias for::

    python setup.py test



