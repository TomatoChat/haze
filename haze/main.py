"""haze — entry point that runs all alignment routes.

Executes every route in sequence so users see all failures at once
rather than one at a time.
"""

import sys

from haze.routes.align_agents import align_agents
from haze.routes.align_docs import align_docs


def main() -> int:
    rc_agents = align_agents()
    rc_docs = align_docs()
    return 1 if (rc_agents or rc_docs) else 0


if __name__ == "__main__":
    sys.exit(main())
