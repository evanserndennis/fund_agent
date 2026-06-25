from seed_helper import uid


# (doc_type, version, body)
DOC_TEMPLATE_DEF = [
    (
        "call_notice", 1,
        "Dear {{investor_name}},\n\nYou are hereby notified that Apex Ventures III, L.P. "
        "has issued Capital Call #{{call_number}} in the amount of USD {{amount}}. "
        "Payment is due by {{due_date}}.\n\nRegards,\nApex GP LLC",
    ),
    (
        "distribution_notice", 1,
        "Dear {{investor_name}},\n\nApex Ventures III, L.P. is pleased to inform you of "
        "a distribution in the amount of USD {{amount}} on {{distribution_date}}. "
        "Funds will be wired to your account on file.\n\nRegards,\nApex GP LLC",
    ),
]


def seed_document_templates(cur) -> list[dict]:
    templates = []
    for doc_type, version, body in DOC_TEMPLATE_DEF:
        templates.append(_template_builder(doc_type, version, body))
    _insert_templates(cur, templates)
    return templates


def _template_builder(doc_type: str, version: int, body: str) -> dict:
    return {
        "id": uid(),
        "doc_type": doc_type,
        "version": version,
        "body": body,
    }


def _insert_templates(cur, templates: list[dict]) -> None:
    cur.executemany(
        """
        INSERT INTO document_templates (id, doc_type, version, body)
        VALUES (%s, %s, %s, %s)
        """,
        [
            (t["id"], t["doc_type"], t["version"], t["body"])
            for t in templates
        ],
    )
