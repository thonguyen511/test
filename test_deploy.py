import os
import json
import subprocess

ACCOUNTS = [
    {"username": "thonguyen511", "key": "9a29974782c1c24e1e9bccf69a51e21d"},
]

def deploy():
    with open('main_template.py', 'r') as f:
        template = f.read()

    os.makedirs('notebooks', exist_ok=True)

    for i in range(1):
        account = ACCOUNTS[0]
        
        print(f"Processing Notebook {i} using account {account['username']}")
        
        os.environ['KAGGLE_USERNAME'] = account['username']
        os.environ['KAGGLE_KEY'] = account['key']
        
        kernel_id = f"{account['username']}/automated-task-notebook-{i}"
        
        print(f"Checking status of {kernel_id}...")
        status_result = subprocess.run(
            ["kaggle", "kernels", "status", kernel_id], 
            capture_output=True, text=True
        )
        print("STATUS STDOUT:", status_result.stdout)
        print("STATUS STDERR:", status_result.stderr)
        
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
            
        print(f"Pushing new version for notebook {i}...")
        push_result = subprocess.run(
            ["kaggle", "kernels", "push", "-p", nb_dir], 
            capture_output=True, text=True
        )
        print("PUSH STDOUT:", push_result.stdout)
        print("PUSH STDERR:", push_result.stderr)

if __name__ == "__main__":
    deploy()
