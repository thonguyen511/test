import os
import json
import subprocess
import sys

# The actual key is the full string including KGAT_
ACCOUNTS = [
    {"username": "thonguyen511", "token": "KGAT_9a29974782c1c24e1e9bccf69a51e21d"},
    {"username": "hero0511acc", "token": "KGAT_8aad194411dbee85815ec01a682f3047"},
    {"username": "tqunacc", "token": "KGAT_46cc7c9f3ebb3239e81b25d0f7f6ae97"},
    {"username": "acc3conheo", "token": "KGAT_9b980e55d4c06e72e229bc520ae1ac98"},
]

def deploy():
    with open('main_template.py', 'r') as f:
        template = f.read()

    # Load sessions state
    sessions_file = 'sessions.json'
    if os.path.exists(sessions_file):
        with open(sessions_file, 'r') as f:
            sessions = json.load(f)
    else:
        sessions = {}

    os.makedirs('notebooks', exist_ok=True)
    has_errors = False
    state_changed = False

    # Ensure ~/.kaggle directory exists
    kaggle_dir = os.path.expanduser('~/.kaggle')
    os.makedirs(kaggle_dir, exist_ok=True)
    
    gh_pat = os.environ.get('GH_PAT', 'None')

    for i in range(20):
        acc_index = i // 5
        account = ACCOUNTS[acc_index]
        nb_key = f"notebook_{i}"
        
        # Check limit
        if sessions.get(nb_key, 0) >= 10:
            print(f"\n==================================================")
            print(f" Notebook {i} has already completed 10 sessions! Sleeping until reset.")
            continue
            
        print(f"\n==================================================")
        print(f"Processing Notebook {i} using account {account['username']}")
        
        # Method 1: Set Environment Variables
        os.environ['KAGGLE_USERNAME'] = account['username']
        os.environ['KAGGLE_KEY'] = account['token'].replace("KGAT_", "")
        os.environ['KAGGLE_API_TOKEN'] = account['token']
        
        # Method 2: Force write kaggle.json
        kaggle_json_path = os.path.join(kaggle_dir, 'kaggle.json')
        with open(kaggle_json_path, 'w') as f:
            json.dump({
                "username": account["username"],
                "key": account["token"].replace("KGAT_", "")
            }, f)
        try:
            os.chmod(kaggle_json_path, 0o600)
        except Exception:
            pass
        
        kernel_id = f"{account['username']}/automated-task-notebook-{i}"
        
        print(f"Checking status of {kernel_id}...")
        status_result = subprocess.run(
            ["kaggle", "kernels", "status", kernel_id], 
            capture_output=True, text=True
        )
        
        stdout_lower = status_result.stdout.lower()
        
        while 'running' in stdout_lower or 'queued' in stdout_lower:
            import time
            print(f" Notebook [{kernel_id}] is still RUNNING/QUEUED. Waiting 30 seconds...")
            time.sleep(30)
            status_result = subprocess.run(
                ["kaggle", "kernels", "status", kernel_id], 
                capture_output=True, text=True
            )
            stdout_lower = status_result.stdout.lower()
            
        print(f" Notebook [{kernel_id}] is complete/error or doesn't exist yet. Preparing to push session {sessions.get(nb_key, 0) + 1}/10...")
        
        nb_dir = f"notebooks/nb_{i}"
        os.makedirs(nb_dir, exist_ok=True)
        
        source_code = template.replace('{{NOTEBOOK_INDEX}}', str(i)).replace('{{GH_PAT_TOKEN}}', gh_pat)
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
            
        print(f" Pushing new version for notebook {i}...")
        try:
            push_result = subprocess.run(
                ["kaggle", "kernels", "push", "-p", nb_dir], 
                capture_output=True, text=True
            )
            
            if push_result.returncode == 0 and "Authentication required" not in push_result.stdout:
                print(f"Successfully pushed and started a new session for notebook {i}!")
                sessions[nb_key] = sessions.get(nb_key, 0) + 1
                state_changed = True
            else:
                print(f" Failed to push notebook {i}.")
                print(f"Error output:\n{push_result.stdout}\n{push_result.stderr}")
                has_errors = True
        except Exception as e:
            print(f"Exception occurred while pushing notebook {i}: {e}")
            has_errors = True

    if state_changed:
        with open(sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)

    if has_errors:
        sys.exit(1)

if __name__ == "__main__":
    deploy()
