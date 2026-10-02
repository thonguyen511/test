import time
import requests
import json
import os

print(f"Starting Kaggle Notebook { {{NOTEBOOK_INDEX}} }...")

# 5 iterations of 1 minute each = ~5 minutes total runtime
# (In production, change 5 to 720 for 12 hours)
iterations = 5

for i in range(iterations):
    print(f"Working on iteration {i+1}/{iterations}...")
    time.sleep(60)
    
print("Notebook finished its task!")

# ---------------------------------------------------------
# OPTION 1: SEND WEBHOOK TO GITHUB TO TRIGGER NEXT WORKFLOW
# ---------------------------------------------------------
GH_PAT = "{{GH_PAT_TOKEN}}"  # Injected by deploy_kaggle.py

if GH_PAT and GH_PAT != "None":
    if "{{NOTEBOOK_INDEX}}" == "0":
        print("Sending webhook to GitHub to instantly trigger the next run...")
        try:
            url = "https://api.github.com/repos/thonguyen511/test/actions/workflows/kaggle_workflow.yml/dispatches"
            headers = {
                "Authorization": f"Bearer {GH_PAT}",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            data = {"ref": "main"}
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 204:
                print("Successfully triggered GitHub Action!")
            else:
                print(f"Failed to trigger. Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            print(f"Error triggering webhook: {e}")
