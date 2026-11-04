from core.hardware import HardwareDetector
from core.analyzer import DiagnosticEngine

def run_diagnostic():
    print("==================================================")
    print("       PC CHECK — DIAGNOSTIC SYSTÈME V0.3        ")
    print("==================================================")

    # 1. Collecte des données matérielles
    hardware_data = {
        "os": HardwareDetector.get_os_info(),
        "cpu": HardwareDetector.get_cpu_info(),
        "ram": HardwareDetector.get_ram_info(),
        "gpus": HardwareDetector.get_gpu_info(),
        "disks": HardwareDetector.get_disks_info()
    }

    # 2. Exécution du moteur de diagnostic
    analysis = DiagnosticEngine.run_full_diagnostic(hardware_data)

    print(f"\n[État général du système : {analysis['overall_status']}]")
    print(f"Alertes : {analysis['critical_count']} Critique(s) | {analysis['warnings_count']} Avertissement(s)\n")

    print("--- DÉTAIL DU DIAGNOSTIC ---")
    for report in analysis["reports"]:
        prefix = f"[{report['level']}]"
        print(f"{prefix:<10} {report['category']} - {report['title']}")
        print(f"           Explication    : {report['description']}")
        print(f"           Recommandation : {report['recommendation']}\n")

if __name__ == "__main__":
    run_diagnostic()