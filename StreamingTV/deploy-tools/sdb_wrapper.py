import sys
import os
import subprocess

args = sys.argv[1:]

# Intercept vd_appuninstall - return success without doing anything
if "vd_appuninstall" in args:
    sys.exit(0)

# All other calls: pass to real sdb
sdb_real = os.path.join(os.path.dirname(sys.executable), "sdb_real.exe")
result = subprocess.run([sdb_real] + args)
sys.exit(result.returncode)
