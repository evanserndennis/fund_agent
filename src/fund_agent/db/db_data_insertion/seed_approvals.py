from seed_helper import uid


CALL_COMMENT = "Reviewed and approved per investment committee authorization."
DIST_COMMENT = "Distribution approved following waterfall calculation review."


def seed_approvals(cur, capital_calls, distributions) -> list[dict]:
    approvals = []

    for call in capital_calls:
        approvals.append(_approval_builder(
            entity_type="capital_call",
            entity_id=call["id"],
            comments=CALL_COMMENT,
            decided_at=f"{call['call_date']}T08:00:00+00:00",
        ))

    for dist in distributions:
        approvals.append(_approval_builder(
            entity_type="distribution",
            entity_id=dist["id"],
            comments=DIST_COMMENT,
            decided_at=f"{dist['distribution_date']}T08:00:00+00:00",
        ))

    _insert_approvals(cur, approvals)
    return approvals


def _approval_builder(
    entity_type: str,
    entity_id: str,
    comments: str,
    decided_at: str,
) -> dict:
    return {
        "id": uid(),
        "entity_type": entity_type,
        "entity_id": entity_id,
        "approver": "CFO",
        "decision": "approved",
        "comments": comments,
        "decided_at": decided_at,
    }


def _insert_approvals(cur, approvals: list[dict]) -> None:
    cur.executemany(
        """
        INSERT INTO approvals
            (id, entity_type, entity_id, approver,
             decision, comments, decided_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        [
            (
                a["id"], a["entity_type"], a["entity_id"], a["approver"],
                a["decision"], a["comments"], a["decided_at"],
            )
            for a in approvals
        ],
    )
