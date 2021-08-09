from django.shortcuts import render, redirect
from hr_dept.models import Connection, Credential

import requests

url = 'http://0.0.0.0:7080'

def remove_connections_agent_1():
    Connection.objects.all().delete()
    connections = requests.get(url + '/connections').json()['results']
    x = len(connections)
    while x > 0:
        connection_id = connections[x-1]["connection_id"]
        requests.post(url + '/connections/' + connection_id + '/remove')
        x -= 1

def remove_credentials_agent_1():
    Credential.objects.all().delete()
    issue_credential = requests.get(url + '/issue-credential/records').json()['results']
    x = len(issue_credential)
    while x > 0:
        credential_exchange_id = issue_credential[x-1]['credential_exchange_id']
        requests.post(url + '/issue-credential/records/' + credential_exchange_id + '/remove')
        x -= 1

def remove_proofs_agent_1():
    proof_records = requests.get(url + '/present-proof/records').json()['results']
    x = len(proof_records)
    while x > 0:
        presentation_exchange_id = proof_records[x-1]['presentation_exchange_id']
        requests.post(url + '/present-proof/records/' + presentation_exchange_id + '/remove')
        x -= 1

def home_view(request):
    context = {
        'title': 'Start'
    }
    return render(request, 'start/start-home.html', context)

def manage_agent_view(request):
    context = {
        'title': 'Manage Agents',
        'connections_quantity'      : len(requests.get(url + '/connections').json()['results']) - len(requests.get(url + '/connections?state=invitation').json()['results']),
        'credential_quantity'       : len(requests.get(url + '/issue-credential/records').json()['results']),
        'proof_quantity'            : len(requests.get(url + '/present-proof/records').json()['results']),
        'connections_invitation'    : len(requests.get(url + '/connections?state=invitation').json()['results'])
    }
    return render(request, 'start/manage_agent.html', context)

def remove_connection_1(request):
    remove_connections_agent_1()
    return redirect('..')

def remove_credential_1(request):
    remove_credentials_agent_1()
    return redirect('..')

def remove_proof_1(request):
    remove_proofs_agent_1()
    return redirect('..')

def remove_invitation_1(request):
    Connection.objects.filter(state='invitation').delete()
    connections_invitation = requests.get(url + '/connections?initiator=self&state=invitation').json()['results']
    if len(connections_invitation) > 0:
        connection_id = requests.get(url + '/connections?initiator=self&state=invitation').json()['results'][0]["connection_id"]
        requests.post(url + '/connections/' + connection_id + '/remove')
    else:
        pass
    return redirect('..')

def reset_agent(request):
    # Deleting all PROOFS of Agent 1 (HR)
    remove_proofs_agent_1()
    # Deleting all CREDENTIALS of Agent 1 (HR)
    remove_credentials_agent_1()
    # Deleting all CONNECTIONS & INVITATIONS of Agent 1 (HR)
    remove_connections_agent_1()
    return redirect('.')
