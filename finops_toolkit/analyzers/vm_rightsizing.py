"""
Virtual Machine Rightsizing Analyzer.
Evaluates CPU and Memory utilization against threshold metrics and computes cost savings.
"""

from typing import List, Dict
from ..core.models import VMMetrics, RightsizingRecommendation
from ..core.config import FinOpsConfig, default_config


class VMRightsizingAnalyzer:
    """Analyzes VM compute telemetry and recommends optimal SKU sizing."""

    # Reference catalog of Azure VM sizes and approx monthly on-demand costs (USD)
    VM_CATALOG: Dict[str, float] = {
        "Standard_D8s_v5": 384.0,
        "Standard_D4s_v5": 192.0,
        "Standard_D2s_v5": 96.0,
        "Standard_B4ms": 132.0,
        "Standard_B2ms": 66.0,
        "Standard_B2s": 33.0,
    }

    # Downsize mapping matrix
    DOWNSIZE_MAP: Dict[str, str] = {
        "Standard_D8s_v5": "Standard_D4s_v5",
        "Standard_D4s_v5": "Standard_D2s_v5",
        "Standard_D2s_v5": "Standard_B2ms",
        "Standard_B4ms": "Standard_B2ms",
        "Standard_B2ms": "Standard_B2s",
    }

    def __init__(self, config: FinOpsConfig = None):
        self.config = config or default_config

    def evaluate_vm(self, vm: VMMetrics) -> RightsizingRecommendation:
        """Evaluate a single VM against rightsizing policy."""
        # Check if VM is underutilized
        is_cpu_low = vm.cpu_p95 < self.config.underutilized_cpu_threshold_pct
        is_mem_low = vm.memory_max_pct < self.config.idle_memory_threshold_pct

        if is_cpu_low and is_mem_low and vm.current_size in self.DOWNSIZE_MAP:
            target_size = self.DOWNSIZE_MAP[vm.current_size]
            projected_cost = self.VM_CATALOG.get(target_size, vm.monthly_cost * 0.5)
            savings = max(0.0, vm.monthly_cost - projected_cost)
            pct = (savings / vm.monthly_cost) * 100.0 if vm.monthly_cost > 0 else 0.0

            rationale = (
                f"VM CPU p95 is {vm.cpu_p95:.1f}% (<{self.config.underutilized_cpu_threshold_pct}%) "
                f"and Max Memory is {vm.memory_max_pct:.1f}% (<{self.config.idle_memory_threshold_pct}%). "
                f"Recommend downsizing from {vm.current_size} to {target_size}."
            )
        else:
            target_size = vm.current_size
            projected_cost = vm.monthly_cost
            savings = 0.0
            pct = 0.0
            rationale = "VM sizing is optimal based on observed utilization patterns."

        return RightsizingRecommendation(
            vm_name=vm.vm_name,
            current_size=vm.current_size,
            recommended_size=target_size,
            current_monthly_cost=vm.monthly_cost,
            projected_monthly_cost=projected_cost,
            monthly_savings=savings,
            savings_percentage=pct,
            rationale=rationale
        )

    def analyze_fleet(self, vms: List[VMMetrics]) -> List[RightsizingRecommendation]:
        """Analyze a collection of virtual machines."""
        return [self.evaluate_vm(vm) for vm in vms]
