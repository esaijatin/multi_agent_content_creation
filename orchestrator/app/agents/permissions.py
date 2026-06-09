"""Explicit agent permission scopes — enforced in Phase 5."""

from dataclasses import dataclass
from enum import Enum


class Permission(str, Enum):
    INTERNET = "internet"
    SECRETS = "secrets"
    RETRIEVAL = "retrieval"
    WORKFLOW_READ = "workflow_read"
    WORKFLOW_WRITE = "workflow_write"


@dataclass(frozen=True)
class AgentPermissions:
    name: str
    allowed: frozenset[Permission]
    denied: frozenset[Permission]


AGENT_PERMISSIONS: dict[str, AgentPermissions] = {
    "planner": AgentPermissions(
        "planner",
        allowed=frozenset({Permission.WORKFLOW_READ}),
        denied=frozenset({Permission.INTERNET, Permission.SECRETS}),
    ),
    "research": AgentPermissions(
        "research",
        allowed=frozenset({Permission.INTERNET, Permission.RETRIEVAL}),
        denied=frozenset({Permission.SECRETS, Permission.WORKFLOW_WRITE}),
    ),
    "draft_writer": AgentPermissions(
        "draft_writer",
        allowed=frozenset({Permission.RETRIEVAL}),
        denied=frozenset({Permission.INTERNET, Permission.SECRETS}),
    ),
    "fact_checker": AgentPermissions(
        "fact_checker",
        allowed=frozenset({Permission.WORKFLOW_READ}),
        denied=frozenset({Permission.INTERNET, Permission.SECRETS, Permission.WORKFLOW_WRITE}),
    ),
}
