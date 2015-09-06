"""
*****
Group
*****
A generic way of applying labels and permissions to more than one user.

The standard django group model has only name and permission fields, our requirements is user to
have ability to create his own groups and permission assigned to them. Hence I extended it.


Default Groups
--------------
Whenever new system is deployed the following groups will be available:

* ``Device``: From whatever the platform is accessible (like android, ios, browser) are under \
these groups. Such user has very limited permissions (see management command).
* ``User``: Typical user (buyer/seller) will be under these group

Modules
-------
"""
