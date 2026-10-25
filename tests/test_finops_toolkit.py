"""
Unit tests for Cloud FinOps Toolkit.
"""

import unittest
from finops_toolkit.core.models import VMMetrics, WasteType
from finops_toolkit.analyzers.vm_rightsizing import VMRightsizingAnalyzer
from finops_toolkit.analyzers.waste_detector import CloudWasteDetector
from finops_toolkit.automation.scheduler import NonProdScheduler
from finops_toolkit.automation.tag_enforcer import TagGovernanceEngine


class TestFinOpsToolkit(unittest.TestCase):

    def test_vm_rightsizing_underutilized(self):
        analyzer = VMRightsizingAnalyzer()
        vm = VMMetrics(
            vm_name="vm-dev-idle",
            resource_group="rg-dev",
            current_size="Standard_D4s_v5",
            cpu_p95=12.0,
            memory_max_pct=15.0,
            monthly_cost=192.0
        )
        rec = analyzer.evaluate_vm(vm)
        self.assertEqual(rec.recommended_size, "Standard_D2s_v5")
        self.assertGreater(rec.monthly_savings, 0)
        self.assertEqual(rec.monthly_savings, 96.0)

    def test_vm_rightsizing_optimal(self):
        analyzer = VMRightsizingAnalyzer()
        vm = VMMetrics(
            vm_name="vm-prod-heavy",
            resource_group="rg-prod",
            current_size="Standard_D8s_v5",
            cpu_p95=75.0,
            memory_max_pct=80.0,
            monthly_cost=384.0
        )
        rec = analyzer.evaluate_vm(vm)
        self.assertEqual(rec.recommended_size, "Standard_D8s_v5")
        self.assertEqual(rec.monthly_savings, 0.0)

    def test_cloud_waste_detector(self):
        detector = CloudWasteDetector()
        inventory = [
            {"name": "disk-orphaned", "type": "disk", "attached_to": None, "days_idle": 30, "monthly_cost": 50.0},
            {"name": "pip-unused", "type": "public_ip", "associated_nic": None, "days_idle": 10, "monthly_cost": 7.0},
            {"name": "disk-attached", "type": "disk", "attached_to": "vm-active", "days_idle": 0, "monthly_cost": 100.0},
        ]
        waste = detector.detect_waste(inventory)
        self.assertEqual(len(waste), 2)
        self.assertEqual(waste[0].resource_type, WasteType.UNATTACHED_DISK)
        self.assertEqual(waste[1].resource_type, WasteType.UNASSOCIATED_IP)

    def test_non_prod_scheduler_savings(self):
        scheduler = NonProdScheduler()
        # 55 hours / 168 hours = 32.74% active, ~67.26% savings
        res = scheduler.calculate_schedule_savings("vm-dev", "vm", 100.0)
        self.assertAlmostEqual(res.savings_percentage, 67.26, delta=0.5)
        self.assertAlmostEqual(res.monthly_savings, 67.26, delta=0.5)

    def test_tag_governance_engine(self):
        engine = TagGovernanceEngine()
        compliant = engine.evaluate_resource_tags("res-1", "vm", {
            "Environment": "Production",
            "CostCenter": "CC-104",
            "Owner": "Shyam",
            "Project": "FinOps"
        })
        self.assertEqual(compliant.compliance_status, "compliant")
        self.assertEqual(len(compliant.missing_tags), 0)

        non_compliant = engine.evaluate_resource_tags("res-2", "vm", {
            "Environment": "Dev"
        })
        self.assertEqual(non_compliant.compliance_status, "non_compliant")
        self.assertIn("CostCenter", non_compliant.missing_tags)


if __name__ == "__main__":
    unittest.main()
