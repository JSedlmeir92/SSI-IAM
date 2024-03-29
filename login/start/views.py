from django.shortcuts import render, redirect

import requests

url2 = 'http://0.0.0.0:9080'

def remove_connections_agent_2():
    connections = requests.get(url2 + '/connections').json()['results']
    y = len(connections)
    while y > 0:
        connection_id = connections[y-1]["connection_id"]
        requests.post(url2 + '/connections/' + connection_id + '/remove')
        y -= 1

def remove_credentials_agent_2():
    issue_credential = requests.get(url2 + '/issue-credential/records').json()['results']
    y = len(issue_credential)
    while y > 0:
        credential_exchange_id = issue_credential[y-1]['credential_exchange_id']
        requests.post(url2 + '/issue-credential/records/' + credential_exchange_id + '/remove')
        y -= 1

def remove_proofs_agent_2():
    proof_records = requests.get(url2 + '/present-proof/records').json()['results']
    y = len(proof_records)
    while y > 0:
        presentation_exchange_id = proof_records[y-1]['presentation_exchange_id']
        requests.post(url2 + '/present-proof/records/' + presentation_exchange_id + '/remove')
        y -= 1

def home_view(request):
    context = {
        'title': 'Start'
    }
    return render(request, 'start/start-home.html', context)

def manage_agent_view(request):
    context = {
        'title': 'Manage Agents',
        'connections_quantity2'     : len(requests.get(url2 + '/connections').json()['results']) - len(requests.get(url2 + '/connections?state=invitation').json()['results']),
        'credential_quantity2'      : len(requests.get(url2 + '/issue-credential/records').json()['results']),
        'proof_quantity2'           : len(requests.get(url2 + '/present-proof/records').json()['results']),
        'connections_invitation2'   : len(requests.get(url2 + '/connections?state=invitation').json()['results'])
    }
    return render(request, 'start/manage_agent.html', context)

def remove_connection_2(request):
    remove_connections_agent_2()
    return redirect('..')

def remove_credential_2(request):
    remove_credentials_agent_2()
    return redirect('..')

def remove_proof_2(request):
    remove_proofs_agent_2()
    return redirect('..')

def remove_invitation_2(request):
    connections_invitation = requests.get(url2 + '/connections?initiator=self&state=invitation').json()['results']
    if len(connections_invitation) > 0:
        connection_id = requests.get(url2 + '/connections?initiator=self&state=invitation').json()['results'][0]["connection_id"]
        requests.post(url2 + '/connections/' + connection_id + '/remove')
    else:
        pass
    return redirect('..')

def reset_agent(request):
    # Deleting all PROOFS of Agent 2 (IAM)
    remove_proofs_agent_2()
    # Deleting all CREDENTIALS of Agent 2 (IAM)
    remove_credentials_agent_2()
    # Deleting all CONNECTIONS & INVITATIONS of Agent 2 (IAM)
    remove_connections_agent_2()
    return redirect('.')
