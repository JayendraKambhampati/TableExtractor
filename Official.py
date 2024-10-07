import csv
import json
import requests
import sys
import time
from azure.identity import DeviceCodeCredential

def get_new_token(dev_support_client_id, tenant_id, scope):
  
    credential = DeviceCodeCredential(
        client_id = dev_support_client_id,
        tenant_id = tenant_id)
    
    token = credential.get_token(scope)
    
    return  "Bearer " + token.token
    # print (authorization)
# csv file name
FILE_NAME = "/Users/rkambham/Documents/UAIS/OpenAI/ProjectId.csv"

# initializing the titles and rows list
fields = []
rows = []
env = sys.argv[1]
is_searchable = sys.argv[2]
url = ""
dev_support_client_id = ""
tenant_id = "db05faca-c82a-4b9d-b9c5-0f64b6755421"
scope = ""

if "DEV" in env:
    url =  "https://gurucontrolplane-gcpdev.haligi.cloud/api/guru-project-api/v2/projects/{projectId}"
    dev_support_client_id = "2037e427-6c6d-4a40-b4d3-72ad205d24ad"
    scope = "api://6303e66b-d453-4a34-b407-bf47e2f21e87/user_impersonation"
elif "NONPROD" in env:
    url =   "https://gurucplaneopm-nonprod.haligi.cloud/api/guru-project-api/v2/projects/{projectId}"
    dev_support_client_id = "2037e427-6c6d-4a40-b4d3-72ad205d24ad"
    scope = "api://221e0e2d-07e4-4180-bec4-973a4fdf97d0/user_impersonation"
elif "PROD" in env:
    url = "https://gurucontrolplane-prod.unitedaistudio.uhg.com/api/guru-project-api/v2/projects/{projectId}"
    dev_support_client_id = "6d914498-1868-429d-84ec-c2f0f5517878"
    scope = "api://27c8245b-ce8d-44e4-949d-3420bb54c908/user_impersonation"
else:
    raise EnvironmentError(
        "Make sure you are using DEV, NONPROD, PROD as environments."
    )

payload = {
  "name": "zzDELETE",
  "description": ""
}

with open('ProjectId.csv', 'r') as csv_file:
   reader = csv.reader(csv_file)
   next(reader)  # Skip header row
   for row in reader:
       rows.append(row[0])
       print(rows)

token = get_new_token(dev_support_client_id, tenant_id, scope)
print(token)
#print(rows)
rows = '11115cf8-29c9-4a7c-9fac-6cbc7ebc17e9'


headers = {
        'Authorization': token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }


for row in rows:
    for projectId in row:
        projectId = '11115cf8-29c9-4a7c-9fac-6cbc7ebc17e9'
        print(projectId)
        endpoint=url.format(projectId = projectId)
        resp =  requests.request("GET", endpoint, headers=headers)
        payload_parse=payload
        name=payload_parse["name"]
        if ( resp and resp.status_code == 200 ) :
            json_response = json.loads(resp.text)
            if len(json_response["name"]) <= 28 : # this number is max project name size - ZZDELETE (8)
                append = "zzDELETE" + json_response["name"]
            else:
                append = "zzDELETE" + json_response["name"][:len(json_response["name"])-8]
            payload["name"] = append
            payload["description"] = json_response['description']
            payload_json = json.dumps(payload)
            print(f"payload2: {payload_json}")
            payload["name"] = ""
            payload["description"] = ""
            response = requests.request("PUT", endpoint, headers=headers, data=payload_json)
            if ( response and response.status_code == 200 ) :
                print("Project Id " + projectId + " has been updated successfully.")
                time.sleep(0.05)
            else:
                print("An error occured while updating Project Id " + projectId + " Exiting ")
                print("Error reason: " + response.reason)
                sys.exit(1)
        else:
            print("An error occured while selecting Project Id " + projectId + " Exiting ")
            print("Error reason: " + resp.reason)
            sys.exit(1)
