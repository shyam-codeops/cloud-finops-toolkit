"""
FinOps domain models using Python dataclasses.
"""

from typing import List, Dict, Optional, Any
from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone


class WasteType(str, Enum):
    UNATTACHED_DISK = "unattached_disk"
    UNASSOCIATED_IP = "unassociated_public_ip"
    AGED_SNAPSHOT = "aged_snapshot"
    IDLE_LB = "idle_load_balancer"


@dataclass
class VMMetrics:
    vm_name: str
    resource_group: str
    current_size: str
    cpu_p95: float
    memory_max_pct: float
    monthly_cost: float


@dataclass
class RightsizingRecommendation:
    vm_name: str
    current_size: str
    recommended_size: str
    current_monthly_cost: float
    projected_monthly_cost: float
    monthly_savings: float
    savings_percentage: float
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WasteItem:
    resource_id: str
    resource_name: str
    resource_type: WasteType
    resource_group: str
    days_idle: int
    monthly_cost: float
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        res = asdict(self)
        res["resource_type"] = self.resource_type.value
        return res


@dataclass
class ScheduleSavings:
    resource_name: str
    resource_type: str
    running_hours_per_week: int
    current_cost: float
    scheduled_cost: float
    monthly_savings: float
    savings_percentage: float


@dataclass
class TagComplianceItem:
    resource_name: str
    resource_type: str
    missing_tags: List[str]
    compliance_status: str  # compliant, non_compliant
