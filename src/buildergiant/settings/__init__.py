"""
Settings
=======================

Settings are composed of two things

* **base**: These settings don't change with environments. Refers to file
``buildergiant/settings/base.py``
* **local**: Add / override settings parameters according your local environments \
``buildergiant/settings/local.py``.

Few settings are mandatory in local. See the base setting section
"""

from .base import *


# Try to load local settings. That is usually related local environments
try:
    from .local import *
except ImportError:
    pass
