"""
Cost Allocation Tag Governance and Enforcement.
"""

from typing import List, Dict, Any
from ..core.models import TagComplianceItem
from ..core.config import FinOpsConfig, default_config


class TagGovernanceEngine:
    """Enforces enterprise cost-allocation tag policies for FinOps accountability."""

    def __init__(self, config: FinOpsConfig = None):
        self.config = config or default_config

    def evaluate_resource_tags(self, resource_name: str, resource_type: str, tags: Dict[str, str]) -> TagComplianceItem:
        """Checks if all mandatory tags are present and non-empty."""
        tags = tags or {}
        missing = []
        for req in self.config.mandatory_tags:
            val = tags.get(req)
            if not val or not str(val).strip():
                missing.append(req)

        status = "compliant" if not missing else "non_compliant"
        return TagComplianceItem(
            resource_name=resource_name,
            resource_type=resource_type,
            missing_tags=missing,
            compliance_status=status
        )

    def audit_inventory(self, inventory: List[Dict[str, Any]]) -> List[TagComplianceItem]:
        items = []
        for res in inventory:
            name = res.get("name", "unknown")
            r_type = res.get("type", "resource")
            tags = res.get("tags", {})
            items.append(self.evaluate_resource_tags(name, r_type, tags))
        return items
