"""
FinOps Configuration & Policy thresholds.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class FinOpsConfig:
    # Utilization thresholds for rightsizing
    idle_cpu_threshold_pct: float = 10.0
    underutilized_cpu_threshold_pct: float = 30.0
    idle_memory_threshold_pct: float = 25.0

    # Waste detection thresholds
    unattached_disk_idle_days: int = 14
    unassociated_ip_idle_days: int = 7
    aged_snapshot_days: int = 60

    # Mandatory cost allocation tags
    mandatory_tags: List[str] = field(default_factory=lambda: [
        "Environment",
        "CostCenter",
        "Owner",
        "Project"
    ])

    # Workweek hours for non-prod scheduler
    # 5 days * 11 hours (8 AM to 7 PM) = 55 hours vs 168 hours full week (67.2% reduction)
    scheduled_hours_per_week: int = 55
    standard_hours_per_week: int = 168


default_config = FinOpsConfig()
