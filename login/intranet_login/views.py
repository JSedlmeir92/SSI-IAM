from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import requests
import time
import datetime
import os
import json
import base64

url = 'http://0.0.0.0:7080'
url2 = 'http://0.0.0.0:9080'

def home_view(request):
    return render(request, 'intranet_login/base_work.html', {'title': 'Work'})

@csrf_exempt
def login_view(request):
    context = {
        'title': 'Login',
    }
    # If an INVITATION is created for a new user, a new session is created and all proof presentations are removed.
    if request.method == 'POST' and 'submit_new_invitation' in request.POST:
        session_key = request.session.session_key
        connections = requests.get(url2 + '/connections?alias=' + session_key + '&state=active').json()['results']
        if len(connections) > 0:
            connection_id = connections[0]['connection_id']
            proof = requests.get(url2 + '/present-proof/records?connection_id=' + connection_id).json()['results']
            if len(proof) > 0:
                pres_ex_id = proof[0]['presentation_exchange_id']
                requests.delete(url2 + '/present-proof/records/' + pres_ex_id)
            else:
                pass
            requests.delete(url2 + '/connections/' + connection_id)
            request.session.flush()
            request.session.save()
        else:
            pass
        return redirect('work-login')
    # In case the session key is None, the session is stored to get a key
    if not request.session.session_key:
        request.session.save()
    # Checks if there is a CONNECTION with the current session key and a verified proof
    session_key = request.session.session_key
    connections_active = requests.get(url2 + '/connections?alias=' + session_key + '&state=active').json()['results']
    if len(connections_active) > 0:
        connection_id = connections_active[0]['connection_id']
        proof = requests.get(url2 + '/present-proof/records?connection_id=' + connection_id + '&state=verified').json()['results']
        if (len(proof) > 0):
            name = proof[0]['presentation']['requested_proof']['revealed_attr_groups']['employee_credential']['values']['Name']['raw']
            context['name'] = name
        else:
            pass
    else:
        connections_response = requests.get(url2 + '/connections?alias=' + session_key + '&state=response').json()['results']
        if len(connections_response) > 0:
            connection_id = connections_response[0]['connection_id']
            requests.delete(url2 + '/connections/' + connection_id)
        else:
            pass
        # Checks if it is necessary to create a new INVITATION QR Code and creates one if necessary
        invitations = requests.get(url2 + '/connections?alias=' + session_key + '&state=invitation').json()['results']
        # Creates a new INVITATION, if none exists
        if len(invitations) == 0:
            invitation_link = requests.post(url2 + '/connections/create-invitation?alias=' + session_key + '&auto_accept=true').json()['invitation_url']
            FileHandler = open("connection_iam.txt", "w")
            FileHandler.write(invitation_link)
        # Creates a new INVITATION, if the file does not exist or is empty
        elif os.stat("connection_iam.txt").st_size == 0:
            # Delete old INVITATION
            connection_id = invitations[0]["connection_id"]
            requests.delete(url2 + '/connections/' + connection_id)
            # Create new INVITATION
            invitation_link = requests.post(url2 + '/connections/create-invitation?alias=' + session_key + '&auto_accept=true').json()['invitation_url']
            FileHandler = open("connection_iam.txt", "w")
            FileHandler.write(invitation_link)
        # Uses the latest created INVITATION, if it has not been used yet
        else:
            FileHandler = open("connection_iam.txt", "r")
            invitation_link = FileHandler.read()
        FileHandler.close()
        # Adding an icon for the Connection
        invitation_splitted = invitation_link.split("=", 1)
        temp = json.loads(base64.b64decode(invitation_splitted[1]))
        temp.update({"imageUrl": "https://raw.githubusercontent.com/Jana-Gl/git-test/master/Icon_Login.png"})
        temp = base64.b64encode(json.dumps(temp).encode("utf-8")).decode("utf-8")
        invitation_splitted[1] = temp
        invitation_link = "=".join(invitation_splitted)
        qr_code = "https://api.qrserver.com/v1/create-qr-code/?data=" + invitation_link + "&amp;size=600x600"
        context['qr_code'] = qr_code
    return render(request, 'intranet_login/login.html', context)

def login_loading_view(request):
    # Gets the CONNECTION ID (to which the proof should be sent)
    session_key = request.session.session_key
    connection_id = requests.get(url2 + '/connections?alias=' + session_key + '&state=active').json()['results'][0]['connection_id']
    # Deletes old PROOF requests & presentations
    proof = requests.get(url2 + '/present-proof/records?connection_id=' + connection_id).json()['results']
    if len(proof) > 0:
        pres_ex_id = proof[0]['presentation_exchange_id']
        requests.delete(url2 + '/present-proof/records/' + pres_ex_id)
    # Gets the CREDENTIAL DEFINITION ID for the proof of a REVOCABLE credential
    created_schema = requests.get(url + '/schemas/created').json()['schema_ids']
    schema_name = requests.get(url + '/schemas/' + created_schema[0]).json()['schema']['name']
    cred_def_id = requests.get(url + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids'][0]
    # Creates the PROOF REQUEST
    proof_request = {
        "connection_id": connection_id,
        "proof_request": {
            "name": "Proof of Division",
            "version": "1.0",
            "requested_attributes": {
                "employee_credential": {
                    "names": ["Name",
                              "Company",
                              "Division"
                              ],
                    "non_revoked": {
                        "from": 0,
                        "to": round(time.time())
                    },
                    "restrictions": [
                        {
                            "cred_def_id": cred_def_id
                        }
                    ]
                }
            },
            "requested_predicates": {}
        }
    }
    requests.post(url2 + '/present-proof/send-request', json=proof_request)
    context = {
        'title': 'Waiting for Proof Presentation',
    }
    return render(request, 'intranet_login/login-loading.html', context)

def login_loading_view2(request):
    session_key = request.session.session_key
    x = 0
    while len(requests.get(url2 + '/connections?alias=' + session_key + '&state=response').json()['results']) == 0:
        time.sleep(5)
        # redirect to the login page after 2 minutes of not receiving a proof presentation
        x += 1
        if x > 23:
            return redirect('work-login')
    else:
        context = {
            'title': 'Waiting for Proof Presentation',
        }
        return render(request, 'intranet_login/login-loading.html', context)

def login_result_view(request):
    session_key = request.session.session_key
    connection_id = requests.get(url2 + '/connections?alias=' + session_key).json()['results'][0]['connection_id']
    x = 0
    while len(requests.get(url2 + '/present-proof/records?connection_id=' + connection_id + '&state=verified').json()['results']) == 0:
        time.sleep(5)
        # redirect to the login page after 2 minutes of not receiving a proof presentation
        x += 1
        if x > 23:
            return redirect('work-login')
    else:
        proof = requests.get(url2 + '/present-proof/records?connection_id=' + connection_id + '&state=verified').json()['results'][0]
        verified = proof['verified']
        context = {
            'title': 'Log In Success',
            'verified': verified
        }
        presentation_exchange_id = proof['presentation_exchange_id']
        # try:
            # state = requests.delete(url2 + '/present-proof/records/' + presentation_exchange_id)
        # except:
            # print("Nothing to delete")

        return render(request, 'intranet_login/login-result.html', context)

def logged_in_view(request):
    if request.method == 'POST':
        proof_records = requests.get(url2 + '/present-proof/records').json()['results']
        x = len(proof_records)
        while x > 0:
            pres_ex_id = proof_records[x - 1]['presentation_exchange_id']
            requests.delete(url2 + '/present-proof/records/' + pres_ex_id)
            x -= 1
        return redirect('work-login')
    session_key = request.session.session_key
    connection_id = requests.get(url2 + '/connections?alias=' + session_key).json()['results'][0]['connection_id']
    proof = requests.get(url2 + '/present-proof/records?connection_id=' + connection_id + '&state=verified').json()['results']
    if len(proof) > 0:
        name = proof[0]['presentation']['requested_proof']['revealed_attr_groups']['employee_credential']['values']['Name']['raw']
        context = {
            'title': 'Logged in',
            'name': name,
            'date': datetime.date.today().strftime('%d - %b - %Y')
        }
        return render(request, 'intranet_login/logged_in.html', context)
    else:
        return redirect('work-login')

@require_POST
@csrf_exempt
def webhook_connection_view(request):
    json_body = json.loads(request.body)
    state = json_body['state']
    if state == 'response':
        connection_id = json_body['connection_id']
        # Deletes old PROOF requests & presentations
        proof = requests.get(url2 + '/present-proof/records?connection_id=' + connection_id).json()['results']
        if len(proof) > 0:
            pres_ex_id = proof[0]['presentation_exchange_id']
            requests.delete(url2 + '/present-proof/records/' + pres_ex_id)
        # Gets the CREDENTIAL DEFINITION ID for the proof of a REVOCABLE credential
        created_schema = requests.get(url + '/schemas/created').json()['schema_ids']
        schema_name = requests.get(url + '/schemas/' + created_schema[0]).json()['schema']['name']
        cred_def_id = requests.get(url + '/credential-definitions/created?schema_name=' + schema_name).json()[
            'credential_definition_ids'][0]
        # Creates the PROOF REQUEST
        proof_request = {
            "connection_id": connection_id,
            "proof_request": {
                "name": "Proof of Division",
                "version": "1.0",
                "requested_attributes": {
                    "employee_credential": {
                        "names": [
                            "Name",
                            "Company",
                            "Division"
                        ],
                        "non_revoked": {
                            "from": 0,
                            "to": round(time.time())
                        },
                        "restrictions": [
                            {
                                "cred_def_id": cred_def_id
                            }
                        ]
                    }
                },
                "requested_predicates": {}
            }
        }
        requests.post(url2 + '/present-proof/send-request', json=proof_request)
    else:
        pass
    return HttpResponse()

@require_POST
@csrf_exempt
def webhook_proof_view(request):
    return HttpResponse()