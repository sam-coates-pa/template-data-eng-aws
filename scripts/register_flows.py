
"""
Register Prefect flows.
This can be extended to register multiple flows.
"""
import subprocess

def register():
    # Prefect CLI registration
    subprocess.run(["prefect", "deploy", "--all"], check=False)
    print("Flows registered.")

if __name__ == "__main__":
    register()
