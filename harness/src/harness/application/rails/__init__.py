"""Lifecycle rails for the bash-script agent.

Importing this package configures openJiuwen logging before the SDK rail
modules are loaded, so the read-only container root is never used for logs.
"""

from harness.application.ojw import configure_logging

configure_logging()

from harness.application.rails.answer import AnswerRail  # noqa: E402
from harness.application.rails.budget import BudgetRail  # noqa: E402
from harness.application.rails.failure import FailureRail  # noqa: E402
from harness.application.rails.features import FeatureRail  # noqa: E402
from harness.application.rails.followup import FollowUpRail  # noqa: E402

__all__ = [
    "AnswerRail",
    "BudgetRail",
    "FailureRail",
    "FeatureRail",
    "FollowUpRail",
]
