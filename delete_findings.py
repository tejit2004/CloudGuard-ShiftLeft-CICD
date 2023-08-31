# Script for deleting all code-scanning findings from a github repo.
# It's completely indiscriminate so only use this on a repo dedicated to testing or 
# you absolutely don't care about deleting all of the code scanning findings!

import requests
import json
import os
import sys
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
                    
# Github access variables
GH_API_HOST = "https://api.github.com/"
GH_REPO_USER = "chkp-stuartgreen" # This should be your github username
GH_REPO = "CloudGuard-ShiftLeft-CICD" # Github repository name
GH_GET_URL_BASE = f'{GH_API_HOST}repos/{GH_REPO_USER}/{GH_REPO}/'
GH_GET_FINDINGS_URL = f'{GH_GET_URL_BASE}code-scanning/analyses'

if 'GH_PAT' not in os.environ:
  logging.error("Please set GH_PAT with your Github personal access token for the repo you're accessing")
  sys.exit(1)

GH_USER_PAT = os.environ['GH_PAT']


# Get code scanning analyses
payload = {}
headers = {
  'Authorization': 'Bearer ' + GH_USER_PAT
}

response = requests.request('GET', GH_GET_FINDINGS_URL, headers=headers, data=payload)
if response.status_code != 200:
    logging.error("The call to Github returned an unexpected status code")
    logging.error(f'Status code: {response.status_code}')
    logging.error(f'{response.text}')
    sys.exit(1)

findings_json = json.loads(response.text)

deletable_findings = [ item for item in findings_json if 'deletable' in item and item['deletable'] == True ]
while len(deletable_findings) > 0:
  for item in deletable_findings:
      response = requests.request('DELETE', item['url']+"?confirm_delete", headers=headers, data=payload)
      if response.status_code != 200:
          logging.warning(f'Did not receive a 200 status for deleting finding {item["id"]}')
          logging.warning(f'Response Code: {response.status_code}')
          logging.warning(f'Response: {response.text}')
      response_json = json.loads(response.text)
      # We don't need the below section, we can just provide delete confirmation on all requests.
      #while 'confirm_delete_url' in response_json and response_json['confirm_delete_url'] != None :
      #    response = requests.request('DELETE', response_json['confirm_delete_url'], headers=headers, data=payload)
      #    if response.status_code != 200:
      #      logging.warning(f'Did not receive a 200 status for deleting nested finding')
      #    response_json = json.loads(response.text)
  response = requests.request('GET', GH_GET_FINDINGS_URL, headers=headers, data=payload)
  findings_json = json.loads(response.text)
  deletable_findings = [ item for item in findings_json if 'deletable' in item and item['deletable'] == True ]

