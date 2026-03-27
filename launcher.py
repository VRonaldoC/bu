import subprocess
import time

total_tokens = 4

for i in range(1, total_tokens + 1):
    subprocess.Popen(["python3", "SCRIPT_PERMISO_DESBLOQUEO.py", str(i)])
    time.sleep(0.3)
