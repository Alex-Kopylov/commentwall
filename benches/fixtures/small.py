"""Session token helpers used by the auth middleware."""

from __future__ import annotations

import hmac
import time
from dataclasses import dataclass

TTL_SECONDS = 900
_CLOCK_SKEW = 30  # tolerated drift between issuer and verifier


@dataclass(frozen=True)
class Token:
    subject: str
    issued_at: int
    signature: str


def _payload(subject: str, issued_at: int) -> bytes:
    return f"{subject}:{issued_at}".encode()


def issue(subject: str, secret: bytes, now: int | None = None) -> Token:
    now = int(time.time()) if now is None else now
    digest = hmac.new(secret, _payload(subject, now), "sha256").hexdigest()
    return Token(subject, now, digest)


def verify(token: Token, secret: bytes, now: int | None = None) -> bool:
    now = int(time.time()) if now is None else now
    if now - token.issued_at > TTL_SECONDS + _CLOCK_SKEW:
        return False
    expected = issue(token.subject, secret, token.issued_at)
    return hmac.compare_digest(expected.signature, token.signature)


# Refreshing re-issues rather than extending: the signature covers issued_at,
# so a new timestamp needs a new digest anyway. Three lines, which stays under
# the default limit of five and keeps this fixture clean.
def refresh(token: Token, secret: bytes) -> Token:
    return issue(token.subject, secret)
