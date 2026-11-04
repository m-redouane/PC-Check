import platform
import psutil
import subprocess
import json
import winreg

class HardwareDetector:
    """Collecte l'ensemble des informations matérielles du système."""
    
    @staticmethod
    def get_os_info():
        return {
            "os": platform.system(),
            "release": platform.release(),
            "architecture": platform.machine()
        }

    @staticmethod
    def get_cpu_info():
        name = None
        try:
            cmd = 'powershell "Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if result.returncode == 0 and result.stdout.strip():
                name = result.stdout.strip()
        except Exception:
            pass

        if not name:
            try:
                key_path = r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                    reg_name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
                    if reg_name:
                        name = reg_name.strip()
            except Exception:
                pass

        if not name:
            name = platform.processor()

        return {
            "name": name,
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "current_freq_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else None
        }

    @staticmethod
    def get_ram_info():
        ram = psutil.virtual_memory()
        speed = None
        slots_count = 0
        manufacturer = None
        part_number = None
        
        try:
            cmd = 'powershell "Get-CimInstance Win32_PhysicalMemory | Select-Object Manufacturer, PartNumber, Speed, Capacity | ConvertTo-Json"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                sticks = [data] if isinstance(data, dict) else data
                slots_count = len(sticks)
                if sticks:
                    first_stick = sticks[0]
                    speed = first_stick.get("Speed")
                    mfg = str(first_stick.get("Manufacturer", "")).strip()
                    pn = str(first_stick.get("PartNumber", "")).strip()
                    
                    # Filtrage des valeurs génériques non renseignées
                    if mfg and mfg.lower() not in ["unknown", "0000", "null"]:
                        manufacturer = mfg
                    if pn and pn.lower() not in ["unknown", "null", "none"]:
                        part_number = pn
        except Exception:
            pass

        return {
            "total_gb": round(ram.total / (1024 ** 3), 2),
            "available_gb": round(ram.available / (1024 ** 3), 2),
            "percent_used": ram.percent,
            "speed_mhz": speed,
            "slots_used": slots_count,
            "manufacturer": manufacturer,
            "part_number": part_number
        }

    @staticmethod
    def get_physical_disks():
        """Récupère les modèles physiques réels des SSD / HDD."""
        disks = []
        try:
            cmd = 'powershell "Get-CimInstance Win32_DiskDrive | Select-Object Model, MediaType, Size | ConvertTo-Json"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                items = [data] if isinstance(data, dict) else data
                for item in items:
                    size_gb = round(item.get("Size", 0) / (1024 ** 3), 2) if item.get("Size") else 0
                    disks.append({
                        "model": item.get("Model", "Disque Inconnu").strip(),
                        "media_type": item.get("MediaType", "Stockage"),
                        "size_gb": size_gb
                    })
        except Exception:
            pass
        return disks

    @staticmethod
    def get_disks_info():
        disks = []
        for partition in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "total_gb": round(usage.total / (1024 ** 3), 2),
                    "used_gb": round(usage.used / (1024 ** 3), 2),
                    "free_gb": round(usage.free / (1024 ** 3), 2),
                    "percent_used": usage.percent
                })
            except PermissionError:
                continue
        return disks

    @staticmethod
    def get_gpu_info():
        gpus = []
        try:
            cmd = 'powershell "Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion | ConvertTo-Json"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            wmi_gpus = []
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                wmi_gpus = [data] if isinstance(data, dict) else data

            key_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
            registry_map = {}
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as master_key:
                    for i in range(winreg.QueryInfoKey(master_key)[0]):
                        sub_key_name = winreg.EnumKey(master_key, i)
                        if sub_key_name.isdigit():
                            with winreg.OpenKey(master_key, sub_key_name) as sub_key:
                                try:
                                    desc, _ = winreg.QueryValueEx(sub_key, "DriverDesc")
                                    val, _ = winreg.QueryValueEx(sub_key, "HardwareInformation.qwMemorySize")
                                    vram_gb = round(val / (1024 ** 3), 2)
                                    registry_map[desc.strip()] = vram_gb
                                except FileNotFoundError:
                                    pass
            except Exception:
                pass

            for item in wmi_gpus:
                gpu_name = item.get("Name", "").strip()
                vram_gb = registry_map.get(gpu_name)
                
                if vram_gb is None:
                    for reg_name, reg_vram in registry_map.items():
                        if reg_name in gpu_name or gpu_name in reg_name:
                            vram_gb = reg_vram
                            break

                gpus.append({
                    "name": gpu_name,
                    "vram_gb": vram_gb,
                    "driver_version": item.get("DriverVersion")
                })
        except Exception:
            pass
        return gpus