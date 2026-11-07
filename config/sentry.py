"""Sentry error reporting (org `skarnik`, project `skarnik_admin`).

Only `config/settings/production.py` calls `init_sentry()`. Development and
testing never report. Production reports only when a DSN is configured, so a
server without one keeps working as before.
"""

import os

DEFAULT_ENVIRONMENT = "production"


def sentry_options(secrets: dict, environ=os.environ) -> dict | None:
    """Build `sentry_sdk.init()` options from secrets.json, falling back to env vars.

    Returns None when no DSN is configured, which means Sentry stays off.
    """

    def value(key: str):
        found = secrets.get(key)
        if found in (None, ""):
            found = environ.get(key)
        return found if found not in (None, "") else None

    dsn = value("SENTRY_DSN")
    if dsn is None:
        return None

    return {
        "dsn": dsn,
        "environment": value("SENTRY_ENVIRONMENT") or DEFAULT_ENVIRONMENT,
        # Errors only by default; set SENTRY_TRACES_SAMPLE_RATE (0.0–1.0) to sample performance traces.
        "traces_sample_rate": float(value("SENTRY_TRACES_SAMPLE_RATE") or 0.0),
        # The admin is used by editors; never send their IPs, cookies or user details.
        "send_default_pii": False,
        # The release defaults to SENTRY_RELEASE or the deployed checkout's `git rev-parse HEAD`.
    }


def init_sentry(secrets: dict) -> bool:
    """Start Sentry if a DSN is configured. Returns whether it was started."""
    options = sentry_options(secrets)
    if options is None:
        return False

    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import ignore_logger

    sentry_sdk.init(integrations=[DjangoIntegration()], **options)
    # Bots hitting the server with foreign Host headers are noise, not bugs.
    ignore_logger("django.security.DisallowedHost")
    return True
