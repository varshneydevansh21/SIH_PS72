import os
import sys
import subprocess

backend_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
backend_dir = os.path.abspath(backend_dir)

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


def run_seed():
    seed_script = os.path.join(backend_dir, "scripts", "seed_demo_data.py")
    if os.path.exists(seed_script):
        env = dict(os.environ)
        env["PYTHONPATH"] = f"{backend_dir}:{env.get('PYTHONPATH', '')}"
        try:
            res = subprocess.run([sys.executable, seed_script], env=env, check=True)
            return res.returncode
        except Exception:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(run_seed())
