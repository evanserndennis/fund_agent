from seed_helper import uid
from fund_agent.models.generated_document import GeneratedDocument
from fund_agent.models.document_template import DocumentTemplate
from fund_agent.models.capital_call import CapitalCall
from fund_agent.models.distribution import Distribution
from fund_agent.models.investor import Investor


CALL_NOTICE_COUNT = 3  # call notices are only generated for the first 3 capital calls


def seed_generated_documents(
    cur,
    templates: list[DocumentTemplate],
    capital_calls: list[CapitalCall],
    distributions: list[Distribution],
    investors: list[Investor],
) -> list[GeneratedDocument]:
    template_id_by_type = {t.doc_type: t.id for t in templates}
    lps = investors[1:]  # investors[0] is the GP; notices only go to LPs

    docs = []

    # Call notices: first N capital calls, one per LP
    for i, call in enumerate(capital_calls[:CALL_NOTICE_COUNT]):
        for lp in lps:
            docs.append(_document_builder(
                template_id=template_id_by_type["call_notice"],
                doc_type="call_notice",
                investor_id=lp.id,
                file_path=f"/docs/calls/call_{i + 1}_{lp.id[:8]}.pdf",
                generated_at=f"{call.call_date}T10:30:00+00:00",
            ))

    # Distribution notices: every distribution, one per LP
    for i, dist in enumerate(distributions):
        for lp in lps:
            docs.append(_document_builder(
                template_id=template_id_by_type["distribution_notice"],
                doc_type="distribution_notice",
                investor_id=lp.id,
                file_path=f"/docs/distributions/dist_{i + 1}_{lp.id[:8]}.pdf",
                generated_at=f"{dist.distribution_date}T10:30:00+00:00",
            ))

    _insert_documents(cur, docs)
    return docs


def _document_builder(
    template_id: str,
    doc_type: str,
    investor_id: str,
    file_path: str,
    generated_at: str,
) -> GeneratedDocument:
    return GeneratedDocument(
        id=uid(),
        template_id=template_id,
        doc_type=doc_type,
        allocation_id=None,
        investor_id=investor_id,
        file_path=file_path,
        generated_at=generated_at,
        status="sent",
    )


def _insert_documents(cur, docs: list[GeneratedDocument]) -> None:
    cur.executemany(
        """
        INSERT INTO generated_documents
            (id, template_id, doc_type, allocation_id,
             investor_id, file_path, generated_at, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        [
            (
                doc.id, doc.template_id, doc.doc_type, doc.allocation_id,
                doc.investor_id, doc.file_path, doc.generated_at, doc.status,
            )
            for doc in docs
        ],
    )
