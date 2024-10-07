import requests   
workflow_file_name = 'apply-to-prod.yml'  
token = ''  
Github_Url = "https://api.github.com/repos/optum-labs/Apollo.IaC.Hub/actions/workflows/apply-to-prod.yml/runs"
  
headers = {  
    'Authorization': f'token {token}',  
    'Accept': 'application/vnd.github.v3+json'  
}  
response = requests.get(Github_Url, headers=headers)  
runs = response.json()['workflow_runs'] 
latest_run = runs[0] if runs else None  
if latest_run and latest_run['conclusion'] == 'success':  
    print('The latest workflow run was successful!')  
else:  
    print('The latest workflow run was not successful.')  
