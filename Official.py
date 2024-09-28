from azure.identity import DeviceCodeCredential
import requests
import json
import csv
import time
# Azure credentials
tenant_id = "db05faca-c82a-4b9d-b9c5-0f64b6755421"
client_id = "6d914498-1868-429d-84ec-c2f0f5517878"
scope = "openid profile api://0e5d8fbf-d9da-4ec0-9795-b27bd985342d/user_impersonation"
# GitHub Actions URL (from the image)
github_url = "https://api.github.com/repos/optum-labs/Apollo.IaC.Hub/actions/workflows/apply-to-prod.yml/dispatches"
# GitHub Actions Payload Template
def create_payload(subscription_id):
    return json.dumps({
        "ref": "main",
        "inputs": {
            "version": "main",
            "subscription-id": subscription_id,
            "run-apply": False  # Adjust based on your requirements
        }
    })

# GitHub Headers

github_headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': 'Bearer TOKEN',  # Replace with your GitHub token
    'X-GitHub-Api-Version': '2022-11-28',
    'Content-Type': 'application/json'
}

# List of known subscription IDs to skip

skip_list = ['cc803b56-bf16-4400-b769-3502c564cefb',
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

# Get token

credential = DeviceCodeCredential(client_id=client_id, tenant_id=tenant_id)
token = credential.get_token(scope)
authorization = "Bearer " + token.token
# API URL for subscriptions
url = "https://apollomdsprod-prod.haligi.cloud/api/apollo-mds/subscriptions/search/byActiveTrue"
# Request headers
headers = {
    'Accept': 'application/hal+json',
    'Authorization': authorization
}
# Send the GET request

response = requests.get(url, headers=headers)

# Check if the request was successful


if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    # Extract azureSubscriptionIds and skip the known ones
    subscription_ids = [
        sub['azureSubscriptionId'] 
        for sub in data['_embedded']['subscriptions'] 
        if sub['azureSubscriptionId'] not in skip_list
    ]

    # Write filtered subscription IDs to a CSV file
    with open('Output.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['azureSubscriptionId'])  # Write header
        for sub_id in subscription_ids:
            writer.writerow([sub_id])
    print("Filtered azureSubscriptionIds have been saved to Output.csv")
    batch_size = 2
    wait_time_seconds = 30

    for i in range(0, len(subscription_ids), batch_size):

        batch = subscription_ids[i:i + batch_size]
        print(f"Processing batch {i // batch_size + 1}: {batch}")
        for sub_id in batch:
           # Create the payload for each subscription ID
            payload = create_payload(sub_id)
           # Send the POST request to GitHub Actions
            github_response = requests.post(github_url, headers=github_headers, data=payload)
           # Print response for debugging
            print(f"Triggered GitHub Action for Subscription ID: {sub_id}")
            print(f"GitHub Response: {github_response.status_code}, {github_response.text}")
       # Wait before moving to the next batch
        if i + batch_size < len(subscription_ids):

            print(f"Waiting for {wait_time_seconds} seconds before processing the next batch...")
            time.sleep(wait_time_seconds)
            print("All batches processed.")
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            print(response.text)
 
