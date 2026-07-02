import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from db_connection import get_db_connection
from teardown import teardown
from seed_fund import seed_fund
from seed_investors import seed_investors
from seed_closings import seed_closings
from seed_chart_of_accounts import seed_chart_of_accounts
from seed_commitments import seed_commitments
from seed_agent_runs import seed_agent_runs
from seed_investments import seed_investments
from seed_capital_calls import seed_capital_calls
from seed_call_allocations import seed_call_allocations
from seed_distributions import seed_distributions
from seed_distribution_allocations import seed_distribution_allocations
from seed_agent_decisions import seed_agent_decisions
from seed_document_templates import seed_document_templates
from seed_approvals import seed_approvals
from seed_generated_documents import seed_generated_documents
from seed_audit_log import seed_audit_log

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--reset", action="store_true")
args = parser.parse_args()

if __name__ == '__main__':
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if args.reset:
                logger.info("Tearing down existing data...")
                teardown(cur)
                logger.info("Teardown complete.")

            logger.info("Seeding fund...")
            fund = seed_fund(cur=cur)

            logger.info("Seeding investors...")
            investors = seed_investors(cur=cur)

            logger.info("Seeding closings...")
            closings = seed_closings(cur=cur, fund_id=fund.id)

            logger.info("Seeding chart of accounts...")
            chart_of_accounts = seed_chart_of_accounts(cur=cur)

            logger.info("Seeding commitments...")
            commitments = seed_commitments(cur=cur, fund_id=fund.id, investors=investors, closings=closings)

            logger.info("Seeding agent runs...")
            agent_runs = seed_agent_runs(cur=cur)

            logger.info("Seeding investments...")
            investments = seed_investments(cur=cur, fund_id=fund.id)

            logger.info("Seeding capital calls...")
            capital_calls = seed_capital_calls(cur=cur, fund_id=fund.id, agent_runs=agent_runs)

            logger.info("Seeding call allocations...")
            call_allocations = seed_call_allocations(cur=cur, capital_calls=capital_calls, investors=investors, commitments=commitments)

            logger.info("Seeding distributions...")
            distributions = seed_distributions(cur=cur, fund_id=fund.id, agent_runs=agent_runs)

            logger.info("Seeding distribution allocations...")
            distribution_allocations = seed_distribution_allocations(cur=cur, distributions=distributions, investors=investors, commitments=commitments)

            logger.info("Seeding agent decisions...")
            agent_decisions = seed_agent_decisions(cur=cur, agent_runs=agent_runs, capital_calls=capital_calls, distributions=distributions)

            logger.info("Seeding document templates...")
            templates = seed_document_templates(cur=cur)

            logger.info("Seeding approvals...")
            approvals = seed_approvals(cur=cur, capital_calls=capital_calls, distributions=distributions)

            logger.info("Seeding generated documents...")
            generated_documents = seed_generated_documents(cur=cur, templates=templates, capital_calls=capital_calls, distributions=distributions, investors=investors)

            logger.info("Seeding audit log...")
            audit_log = seed_audit_log(cur=cur, capital_calls=capital_calls, distributions=distributions)

            conn.commit()
            logger.info("Seed complete.")
