# SPDX-FileCopyrightText: 2025 Magenta ApS <info@magenta.dk>
#
# SPDX-License-Identifier: MPL-2.0

from split_settings.tools import include

include(
    "base.py",
    "apps.py",
    "middleware.py",
    "database.py",
    "templates.py",
    "locale.py",
    "login.py",
    "logging.py",
    "staticfiles.py",
    "redis.py",
    "rest.py",
    "csp.py",
    "dafo.py",
    "eboks.py",
    "metrics.py",
    "tenq.py",
)
