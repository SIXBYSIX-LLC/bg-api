"""
***
Usr
***
Aka User (because django doesn't allow to have user). This app extends the User auth module and
adds new module of Address


User Hierarchy
--------------
To build the hierarchy, user can create a user and reference is stored in ``Profile.user``. For
now, only one level is possible though multi-level shouldn't be difficult.

When new user is registered by the Device group, user is assigned `User` group by the system
(``tasks.assign_group`` is responsible for that). Further user can assign group and permissions
to his child users.

Whatever child user perform it'll be done behalf of the parent user


Modules
-------
"""
default_app_config = 'usr.apps.UserConfig'
