import importlib
import os
import sys
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

class ProductionSettingsTestCase(SimpleTestCase):
    def test_production_settings_fails_when_postgres_env_missing(self):
        """Verify production settings raises ImproperlyConfigured when PostgreSQL env vars are absent."""
        # Clear any environment variables that might satisfy production
        env_to_clear = [
            'SECRET_KEY', 'ALLOWED_HOSTS', 'POSTGRES_DB',
            'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_HOST'
        ]
        old_env = {k: os.environ.get(k) for k in env_to_clear}
        for k in env_to_clear:
            if k in os.environ:
                del os.environ[k]

        try:
            # Set minimal secret key and allowed hosts to reach the DB check
            os.environ['SECRET_KEY'] = 'test-secret-key-for-prod-test'
            os.environ['ALLOWED_HOSTS'] = 'example.com'

            if 'config.settings.production' in sys.modules:
                del sys.modules['config.settings.production']

            with self.assertRaises(ImproperlyConfigured) as ctx:
                importlib.import_module('config.settings.production')

            self.assertIn("Silent fallback to SQLite in production is strictly prohibited", str(ctx.exception))
        finally:
            # Restore environment
            for k, v in old_env.items():
                if v is not None:
                    os.environ[k] = v
                elif k in os.environ:
                    del os.environ[k]
            if 'config.settings.production' in sys.modules:
                del sys.modules['config.settings.production']

    def test_production_settings_configures_postgresql_when_env_present(self):
        """Verify production settings correctly configures PostgreSQL engine when env vars are present."""
        env_vars = {
            'SECRET_KEY': 'test-secret-key-for-prod-test',
            'ALLOWED_HOSTS': 'example.com',
            'POSTGRES_DB': 'realestate_prod',
            'POSTGRES_USER': 'postgres_user',
            'POSTGRES_PASSWORD': 'postgres_password',
            'POSTGRES_HOST': 'db.example.com',
            'POSTGRES_PORT': '5432',
        }
        old_env = {k: os.environ.get(k) for k in env_vars}
        os.environ.update(env_vars)

        try:
            if 'config.settings.production' in sys.modules:
                del sys.modules['config.settings.production']

            prod_module = importlib.import_module('config.settings.production')
            self.assertEqual(prod_module.DATABASES['default']['ENGINE'], 'django.db.backends.postgresql')
            self.assertEqual(prod_module.DATABASES['default']['NAME'], 'realestate_prod')
            self.assertFalse(prod_module.DEBUG)
        finally:
            for k, v in old_env.items():
                if v is not None:
                    os.environ[k] = v
                elif k in os.environ:
                    del os.environ[k]
            if 'config.settings.production' in sys.modules:
                del sys.modules['config.settings.production']
