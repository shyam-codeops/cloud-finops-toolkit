"""
Non-Production Resource Scheduler.
Calculates savings and generates start/stop schedules for dev/stage environments.
"""

from typing import List, Dict, Any
from ..core.models import ScheduleSavings
from ..core.config import FinOpsConfig, default_config


class NonProdScheduler:
    """Simulates and manages off-hours shutdown schedules for non-production environments."""

    def __init__(self, config: FinOpsConfig = None):
        self.config = config or default_config

    def calculate_schedule_savings(self, resource_name: str, resource_type: str, full_monthly_cost: float) -> ScheduleSavings:
        """
        Calculates savings from running resources only during business hours
        (e.g., Monday-Friday 08:00 - 19:00 = 55 hrs/wk vs 168 hrs/wk 24/7).
        """
        active_ratio = self.config.scheduled_hours_per_week / self.config.standard_hours_per_week
        scheduled_monthly_cost = full_monthly_cost * active_ratio
        monthly_savings = full_monthly_cost - scheduled_monthly_cost
        pct = (monthly_savings / full_monthly_cost) * 100.0 if full_monthly_cost > 0 else 0.0

        return ScheduleSavings(
            resource_name=resource_name,
            resource_type=resource_type,
            running_hours_per_week=self.config.scheduled_hours_per_week,
            current_cost=full_monthly_cost,
            scheduled_cost=scheduled_monthly_cost,
            monthly_savings=monthly_savings,
            savings_percentage=pct
        )

    def evaluate_environment(self, non_prod_resources: List[Dict[str, Any]]) -> List[ScheduleSavings]:
        results = []
        for res in non_prod_resources:
            cost = float(res.get("monthly_cost", 0.0))
            name = res.get("name", "dev-vm")
            r_type = res.get("type", "virtual_machine")
            results.append(self.calculate_schedule_savings(name, r_type, cost))
        return results
