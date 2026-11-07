from unittest import TestCase

from config.sentry import sentry_options


class SentryOptionsTests(TestCase):
    def test_no_dsn_keeps_sentry_off(self):
        self.assertIsNone(sentry_options({}, environ={}))

    def test_empty_dsn_keeps_sentry_off(self):
        self.assertIsNone(sentry_options({"SENTRY_DSN": ""}, environ={}))

    def test_dsn_from_secrets(self):
        options = sentry_options({"SENTRY_DSN": "https://key@o1.ingest.sentry.io/1"}, environ={})
        self.assertEqual(options["dsn"], "https://key@o1.ingest.sentry.io/1")
        self.assertEqual(options["environment"], "production")
        self.assertEqual(options["traces_sample_rate"], 0.0)
        self.assertFalse(options["send_default_pii"])

    def test_env_var_is_fallback(self):
        options = sentry_options({}, environ={"SENTRY_DSN": "https://env@o1.ingest.sentry.io/1"})
        self.assertEqual(options["dsn"], "https://env@o1.ingest.sentry.io/1")

    def test_secrets_win_over_env(self):
        options = sentry_options(
            {"SENTRY_DSN": "https://secret@o1.ingest.sentry.io/1"},
            environ={"SENTRY_DSN": "https://env@o1.ingest.sentry.io/1"},
        )
        self.assertEqual(options["dsn"], "https://secret@o1.ingest.sentry.io/1")

    def test_optional_settings(self):
        options = sentry_options(
            {
                "SENTRY_DSN": "https://key@o1.ingest.sentry.io/1",
                "SENTRY_ENVIRONMENT": "staging",
                "SENTRY_TRACES_SAMPLE_RATE": 0.1,
            },
            environ={},
        )
        self.assertEqual(options["environment"], "staging")
        self.assertEqual(options["traces_sample_rate"], 0.1)
