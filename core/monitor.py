import os
import clr

# Chargement de la bibliothèque .NET depuis le dossier core
dll_path = os.path.abspath("core/LibreHardwareMonitorLib.dll")
if os.path.exists(dll_path):
    clr.AddReference(dll_path)
else:
    clr.AddReference("LibreHardwareMonitorLib")

from LibreHardwareMonitor.Hardware import Computer

# 1. Initialisation de l'ordinateur et activation des composants cibles
computer = Computer()
computer.IsCpuEnabled = True
computer.IsGpuEnabled = True
computer.IsStorageEnabled = True
computer.IsMemoryEnabled = True
computer.Open()

print("=== EXPLOITATION DES CAPTEURS MATÉRIELS (PC CHECK) ===")

try:
    for hardware in computer.Hardware:
        hardware.Update()
        hw_type = str(hardware.HardwareType)
        print(f"\n[Composant] {hardware.Name} ({hw_type})")
        
        for sensor in hardware.Sensors:
            sensor_type = str(sensor.SensorType)
            sensor_name = str(sensor.Name)
            sensor_value = sensor.Value
            
            if sensor_value is None:
                continue

            # 2. Stockage : Uniquement la température Composite (évite le faux seuil critique à 79°C)
            if "Storage" in hw_type and "Temperature" in sensor_type:
                if "Composite" in sensor_name:
                    print(f"  -> {sensor_name} : {sensor_value:.1f} °C")
            
            # 3. Processeur : Température globale (Package / Tdie)
            elif "Cpu" in hw_type and "Temperature" in sensor_type:
                if "Package" in sensor_name or "Tdie" in sensor_name or "CPU" in sensor_name:
                    print(f"  -> {sensor_name} : {sensor_value:.1f} °C")
            
            # 4. GPU : Affichage de la tension (Voltage) et de l'utilisation (Load) au lieu de la température
            elif "Gpu" in hw_type:
                if "Voltage" in sensor_type:
                    print(f"  -> {sensor_name} (Tension) : {sensor_value:.3f} V")
                elif "Load" in sensor_type:
                    print(f"  -> {sensor_name} (Utilisation) : {sensor_value:.1f} %")

finally:
    computer.Close()
    print("\n=== ANALYSE TERMINÉE ===")