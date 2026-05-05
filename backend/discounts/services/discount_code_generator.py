from __future__ import annotations

import re
import secrets


class DiscountCodeGenerator:
    """
    Generate safe, readable, normalized discount codes.

    This generator avoids ambiguous characters and supports campaign-style
    prefixes such as BLACKFRIDAY, HOLIDAY, LOYALTY, or GOLD.
    """

    ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    DEFAULT_LENGTH = 8
    MAX_CODE_LENGTH = 64
    MAX_ATTEMPTS = 20

    @classmethod
    def generate(
        cls,
        *,
        prefix: str = "",
        length: int = DEFAULT_LENGTH,
    ) -> str:
        """
        Generate a readable discount code.

        This method does not check database uniqueness. Use
        generate_unique when creating persisted discounts.
        """
        cls._validate_length(length=length)

        token = "".join(
            secrets.choice(cls.ALPHABET)
            for _ in range(length)
        )
        clean_prefix = cls.normalize(prefix)

        if clean_prefix:
            code = f"{clean_prefix}-{token}"
        else:
            code = token

        cls._validate_code_length(code=code)

        return code

    @classmethod
    def generate_unique(
        cls,
        *,
        website,
        prefix: str = "",
        length: int = DEFAULT_LENGTH,
    ) -> str:
        """
        Generate a tenant-unique discount code.
        """
        from discounts.models.discount import Discount

        for _ in range(cls.MAX_ATTEMPTS):
            code = cls.generate(
                prefix=prefix,
                length=length,
            )

            exists = Discount.objects.filter(
                website=website,
                discount_code=code,
            ).exists()

            if not exists:
                return code

        raise ValueError(
            "Could not generate a unique discount code."
        )

    @classmethod
    def normalize(cls, code: str | None) -> str:
        """
        Normalize discount codes for storage and lookup.

        Rules:
            - Strip outer whitespace.
            - Uppercase.
            - Convert spaces and underscores to hyphens.
            - Remove unsafe characters.
            - Collapse repeated hyphens.
        """
        if not code:
            return ""

        cleaned = code.strip().upper()
        cleaned = cleaned.replace("_", "-")
        cleaned = re.sub(r"\s+", "-", cleaned)
        cleaned = re.sub(r"[^A-Z0-9-]", "", cleaned)
        cleaned = re.sub(r"-+", "-", cleaned)
        cleaned = cleaned.strip("-")

        cls._validate_code_length(code=cleaned)

        return cleaned

    @classmethod
    def _validate_length(cls, *, length: int) -> None:
        """
        Validate generated token length.
        """
        if length <= 0:
            raise ValueError(
                "Code length must be greater than zero."
            )

        if length > cls.MAX_CODE_LENGTH:
            raise ValueError(
                "Code length cannot exceed maximum code length."
            )

    @classmethod
    def _validate_code_length(cls, *, code: str) -> None:
        """
        Validate final discount code length.
        """
        if len(code) > cls.MAX_CODE_LENGTH:
            raise ValueError(
                "Discount code cannot exceed 64 characters."
            )