import requests
import json
import csv
import time
from azure.identity import DeviceCodeCredential
# =================== Configuration Variables ====================
# Azure credentials
Tenant_Id = "db05faca-c82a-4b9d-b9c5-0f64b6755421"
Clien_Id = "6d914498-1868-429d-84ec-c2f0f5517878"
Scope = "openid profile api://0e5d8fbf-d9da-4ec0-9795-b27bd985342d/user_impersonation"
# GitHub credentials and URLs
Github_Url = "https://api.github.com/repos/optum-labs/Apollo.IaC.Hub/actions/workflows/apply-to-prod.yml/dispatches"
Github_Token = ""
# List of known subscription IDs to skip
Skip_List = ['cc803b56-bf16-4400-b769-3502c564cefb',
'057889dc-dc8b-4148-859d-ab721a5f33bc',
'34964669-2679-4138-922c-bfca8ef8e2c5',
'56857d59-2e55-4ea7-b4be-9a6b09413f44',
'4c28738f-f899-4e78-9f04-6c53c9c0e1e9',
'93e8d689-6d2a-4f55-a633-085484999c02',
'd7965193-f5a8-4550-b11d-bd1f52d83247',
'20d4ad54-cc90-470c-b65a-1d0e2c619f71',
'11713394-ca05-43a3-bb2b-6ca7bd92bd66',
'e07c7c8b-1b0b-434f-8593-4322e4890584',
'f38f0533-2183-44c9-b473-c4b77e5fcc07',
'd3cc24eb-e455-45bf-932e-ab0c70648f9b',
'37aeffb0-178f-4868-a8ce-69a075d5d418',
'b9cc84fb-e181-4d2d-9bd3-fae926454d73',
'7e1937f3-14f6-486e-a3a0-893e6880290c',
]
# API URL for subscriptions
Subscription_Api_Url = "https://apollomdsprod-prod.haligi.cloud/api/apollo-mds/subscriptions/search/byActiveTrue"

# Batch configuration

Batch_Size = 10
Sleep_Time = 30 #In Seconds
Csv_Filepath = 'Output.csv'

# Get the Azure Access Token 

def get_azure_token():
   """Authenticate using Azure DeviceCodeCredential and get the token."""
   credential = DeviceCodeCredential(client_id=Clien_Id, tenant_id=Tenant_Id)
   token = credential.get_token(Scope)
   return token.token

# Get the Active Subscriptions and remove the skip list from the active subs for which the Backfill is not needed

def fetch_active_subscriptions(authorization):
   """Fetch active Azure subscriptions from the API."""
   headers = {
       'Accept': 'application/hal+json',
       'Authorization': f"Bearer {authorization}"
   }
   response = requests.get(Subscription_Api_Url, headers=headers)
   if response.status_code == 200:
       data = response.json()
       subscription_ids = [
           sub['azureSubscriptionId']
           for sub in data['_embedded']['subscriptions']
           if sub['azureSubscriptionId'] not in Skip_List
       ]
       return subscription_ids
   else:
       print(f"Failed to fetch data. Status code: {response.status_code}")
       print(response.text)
       return []

# Save the filtered active subs to Output.csv

def save_to_csv(subscription_ids):
   """Save filtered subscription IDs to a CSV file."""
   with open(Csv_Filepath, 'w', newline='') as csv_file:
       writer = csv.writer(csv_file)
       writer.writerow(['azureSubscriptionId'])  # Write header
       for sub_id in subscription_ids:
           writer.writerow([sub_id])
   print(f"Filtered azureSubscriptionIds have been saved to {Csv_Filepath}")

# Function for triggering the GitHub Iac Payload. For applying the backfill change the "run-apply" to True

def create_github_payload(subscription_id):
   """Create the payload for GitHub Actions API."""
   return json.dumps({
       "ref": "main",
       "inputs": {
           "version": "main",
           "subscription-id": subscription_id,
           "run-apply": False  # Adjust based on your requirements
       }
   })

# Trigger the Payload for GitHub Actions

def trigger_github_action(subscription_id):
   """Trigger GitHub Action for a given subscription ID."""
   Github_Headers = {
       'Accept': 'application/vnd.github+json',
       'Authorization': f'Bearer {Github_Token}',
       'X-GitHub-Api-Version': '2022-11-28',
       'Content-Type': 'application/json'
   }
   Payload = create_github_payload(subscription_id)
   response = requests.post(Github_Url, headers=Github_Headers, data=Payload)
   if response.status_code == 204:
       print(f"Successfully triggered GitHub Action for Subscription ID: {subscription_id}")
   else:
       print(f"Failed to trigger GitHub Action for Subscription ID: {subscription_id}. Response: {response.status_code}, {response.text}")

# With the given batch size and sleep time(in sec), This function will start trigger the workflow for the batch size and wait for the mentioned seconds

def process_subscriptions_in_batches(subscription_ids):
   """Process the subscription IDs in batches and trigger GitHub Actions."""
   for i in range(0, len(subscription_ids), Batch_Size):
       batch = subscription_ids[i:i + Batch_Size]
       print(f"Processing batch {i // Batch_Size + 1}: {batch}")
       for sub_id in batch:
           try:
               trigger_github_action(sub_id)
           except Exception as e:
               print(f"Error triggering GitHub Action for Subscription ID: {sub_id}. Exception: {str(e)}")
       if i + Batch_Size < len(subscription_ids):
           print(f"Waiting for {Sleep_Time} seconds before processing the next batch...")
           time.sleep(Sleep_Time)
   print("All batches processed.")

# Main Function

def main():
   """Main execution flow of the script."""
   # Get Azure authentication token
   azure_token = get_azure_token()
   # Fetch active subscriptions
   subscription_ids = fetch_active_subscriptions(azure_token)
   # Save subscription IDs to CSV
   if subscription_ids:
       save_to_csv(subscription_ids)
   # Process subscriptions and trigger GitHub Actions in batches
   process_subscriptions_in_batches(subscription_ids)
# Call the main function
if __name__ == "__main__":
   main()
