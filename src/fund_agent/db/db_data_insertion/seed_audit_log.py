import json

from seed_helper import uid
from fund_agent.models.audit_log import AuditLog
from fund_agent.models.capital_call import CapitalCall
from fund_agent.models.distribution import Distribution


def seed_audit_log(cur, capital_calls: list[CapitalCall], distributions: list[Distribution]) -> list[AuditLog]:
    entries = []

    # Each capital call gets an agent "create" entry and a CFO "approve" entry.
    for call in capital_calls:
        entries.append(_audit_builder(
            actor="agent",
            action="create",
            entity_type="capital_call",
            entity_id=call.id,
            before=None,
            after={"status": "draft", "total_amount": float(call.total_amount), "purpose": call.purpose},
            at=f"{call.call_date}T09:05:00+00:00",
        ))
        entries.append(_audit_builder(
            actor="CFO",
            action="approve",
            entity_type="capital_call",
            entity_id=call.id,
            before={"status": "proposed"},
            after={"status": "approved"},
            at=f"{call.call_date}T11:00:00+00:00",
        ))

    # Same two-step trail for each distribution.
    for dist in distributions:
        entries.append(_audit_builder(
            actor="agent",
            action="create",
            entity_type="distribution",
            entity_id=dist.id,
            before=None,
            after={"status": "draft", "total_amount": float(dist.total_amount), "type": dist.type},
            at=f"{dist.distribution_date}T09:05:00+00:00",
        ))
        entries.append(_audit_builder(
            actor="CFO",
            action="approve",
            entity_type="distribution",
            entity_id=dist.id,
            before={"status": "proposed"},
            after={"status": "approved"},
            at=f"{dist.distribution_date}T11:00:00+00:00",
        ))

    _insert_audit_log(cur, entries)
    return entries


def _audit_builder(
    actor: str,
    action: str,
    entity_type: str,
    entity_id: str,
    before,
    after,
    at: str,
) -> AuditLog:
    return AuditLog(
        id=uid(),
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before=before,
        after=after,
        at=at,
    )


def _insert_audit_log(cur, entries: list[AuditLog]) -> None:
    cur.executemany(
        """
        INSERT INTO audit_log
            (id, actor, action, entity_type, entity_id,
             before, after, at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        [
            (
                e.id, e.actor, e.action, e.entity_type, e.entity_id,
                json.dumps(e.before), json.dumps(e.after), e.at,
            )
            for e in entries
        ],
    )
