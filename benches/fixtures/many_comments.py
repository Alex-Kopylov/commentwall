"""Rule engine for request shaping.

Comment-dense but compliant: dozens of short standalone runs, none longer
than the default limit of five. Every run has to be opened, extended and
closed, so this measures run bookkeeping without any violation allocation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Iterable, Iterator, Mapping, Sequence

# Rule ids are stable across releases; downstream dashboards key on them.
# Renaming one is a breaking change.
RULE_ID = re.compile(r"^[a-z][a-z0-9_]{2,31}$")

# Anything above this many rules in one ruleset usually means the ruleset
# should have been split by route prefix instead.
MAX_RULES = 256

# Priority ties are broken by insertion order, so the loader must preserve it.
DEFAULT_PRIORITY = 100


@dataclass(frozen=True)
class Rule:
    """A single match/action pair."""

    id: str
    match: Callable[[Mapping[str, str]], bool]
    action: str
    priority: int = DEFAULT_PRIORITY
    tags: frozenset[str] = field(default_factory=frozenset)


@dataclass
class Ruleset:
    rules: list[Rule] = field(default_factory=list)
    # Compiled lookup, rebuilt lazily whenever `rules` changes.
    _by_tag: dict[str, list[Rule]] | None = None

    def add(self, rule: Rule) -> None:
        # Validate before mutating so a rejected rule leaves no partial state.
        if not RULE_ID.match(rule.id):
            raise ValueError(f"bad rule id: {rule.id!r}")
        if len(self.rules) >= MAX_RULES:
            raise ValueError(f"ruleset exceeds {MAX_RULES} rules")
        self.rules.append(rule)
        self._by_tag = None  # invalidate

    def by_tag(self, tag: str) -> Sequence[Rule]:
        # Built on demand: most rulesets are queried by tag zero or one times.
        if self._by_tag is None:
            index: dict[str, list[Rule]] = {}
            for rule in self.rules:
                for name in rule.tags:
                    index.setdefault(name, []).append(rule)
            self._by_tag = index
        return self._by_tag.get(tag, ())

    def ordered(self) -> list[Rule]:
        # Stable sort keeps insertion order inside a priority band.
        return sorted(self.rules, key=lambda rule: rule.priority)


def _header(name: str, expected: str) -> Callable[[Mapping[str, str]], bool]:
    # Header names arrive lowercased from the proxy; do not re-normalize here
    # or the comparison silently starts allocating on every request.
    def predicate(headers: Mapping[str, str]) -> bool:
        return headers.get(name) == expected

    return predicate


def _prefix(name: str, prefix: str) -> Callable[[Mapping[str, str]], bool]:
    # Prefix rules are the common case for path routing.
    def predicate(headers: Mapping[str, str]) -> bool:
        return headers.get(name, "").startswith(prefix)

    return predicate


def _absent(name: str) -> Callable[[Mapping[str, str]], bool]:
    # Distinguishes a missing header from an empty one; the proxy sends both.
    def predicate(headers: Mapping[str, str]) -> bool:
        return name not in headers

    return predicate


def _any_of(*predicates: Callable[[Mapping[str, str]], bool]):
    # Short-circuits, so order the cheap predicates first at the call site.
    def predicate(headers: Mapping[str, str]) -> bool:
        return any(inner(headers) for inner in predicates)

    return predicate


def _all_of(*predicates: Callable[[Mapping[str, str]], bool]):
    def predicate(headers: Mapping[str, str]) -> bool:
        return all(inner(headers) for inner in predicates)

    return predicate


# --- shipped rules ---------------------------------------------------------

# Health checks bypass everything. Kept first so the ordering is obvious to
# anyone reading the file top to bottom.
HEALTH = Rule(
    id="health_bypass",
    match=_prefix(":path", "/healthz"),
    action="allow",
    priority=0,
    tags=frozenset({"infra"}),
)

# Internal traffic is identified by a header the edge strips from the public
# listener, so it cannot be spoofed from outside.
INTERNAL = Rule(
    id="internal_allow",
    match=_header("x-internal", "1"),
    action="allow",
    priority=10,
    tags=frozenset({"infra", "trust"}),
)

# Unauthenticated writes are the single largest source of abuse reports.
ANON_WRITE = Rule(
    id="anon_write_deny",
    match=_all_of(_absent("authorization"), _prefix(":method", "POST")),
    action="deny",
    priority=20,
    tags=frozenset({"abuse"}),
)

# Legacy clients still send the v1 accept header. Shape them down rather than
# rejecting; the deprecation window closes next quarter.
LEGACY = Rule(
    id="legacy_shape",
    match=_header("accept", "application/vnd.api.v1+json"),
    action="shape:slow",
    priority=30,
    tags=frozenset({"deprecation"}),
)

# Two separate scrapers, same treatment.
SCRAPERS = Rule(
    id="scraper_shape",
    match=_any_of(_header("user-agent", "kite/1"), _header("user-agent", "kite/2")),
    action="shape:slow",
    priority=40,
    tags=frozenset({"abuse"}),
)

# Everything else falls through to the default action.
FALLTHROUGH = Rule(
    id="default_allow",
    match=lambda headers: True,
    action="allow",
    priority=1000,
)


def default_ruleset() -> Ruleset:
    ruleset = Ruleset()
    for rule in (HEALTH, INTERNAL, ANON_WRITE, LEGACY, SCRAPERS, FALLTHROUGH):
        ruleset.add(rule)
    return ruleset


def evaluate(ruleset: Ruleset, headers: Mapping[str, str]) -> str:
    # First match wins; `ordered` guarantees priority order.
    for rule in ruleset.ordered():
        if rule.match(headers):
            return rule.action
    # Unreachable while FALLTHROUGH is installed, but a caller can build a
    # ruleset without it.
    return "deny"


def explain(ruleset: Ruleset, headers: Mapping[str, str]) -> Iterator[tuple[str, bool]]:
    # Used by the debug endpoint; evaluates every rule, not just up to the
    # first match.
    for rule in ruleset.ordered():
        yield rule.id, rule.match(headers)


def partition(rules: Iterable[Rule]) -> tuple[list[Rule], list[Rule]]:
    # Splits terminal actions from shaping actions.
    terminal: list[Rule] = []
    shaping: list[Rule] = []
    for rule in rules:
        # `shape:` is a prefix rather than a set so new shaping modes need no
        # change here.
        if rule.action.startswith("shape:"):
            shaping.append(rule)
        else:
            terminal.append(rule)
    return terminal, shaping


def merge(base: Ruleset, overlay: Ruleset) -> Ruleset:
    # Overlay wins on id collisions. Priority is taken from the overlay too,
    # which is what tenant-specific overrides expect.
    merged = Ruleset()
    overridden = {rule.id for rule in overlay.rules}
    for rule in base.rules:
        if rule.id not in overridden:
            merged.add(rule)
    for rule in overlay.rules:
        merged.add(rule)
    return merged


def validate(ruleset: Ruleset) -> list[str]:
    # Returns problems rather than raising: the loader reports all of them at
    # once instead of one per restart.
    problems: list[str] = []
    seen: set[str] = set()
    for rule in ruleset.rules:
        if rule.id in seen:
            problems.append(f"duplicate id: {rule.id}")
        seen.add(rule.id)
        if rule.priority < 0:
            problems.append(f"negative priority: {rule.id}")
    # A ruleset with no terminal rule can fall off the end of `evaluate`.
    if not any(not rule.action.startswith("shape:") for rule in ruleset.rules):
        problems.append("no terminal rule")
    return problems
