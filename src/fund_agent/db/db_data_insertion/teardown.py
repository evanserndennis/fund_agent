
def teardown(cur):
    cur.execute("""
        TRUNCATE TABLE
            audit_log, approvals, agent_decisions,
            generated_documents, document_templates,
            distribution_allocations, distributions,
            call_allocations, capital_calls,
            investments, agent_runs,
            journal_lines, journal_entries,
            chart_of_accounts, commitments,
            closings, investors, funds
        RESTART IDENTITY CASCADE;
    """)
