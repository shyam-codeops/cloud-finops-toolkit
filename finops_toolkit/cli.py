"""
Interactive CLI for Cloud FinOps Cost Optimization Toolkit.
"""

import sys
import argparse
from typing import List, Dict, Any
from .core.models import VMMetrics
from .analyzers.vm_rightsizing import VMRightsizingAnalyzer
from .analyzers.waste_detector import CloudWasteDetector
from .automation.scheduler import NonProdScheduler
from .automation.tag_enforcer import TagGovernanceEngine

# Windows UTF-8 stdout configuration
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def print_banner():
    banner = """
===============================================================
   [FINOPS] CLOUD FINOPS COST OPTIMIZATION TOOLKIT
   Rightsizing | Waste Elimination | Off-Hours Scheduling
===============================================================
    """
    print(banner)


def get_sample_vms() -> List[VMMetrics]:
    return [
        VMMetrics("vm-frontend-dev", "rg-dev", "Standard_D4s_v5", cpu_p95=12.4, memory_max_pct=18.5, monthly_cost=192.0),
        VMMetrics("vm-batch-worker", "rg-dev", "Standard_D8s_v5", cpu_p95=8.2, memory_max_pct=22.0, monthly_cost=384.0),
        VMMetrics("vm-db-replica", "rg-prod", "Standard_D8s_v5", cpu_p95=78.5, memory_max_pct=85.0, monthly_cost=384.0),
        VMMetrics("vm-api-stage", "rg-stage", "Standard_B4ms", cpu_p95=14.0, memory_max_pct=19.0, monthly_cost=132.0),
    ]


def get_sample_waste_inventory() -> List[Dict[str, Any]]:
    return [
        {"name": "disk-db-backup-old", "type": "disk", "attached_to": None, "days_idle": 45, "monthly_cost": 65.0, "resource_group": "rg-storage"},
        {"name": "disk-vm-test-unattached", "type": "disk", "attached_to": None, "days_idle": 21, "monthly_cost": 32.0, "resource_group": "rg-dev"},
        {"name": "pip-ingress-old", "type": "public_ip", "associated_nic": None, "days_idle": 18, "monthly_cost": 7.5, "resource_group": "rg-network"},
        {"name": "snap-manual-2025", "type": "snapshot", "days_idle": 120, "monthly_cost": 15.0, "resource_group": "rg-backup"},
        {"name": "disk-prod-active", "type": "disk", "attached_to": "vm-prod", "days_idle": 0, "monthly_cost": 130.0, "resource_group": "rg-prod"},
    ]


def cmd_rightsize(args):
    print("\n[*] Evaluating VM Compute Rightsizing Opportunities...")
    analyzer = VMRightsizingAnalyzer()
    recommendations = analyzer.analyze_fleet(get_sample_vms())

    total_current = sum(r.current_monthly_cost for r in recommendations)
    total_projected = sum(r.projected_monthly_cost for r in recommendations)
    total_savings = sum(r.monthly_savings for r in recommendations)

    print("\n--- [REPORT] VM RIGHTSIZING RECOMMENDATIONS ---")
    for idx, r in enumerate(recommendations, 1):
        if r.monthly_savings > 0:
            print(f"\n[{idx}] VM: {r.vm_name}")
            print(f"    Current: {r.current_size} (${r.current_monthly_cost:.2f}/mo)")
            print(f"    Target : {r.recommended_size} (${r.projected_monthly_cost:.2f}/mo)")
            print(f"    Savings: ${r.monthly_savings:.2f}/mo ({r.savings_percentage:.1f}%)")
            print(f"    Reason : {r.rationale}")

    print("\n" + "=" * 55)
    print(f"Current Compute Spend  : ${total_current:.2f}/mo")
    print(f"Optimized Compute Spend: ${total_projected:.2f}/mo")
    print(f"Monthly Cost Savings   : ${total_savings:.2f}/mo ({(total_savings/total_current)*100:.1f}%)")
    print(f"Annualized Run-Rate    : ${total_savings * 12:.2f}/year")


def cmd_waste(args):
    print("\n[*] Scanning Cloud Inventory for Orphaned & Idle Resources...")
    detector = CloudWasteDetector()
    waste_items = detector.detect_waste(get_sample_waste_inventory())
    total_waste = sum(w.monthly_cost for w in waste_items)

    print("\n--- [REPORT] CLOUD WASTE & ORPHANED RESOURCES ---")
    for idx, w in enumerate(waste_items, 1):
        print(f"\n[{idx}] Resource: {w.resource_name} ({w.resource_type.value})")
        print(f"    Group   : {w.resource_group} | Idle: {w.days_idle} days")
        print(f"    Waste   : ${w.monthly_cost:.2f}/month")
        print(f"    Action  : {w.recommendation}")

    print("\n" + "=" * 55)
    print(f"Total Direct Waste Elimination: ${total_waste:.2f}/month (${total_waste * 12:.2f}/year)")


def cmd_scheduler(args):
    print("\n[*] Simulating Non-Production Off-Hours Auto-Shutdown Schedules...")
    scheduler = NonProdScheduler()
    non_prod = [
        {"name": "vm-frontend-dev", "type": "vm", "monthly_cost": 192.0},
        {"name": "vm-batch-worker", "type": "vm", "monthly_cost": 384.0},
        {"name": "vm-api-stage", "type": "vm", "monthly_cost": 132.0},
    ]
    results = scheduler.evaluate_environment(non_prod)
    total_savings = sum(r.monthly_savings for r in results)

    print("\n--- [REPORT] OFF-HOURS SHUTDOWN (55 hrs/wk vs 168 hrs/wk) ---")
    for idx, s in enumerate(results, 1):
        print(f"\n[{idx}] Resource: {s.resource_name}")
        print(f"    24/7 Cost     : ${s.current_cost:.2f}/mo")
        print(f"    Scheduled Cost: ${s.scheduled_cost:.2f}/mo (Mon-Fri 08:00-19:00)")
        print(f"    Monthly Saving: ${s.monthly_savings:.2f}/mo ({s.savings_percentage:.1f}%)")

    print("\n" + "=" * 55)
    print(f"Total Scheduler Monthly Savings: ${total_savings:.2f}/month (${total_savings * 12:.2f}/year)")


def cmd_executive_summary(args):
    print("\n[*] Generating Complete FinOps Executive ROI Savings Summary...\n")
    analyzer = VMRightsizingAnalyzer()
    vm_savings = sum(r.monthly_savings for r in analyzer.analyze_fleet(get_sample_vms()))

    detector = CloudWasteDetector()
    waste_savings = sum(w.monthly_cost for w in detector.detect_waste(get_sample_waste_inventory()))

    scheduler = NonProdScheduler()
    sched_savings = sum(r.monthly_savings for r in scheduler.evaluate_environment([
        {"name": "vm-frontend-dev", "monthly_cost": 192.0},
        {"name": "vm-batch-worker", "monthly_cost": 384.0},
    ]))

    total_monthly = vm_savings + waste_savings + sched_savings
    total_annual = total_monthly * 12

    print("===============================================================")
    print("           FINOPS EXECUTIVE COST REDUCTION DASHBOARD           ")
    print("===============================================================")
    print(f" 1. VM Rightsizing & SKU Downsizing     :  ${vm_savings:8.2f} / mo")
    print(f" 2. Orphaned Disk & IP Waste Cleanup    :  ${waste_savings:8.2f} / mo")
    print(f" 3. Non-Prod Off-Hours Auto-Shutdown    :  ${sched_savings:8.2f} / mo")
    print("---------------------------------------------------------------")
    print(f" TOTAL MONTHLY RUN-RATE REDUCTION       :  ${total_monthly:8.2f} / mo")
    print(f" TOTAL PROJECTED ANNUAL CASH SAVINGS    :  ${total_annual:8.2f} / yr")
    print("===============================================================")


def main():
    parser = argparse.ArgumentParser(description="Cloud FinOps Cost Optimization Toolkit")
    subparsers = parser.add_subparsers(dest="command", help="FinOps subcommands")

    subparsers.add_parser("rightsize", help="Analyze VM compute rightsizing")
    subparsers.add_parser("waste", help="Scan for orphaned disks and public IPs")
    subparsers.add_parser("scheduler", help="Calculate off-hours shutdown savings")
    subparsers.add_parser("summary", help="Generate executive summary report")

    args = parser.parse_args()
    print_banner()

    if args.command == "rightsize":
        cmd_rightsize(args)
    elif args.command == "waste":
        cmd_waste(args)
    elif args.command == "scheduler":
        cmd_scheduler(args)
    elif args.command == "summary":
        cmd_executive_summary(args)
    else:
        # Default run executive summary
        cmd_executive_summary(args)


if __name__ == "__main__":
    main()
