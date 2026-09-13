"""Retry and backoff helpers.

What an agent-written module looks like before commentwall sees it: a handful
of very long standalone runs that restate the code below them. This is the
violation-heavy path, where every wall is collected and returned.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, Iterator, TypeVar

T = TypeVar("T")

# Configuration constants for the retry subsystem.
#
# BASE_DELAY is the delay applied after the first failed attempt. It is
# deliberately small because the overwhelming majority of transient failures
# in this system resolve within a few tens of milliseconds, and a larger
# starting point would add latency to the common case for no benefit.
#
# MAX_DELAY caps the exponential growth. Without a cap, the fifth or sixth
# attempt would sleep for longer than the upstream request timeout, which
# means the retry would be cancelled before it ever fired and the caller
# would see a timeout instead of the underlying error.
#
# MAX_ATTEMPTS is the total number of attempts including the first one. It is
# not the number of retries. This distinction has caused confusion in review
# more than once, hence this note.
#
# JITTER_RATIO is the fraction of the computed delay that is randomised. Full
# jitter was measured to be worse than partial jitter for our traffic shape,
# because full jitter can collapse the effective backoff to nearly zero and
# re-synchronise the thundering herd it is supposed to break up.
BASE_DELAY = 0.05
MAX_DELAY = 2.0
MAX_ATTEMPTS = 5
JITTER_RATIO = 0.25


@dataclass(frozen=True)
class Attempt:
    number: int
    delay: float
    error: BaseException | None


def delays(
    base: float = BASE_DELAY,
    cap: float = MAX_DELAY,
    attempts: int = MAX_ATTEMPTS,
    jitter: float = JITTER_RATIO,
) -> Iterator[float]:
    # Generate the backoff schedule.
    #
    # The schedule is exponential with a multiplier of two, clamped at `cap`,
    # with partial jitter applied afterwards. Applying jitter after the clamp
    # rather than before keeps the maximum sleep bounded by `cap`, which is
    # what callers assume when they size their overall deadline.
    #
    # The first yielded value is the delay before the second attempt. There is
    # no delay before the first attempt, so the generator yields exactly
    # `attempts - 1` values.
    #
    # Note that this is a generator rather than a list. Callers that abandon
    # the loop early, which is the normal case because most calls succeed on
    # the first or second attempt, never pay for the unused entries.
    #
    # The random source is the module-level `random`, not `secrets`. Backoff
    # jitter is not a security boundary and `secrets` is measurably slower
    # here.
    for number in range(1, attempts):
        raw = min(base * (2 ** (number - 1)), cap)
        yield raw * (1 - jitter * random.random())


def retry(
    operation: Callable[[], T],
    *,
    retryable: Callable[[BaseException], bool] = lambda _: True,
    attempts: int = MAX_ATTEMPTS,
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    # Run `operation`, retrying transient failures.
    #
    # The `retryable` predicate decides whether a given exception is worth
    # another attempt. The default retries everything, which is correct for
    # the idempotent read paths this helper was written for and wrong for
    # anything that mutates state. Callers that mutate must pass a predicate.
    #
    # `sleep` is injected so tests can run the full schedule without actually
    # sleeping. Do not replace this with a module-level patch point: two test
    # modules already collided on one and the resulting failures only showed
    # up under `-p no:randomly`.
    #
    # On exhaustion the last exception is re-raised with its original
    # traceback rather than wrapped, because wrapping breaks the exception
    # filters that the callers upstream of this module already have in place.
    last: BaseException | None = None
    schedule = delays(attempts=attempts)
    for number in range(1, attempts + 1):
        try:
            return operation()
        except BaseException as error:  # noqa: BLE001 - re-raised below
            if not retryable(error):
                raise
            last = error
            if number == attempts:
                break
            sleep(next(schedule))
    assert last is not None
    raise last


def trace(
    operation: Callable[[], T],
    *,
    retryable: Callable[[BaseException], bool] = lambda _: True,
    attempts: int = MAX_ATTEMPTS,
    sleep: Callable[[float], None] = time.sleep,
) -> tuple[T | None, list[Attempt]]:
    # Same control flow as `retry`, but records every attempt.
    #
    # This exists because the metrics pipeline needs per-attempt delays and
    # error types, and threading a callback through `retry` made the common
    # path slower for the sake of a diagnostic one. Duplicating the loop is
    # the cheaper trade.
    #
    # The returned value is `None` when every attempt failed. The attempt list
    # is always populated and is always `attempts` long in that case, so a
    # caller can tell exhaustion from success without inspecting the value.
    #
    # If you change the control flow in `retry`, change it here too. There is
    # a test that runs both against the same fault-injection sequence and
    # asserts the outcomes agree.
    history: list[Attempt] = []
    schedule = delays(attempts=attempts)
    for number in range(1, attempts + 1):
        try:
            value = operation()
        except BaseException as error:  # noqa: BLE001 - recorded below
            delay = 0.0 if number == attempts else next(schedule)
            history.append(Attempt(number, delay, error))
            if not retryable(error) or number == attempts:
                return None, history
            sleep(delay)
        else:
            history.append(Attempt(number, 0.0, None))
            return value, history
    return None, history


class Budget:
    """A shared retry budget across many operations."""

    # Why a budget at all.
    #
    # Per-call retry limits bound the latency of a single call but say nothing
    # about aggregate load. When a dependency degrades, every in-flight call
    # independently decides to retry, and the retry traffic alone can be
    # enough to keep the dependency down. A shared budget makes retries a
    # scarce resource: the first few calls to notice the degradation get to
    # retry, the rest fail fast.
    #
    # The ratio is retries per successful request, not per request. Tying it
    # to successes means the budget shrinks as the dependency gets worse,
    # which is the behaviour we want.
    #
    # This is not thread-safe. Every consumer so far is single-threaded per
    # event loop, and adding a lock measurably regressed the hot path.

    def __init__(self, ratio: float = 0.1, minimum: int = 10) -> None:
        self.ratio = ratio
        self.minimum = minimum
        self._successes = 0
        self._retries = 0

    def record_success(self) -> None:
        self._successes += 1

    def withdraw(self) -> bool:
        allowance = self.minimum + int(self._successes * self.ratio)
        if self._retries >= allowance:
            return False
        self._retries += 1
        return True


def with_budget(
    operation: Callable[[], T],
    budget: Budget,
    *,
    attempts: int = MAX_ATTEMPTS,
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    # Wire `retry` to a `Budget`.
    #
    # The predicate consults the budget, so an exhausted budget turns the
    # operation into a single attempt. Recording the success here rather than
    # inside `retry` keeps `retry` free of budget knowledge.
    #
    # Note the ordering: the budget is only credited on success, and it is
    # credited once per call, not once per attempt. Crediting per attempt
    # would let a flapping dependency refill its own retry budget.
    value = retry(
        operation,
        retryable=lambda _: budget.withdraw(),
        attempts=attempts,
        sleep=sleep,
    )
    budget.record_success()
    return value
