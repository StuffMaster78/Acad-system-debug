from __future__ import annotations

import logging
import os

log = logging.getLogger("config")


class Secrets:
    """
    Layered secrets resolver.

    Resolution order (first non-empty value wins):
        1. Environment variable  — always checked first, fastest path
        2. AWS Secrets Manager   — optional; activated when AWS_SECRETS_MANAGER_PREFIX
                                   is set and boto3 is available
        3. default               — caller-supplied fallback

    AWS Secrets Manager notes:
        - Set AWS_SECRETS_MANAGER_PREFIX to the path prefix for your secrets,
          e.g. "my-app/production/". The secret name is then
          "<prefix><key>" → e.g. "my-app/production/STRIPE_SECRET_KEY".
        - AWS credentials are resolved by boto3 in the standard order
          (env vars → ~/.aws/credentials → EC2/ECS IAM role).
        - Results are cached in memory after the first retrieval to avoid
          repeated API calls during a single process lifetime.

    Usage:
        from writing_system.settings.secrets import secrets
        value = secrets.get("STRIPE_SECRET_KEY")
        value = secrets.get("DATABASE_PASSWORD", default="fallback")
    """

    def __init__(self):
        self._cache: dict[str, str] = {}
        self._prefix: str = os.getenv("AWS_SECRETS_MANAGER_PREFIX", "")
        self._use_aws: bool = bool(self._prefix)

    def get(self, key: str, default=None):
        # 1. Environment variable
        value = os.getenv(key)
        if value:
            return value

        # 2. AWS Secrets Manager (only when prefix is configured)
        if self._use_aws:
            aws_value = self._get_from_aws(key)
            if aws_value is not None:
                return aws_value

        return default

    def _get_from_aws(self, key: str) -> str | None:
        """
        Retrieve a secret from AWS Secrets Manager.

        Returns None on any error so the caller falls through to default.
        Results are cached in-process to minimise API calls.
        """
        cache_key = f"{self._prefix}{key}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            import boto3
            from botocore.exceptions import ClientError

            client = boto3.client(
                "secretsmanager",
                region_name=os.getenv("AWS_SECRETS_MANAGER_REGION", os.getenv("AWS_S3_REGION_NAME", "us-east-1")),
            )
            response = client.get_secret_value(SecretId=cache_key)
            secret_value = response.get("SecretString") or ""

            if secret_value:
                self._cache[cache_key] = secret_value
                return secret_value

        except ImportError:
            log.debug("boto3 not available — AWS Secrets Manager disabled.")
            self._use_aws = False
        except Exception as exc:
            log.debug("AWS Secrets Manager lookup failed for %s: %s", key, exc)

        return None

    def require(self, key: str) -> str:
        """
        Return a secret or raise ImproperlyConfigured if not found.

        Use for secrets that must exist for the app to function correctly.
        """
        value = self.get(key)
        if not value:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured(
                f"Required secret '{key}' is not set in environment "
                f"or AWS Secrets Manager (prefix: '{self._prefix}')."
            )
        return value


secrets = Secrets()
