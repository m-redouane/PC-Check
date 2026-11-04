import os
import psutil
import clr

class HardwareSensors:
    def __init__(self):
        self.computer = None
        self._init_monitor()

    def _init_monitor(self):
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
        except Exception as e:
            print(f"Erreur d'initialisation de la DLL LHM : {e}")

    def get_live_metrics(self):
        cpu_load = f"{psutil.cpu_percent(interval=0.1):.1f} %"
        ram_load = f"{psutil.virtual_memory().percent:.1f} %"
        cores_load = [f"{p:.1f} %" for p in psutil.cpu_percent(percpu=True)]

        cpu_temp = "N/A"
        gpu_temp = "N/A"
        gpu_load = "N/A"
        disks_temp = "N/A"
        disk_usage = f"{psutil.disk_usage('C:').percent:.1f} %"

        if self.computer:
            try:
                for hw in self.computer.Hardware:
                    hw.Update()
                    hw_type = str(hw.HardwareType)
                    
                    # Récupération de tous les capteurs (y compris sous-matériel)
                    all_sensors = list(hw.Sensors)
                    for sub in hw.SubHardware:
                        sub.Update()
                        all_sensors.extend(list(sub.Sensors))

                    for sensor in all_sensors:
                        s_type = str(sensor.SensorType)
                        s_name = str(sensor.Name)
                        val = sensor.Value

                        if val is not None:
                            # Processeur (CPU) - Recherche des sondes Tctl/Tdie ou Package
                            if "Cpu" in hw_type and s_type == "Temperature":
                                if any(k in s_name for k in ["Package", "Tctl", "Tdie", "CPU", "Core Average"]):
                                    if cpu_temp == "N/A":
                                        cpu_temp = f"{val:.1f} °C"
                            
                            # Carte Graphique (GPU AMD/Nvidia)
                            elif "Gpu" in hw_type:
                                if s_type == "Temperature" and ("Core" in s_name or "GPU" in s_name or "Temperature" in s_name):
                                    gpu_temp = f"{val:.1f} °C"
                                elif s_type == "Load" and ("Core" in s_name or "GPU" in s_name or "Total" in s_name):
                                    gpu_load = f"{val:.1f} %"

                            # Stockage (SSD Kingston)
                            elif "Storage" in hw_type and s_type == "Temperature":
                                disks_temp = f"{val:.1f} °C"
            except Exception as e:
                print(f"Erreur de lecture des capteurs réels : {e}")

        return {
            "cpu_load": cpu_load,
            "cpu_temp": cpu_temp,
            "gpu_load": gpu_load if gpu_load != "N/A" else "0.0 %",
            "gpu_temp": gpu_temp,
            "ram_load": ram_load,
            "cores_load": cores_load,
            "disks_temp": disks_temp,
            "disk_usage": disk_usage
        }