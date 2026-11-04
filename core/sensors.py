import os
import psutil
from core.logger import get_logger

logger = get_logger("SensorsEngine")

try:
    import clr
except ImportError:
    clr = None

class HardwareSensors:
    def __init__(self):
        self.computer = None
        self._init_monitor()

    def _init_monitor(self):
        if not clr:
            return
        try:
            dll_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "LibreHardwareMonitorLib.dll"))
            if os.path.exists(dll_path):
                clr.AddReference(dll_path)
                from LibreHardwareMonitor import Hardware
                self.computer = Hardware.Computer()
                self.computer.IsCpuEnabled = True
                self.computer.IsGpuEnabled = True
                self.computer.IsMemoryEnabled = True
                self.computer.IsStorageEnabled = True
                self.computer.IsMotherboardEnabled = True
                self.computer.Open()
                logger.info("Moteur matériel LHM embarqué initialisé avec succès.")
        except Exception as e:
            logger.error(f"Erreur d'initialisation du moteur matériel interne : {e}")

    def get_live_metrics(self):
        # Initialisation du dictionnaire de métriques pour construire l'arborescence complète
        metrics = {
            "components": []
        }

        # On rajoute les infos de base psutil pour l'utilisation (comme dans l'ancienne version, si besoin ailleurs)
        metrics["cpu_load"] = f"{psutil.cpu_percent(interval=0.1):.1f} %"
        metrics["ram_load"] = f"{psutil.virtual_memory().percent:.1f} %"
        metrics["disk_usage"] = f"{psutil.disk_usage('C:').percent:.1f} %"

        if self.computer:
            try:
                for hw in self.computer.Hardware:
                    hw.Update()
                    
                    comp_data = {
                        "name": str(hw.Name),
                        "type": str(hw.HardwareType),
                        "sensor_categories": {} # Ex: 'Temperatures': [], 'Voltages': []
                    }

                    for sensor in hw.Sensors:
                        if sensor.Value is not None:
                            s_type = str(sensor.SensorType) # Temperature, Load, Voltage, Power, Clock
                            s_name = str(sensor.Name)
                            s_val = sensor.Value
                            
                            # Logique spécifique de formatage selon le type
                            val_str = f"{s_val:.2f}"
                            if s_type == "Temperature": val_str += " °C"
                            elif s_type == "Load": val_str += " %"
                            elif s_type == "Voltage": val_str += " V"
                            elif s_type == "Power": val_str += " W"
                            elif s_type == "Clock": val_str += " MHz"
                            
                            # Création de la catégorie si elle n'existe pas
                            cat_name = s_type + "s" # On ajoute un 's' (Temperatures, Voltages...) pour coller au style LHM
                            if cat_name not in comp_data["sensor_categories"]:
                                comp_data["sensor_categories"][cat_name] = []
                                
                            comp_data["sensor_categories"][cat_name].append({
                                "name": s_name,
                                "value": val_str,
                                "raw_value": s_val
                            })
                            
                    metrics["components"].append(comp_data)
            except Exception:
                pass

        return metrics