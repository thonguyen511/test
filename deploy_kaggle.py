import os
import json
import subprocess
import sys

# The Kaggle API now uses KAGGLE_API_TOKEN
ACCOUNTS = [
    {"username": "thonguyen511", "token": "KGAT_9a29974782c1c24e1e9bccf69a51e21d"},
    {"username": "hero0511acc", "token": "KGAT_8aad194411dbee85815ec01a682f3047"},
    {"username": "tqunacc", "token": "KGAT_46cc7c9f3ebb3239e81b25d0f7f6ae97"},
    {"username": "acc3conheo", "token": "KGAT_9b980e55d4c06e72e229bc520ae1ac98"},
]

def deploy():
    with open('main_template.py', 'r') as f:
        template = f.read()

    os.makedirs('notebooks', exist_ok=True)
    has_errors = False

    for i in range(20):
        acc_index = i // 5
        account = ACCOUNTS[acc_index]
        
        print(f"\n==================================================")
        print(f"Processing Notebook {i} using account {account['username']}")
        
        # Use the correct env variable for the new Kaggle API
        os.environ['KAGGLE_API_TOKEN'] = account['token']
        
        kernel_id = f"{account['username']}/automated-task-notebook-{i}"
        
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
            
        print(f"🚀 Pushing new version for notebook {i}...")
        try:
            push_result = subprocess.run(
                ["kaggle", "kernels", "push", "-p", nb_dir], 
                capture_output=True, text=True
            )
            
            # Check if authentication failed or command failed
            if push_result.returncode == 0 and "Authentication required" not in push_result.stdout:
                print(f"Successfully pushed and started a new session for notebook {i}!")
            else:
                print(f"❌ Failed to push notebook {i}.")
                print(f"Error output:\n{push_result.stdout}\n{push_result.stderr}")
                has_errors = True
        except Exception as e:
            print(f"Exception occurred while pushing notebook {i}: {e}")
            has_errors = True

    # If any notebook failed to push, exit with an error code so GitHub Action turns red!
    if has_errors:
        sys.exit(1)

if __name__ == "__main__":
    deploy()
