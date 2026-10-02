import os
import json
import subprocess

# In a real production environment, you should use GitHub Secrets and load them via os.getenv()
ACCOUNTS = [
    {"username": "thonguyen511", "key": "9a29974782c1c24e1e9bccf69a51e21d"},
    {"username": "hero0511acc", "key": "8aad194411dbee85815ec01a682f3047"},
    {"username": "tqunacc", "key": "46cc7c9f3ebb3239e81b25d0f7f6ae97"},
    {"username": "acc3conheo", "key": "9b980e55d4c06e72e229bc520ae1ac98"},
]

def deploy():
    with open('main_template.py', 'r') as f:
        template = f.read()

    os.makedirs('notebooks', exist_ok=True)

    for i in range(20):
        acc_index = i // 5
        account = ACCOUNTS[acc_index]
        
        print(f"\n==================================================")
        print(f"Processing Notebook {i} using account {account['username']}")
        
        os.environ['KAGGLE_USERNAME'] = account['username']
        os.environ['KAGGLE_KEY'] = account['key']
        
        kernel_id = f"{account['username']}/automated-task-notebook-{i}"
        
        # 1. CHECK STATUS FIRST
        print(f"Checking status of {kernel_id}...")
        status_result = subprocess.run(
            ["kaggle", "kernels", "status", kernel_id], 
            capture_output=True, text=True
        )
        
        stdout_lower = status_result.stdout.lower()
        
        if 'running' in stdout_lower or 'queued' in stdout_lower:
            print(f"⏭️ Notebook [{kernel_id}] is currently RUNNING/QUEUED. Skipping push.")
            continue
            
        print(f"✅ Notebook [{kernel_id}] is complete/error or doesn't exist yet. Preparing to push a new version...")
        
        nb_dir = f"notebooks/nb_{i}"
        os.makedirs(nb_dir, exist_ok=True)
        
        source_code = template.replace('{{NOTEBOOK_INDEX}}', str(i))
        with open(f"{nb_dir}/main.py", 'w') as f:
            f.write(source_code)
            
        metadata = {
          "id": kernel_id,
          "title": f"Automated Task Notebook {i}",
          "code_file": "main.py",
          "language": "python",
          "kernel_type": "script",
          "is_private": "true",
          "enable_gpu": "false",
          "enable_internet": "true",
          "dataset_sources": [],
          "competition_sources": [],
          "kernel_sources": []
        }
        with open(f"{nb_dir}/kernel-metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
            
        # 2. PUSH NEW VERSION
        print(f"🚀 Pushing new version for notebook {i}...")
        try:
            push_result = subprocess.run(
                ["kaggle", "kernels", "push", "-p", nb_dir], 
                capture_output=True, text=True
            )
            if push_result.returncode == 0:
                print(f"Successfully pushed and started a new session for notebook {i}!")
            else:
                print(f"Failed to push notebook {i}. Error: {push_result.stderr}")
        except Exception as e:
            print(f"Exception occurred while pushing notebook {i}: {e}")

if __name__ == "__main__":
    deploy()
