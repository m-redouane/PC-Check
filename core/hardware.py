import platform
import psutil
import subprocess
import json

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
        return {
            "name": platform.processor(),
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "current_freq_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else None
        }

    @staticmethod
    def get_ram_info():
        ram = psutil.virtual_memory()
        return {
            "total_gb": round(ram.total / (1024 ** 3), 2),
            "available_gb": round(ram.available / (1024 ** 3), 2),
            "percent_used": ram.percent
        }

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
            cmd = 'powershell "Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion | ConvertTo-Json"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                if isinstance(data, dict):
                    data = [data]
                for item in data:
                    vram = item.get("AdapterRAM")
                    vram_gb = round(vram / (1024 ** 3), 2) if vram and isinstance(vram, int) else None
                    gpus.append({
                        "name": item.get("Name"),
                        "vram_gb": vram_gb,
                        "driver_version": item.get("DriverVersion")
                    })
        except Exception:
            pass
        return gpus