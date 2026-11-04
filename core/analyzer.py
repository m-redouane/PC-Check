class DiagnosticEngine:
    """Moteur d'évaluation et de diagnostic système."""

    @staticmethod
    def analyze_ram(ram_info):
        issues = []
        usage = ram_info.get("percent_used", 0)
        available_gb = ram_info.get("available_gb", 0)

        if usage >= 90:
            issues.append({
                "level": "CRITICAL",
                "category": "RAM",
                "title": "Mémoire vive presque saturée",
                "description": f"L'utilisation de la RAM atteint {usage}%. Le système risque de ralentir fortement.",
                "recommendation": "Fermez les applications gourmandes en arrière-plan ou envisagez un passage à 32 Go de RAM."
            })
        elif usage >= 75:
            issues.append({
                "level": "WARNING",
                "category": "RAM",
                "title": "Consommation RAM élevée",
                "description": f"L'utilisation de la RAM est de {usage}% (seulement {available_gb} Go disponibles).",
                "recommendation": "Vérifiez les processus en arrière-plan consommateurs de mémoire (navigateurs, applications au démarrage)."
            })
        else:
            issues.append({
                "level": "INFO",
                "category": "RAM",
                "title": "Mémoire RAM optimale",
                "description": f"Utilisation normale à {usage}%.",
                "recommendation": "Aucune action requise."
            })
        return issues

    @staticmethod
    def analyze_disks(disks_info):
        issues = []
        for disk in disks_info:
            usage = disk.get("percent_used", 0)
            free_gb = disk.get("free_gb", 0)
            mountpoint = disk.get("mountpoint", "")

            if free_gb < 20 or usage >= 90:
                issues.append({
                    "level": "CRITICAL",
                    "category": "Stockage",
                    "title": f"Espace critique sur le lecteur {mountpoint}",
                    "description": f"Il ne reste que {free_gb} Go libres ({usage}% utilisé).",
                    "recommendation": "Libérez immédiatement de l'espace disque pour éviter un blocage des mises à jour Windows."
                })
            elif usage >= 75:
                issues.append({
                    "level": "WARNING",
                    "category": "Stockage",
                    "title": f"Espace disque à surveiller sur {mountpoint}",
                    "description": f"Le lecteur est rempli à {usage}% ({free_gb} Go libres).",
                    "recommendation": "Effectuez un nettoyage des fichiers temporaires et des téléchargements obsolètes."
                })
            else:
                issues.append({
                    "level": "INFO",
                    "category": "Stockage",
                    "title": f"Lecteur {mountpoint} en bon état",
                    "description": f"{free_gb} Go d'espace libre disponibles ({usage}% utilisé).",
                    "recommendation": "Aucune action requise."
                })
        return issues

    @classmethod
    def run_full_diagnostic(cls, hardware_data):
        results = {
            "overall_status": "GOOD",
            "warnings_count": 0,
            "critical_count": 0,
            "reports": []
        }

        # Analyse RAM et Disques
        ram_reports = cls.analyze_ram(hardware_data.get("ram", {}))
        disk_reports = cls.analyze_disks(hardware_data.get("disks", []))

        all_reports = ram_reports + disk_reports
        results["reports"] = all_reports

        # Calcul du bilan général
        for item in all_reports:
            if item["level"] == "CRITICAL":
                results["critical_count"] += 1
            elif item["level"] == "WARNING":
                results["warnings_count"] += 1

        if results["critical_count"] > 0:
            results["overall_status"] = "ATTENTION"
        elif results["warnings_count"] > 0:
            results["overall_status"] = "À SURVEILLER"
        else:
            results["overall_status"] = "EXCELLENT"

        return results