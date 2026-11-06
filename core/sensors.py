import os
import sys
import psutil
from core.logger import get_logger

logger = get_logger("SensorsEngine")

try:
    import clr
except ImportError:
    clr = None

def resource_path(relative_path):
    """ Obtient le chemin absolu vers la ressource, compatible dev et PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class HardwareSensors:
    def __init__(self):
        self.computer = None
        self._init_monitor()

    def _init_monitor(self):
        if not clr:
            return
        try:
            # Utilisation de resource_path pour localiser la DLL de manière sécurisée
            dll_path = resource_path(os.path.join("core", "LibreHardwareMonitorLib.dll"))
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
            else:
                logger.error(f"DLL introuvable au chemin : {dll_path}")
        except Exception as e:
            logger.error(f"Erreur d'initialisation du moteur matériel interne : {e}")

    def get_live_metrics(self):
        metrics = {
            "components": []
        }

        metrics["cpu_load"] = f"{psutil.cpu_percent(interval=0.1):.1f} %"
        metrics["ram_load"] = f"{psutil.virtual_memory().percent:.1f} %"
        metrics["disk_usage"] = f"{psutil.disk_usage('C:').percent:.1f} %"

        if self.computer:
            try:
                def process_hardware(hw_item):
                    try:
                        hw_item.Update()
                        comp_data = {
                            "name": str(hw_item.Name),
                            "type": str(hw_item.HardwareType),
                            "sensor_categories": {}
                        }

                        for sensor in hw_item.Sensors:
                            if sensor.Value is not None:
                                s_type = str(sensor.SensorType)
                                s_name = str(sensor.Name)
                                s_val = sensor.Value
                                
                                val_str = f"{s_val:.2f}"
                                if s_type == "Temperature": val_str += " °C"
                                elif s_type == "Load": val_str += " %"
                                elif s_type == "Voltage": val_str += " V"
                                elif s_type == "Power": val_str += " W"
                                elif s_type == "Clock":
                                    val_str = f"{s_val * 1e-3:.2f} GHz"
                                
                                cat_name = s_type + "s"
                                if cat_name not in comp_data["sensor_categories"]:
                                    comp_data["sensor_categories"][cat_name] = []
                                    
                                comp_data["sensor_categories"][cat_name].append({
                                    "name": s_name,
                                    "value": val_str,
                                    "raw_value": s_val
                                })
                        
                        if comp_data["sensor_categories"]:
                            metrics["components"].append(comp_data)

                        for sub_hw in hw_item.SubHardware:
                            process_hardware(sub_hw)
                            
                    except Exception as sub_e:
                        logger.error(f"Erreur sur le sous-matériel {hw_item.Name}: {sub_e}")

                for hw in self.computer.Hardware:
                    process_hardware(hw)

            except Exception as e:
                logger.error(f"Erreur globale lors de la lecture des capteurs LHM : {e}")

        return metrics