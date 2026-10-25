"""
Orphaned Resource and Cloud Waste Detector.
"""

from typing import List, Dict, Any
from ..core.models import WasteItem, WasteType
from ..core.config import FinOpsConfig, default_config


class CloudWasteDetector:
    """Scans cloud inventory for idle, orphaned, and unassociated resources."""

    def __init__(self, config: FinOpsConfig = None):
        self.config = config or default_config

    def detect_waste(self, inventory: List[Dict[str, Any]]) -> List[WasteItem]:
        """
        Scans a raw resource inventory list and returns classified waste items.
        """
        waste_items: List[WasteItem] = []

        for res in inventory:
            res_type = res.get("type", "").lower()
            days_idle = res.get("days_idle", 0)
            cost = float(res.get("monthly_cost", 0.0))
            name = res.get("name", "unknown")
            rg = res.get("resource_group", "default-rg")
            res_id = res.get("id", f"/subscriptions/sub-123/{name}")

            # 1. Unattached Disks
            if "disk" in res_type and not res.get("attached_to"):
                if days_idle >= self.config.unattached_disk_idle_days:
                    waste_items.append(WasteItem(
                        resource_id=res_id,
                        resource_name=name,
                        resource_type=WasteType.UNATTACHED_DISK,
                        resource_group=rg,
                        days_idle=days_idle,
                        monthly_cost=cost,
                        recommendation=f"Disk unattached for {days_idle} days. Create snapshot backup and delete disk."
                    ))

            # 2. Unassociated Public IPs
            elif "public_ip" in res_type or "publicipaddress" in res_type:
                if not res.get("associated_nic") and days_idle >= self.config.unassociated_ip_idle_days:
                    waste_items.append(WasteItem(
                        resource_id=res_id,
                        resource_name=name,
                        resource_type=WasteType.UNASSOCIATED_IP,
                        resource_group=rg,
                        days_idle=days_idle,
                        monthly_cost=cost,
                        recommendation=f"Public IP unassociated for {days_idle} days. Release static IP address."
                    ))

            # 3. Aged Snapshots
            elif "snapshot" in res_type and days_idle >= self.config.aged_snapshot_days:
                waste_items.append(WasteItem(
                    resource_id=res_id,
                    resource_name=name,
                    resource_type=WasteType.AGED_SNAPSHOT,
                    resource_group=rg,
                    days_idle=days_idle,
                    monthly_cost=cost,
                    recommendation=f"Snapshot is {days_idle} days old (> retention threshold {self.config.aged_snapshot_days}d). Archive or delete."
                ))

        return waste_items
