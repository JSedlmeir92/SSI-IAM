from django.shortcuts import render, get_object_or_404, redirect
from .models import Credential, Connection
from .forms import CredentialForm, ConnectionForm
from pathlib import Path
import requests
import time
import urllib.request
import os
import base64
import json

url = 'http://0.0.0.0:7080'

def home_view(request):
    return render(request, 'hr_dept/base_hr.html', {'title': 'HR'})

def connection_view(request):
    form = ConnectionForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = ConnectionForm()
    context = {
        'title': 'Establish Connection (HR)',
        'form': form
    }
    if request.method == 'POST':
        # Deleting old INVITATIONS
        connections_invitation = requests.get(url + '/connections?initiator=self&state=invitation').json()['results']
        if len(connections_invitation) > 0:
            connection_id = requests.get(url + '/connections?initiator=self&state=invitation').json()['results'][0]["connection_id"]
            requests.post(url + '/connections/' + connection_id + '/remove')
        # Generating the new INVITATION
        alias = request.POST.get('alias')
        response = requests.post(url + '/connections/create-invitation?alias=' + alias + '&auto_accept=true').json()
        invitation_link = response['invitation_url']
        connection_id = response['connection_id']
        Connection.objects.filter(id=Connection.objects.latest('date_added').id).update(invitation_link=invitation_link)
        Connection.objects.filter(id=Connection.objects.latest('date_added').id).update(connection_id=connection_id)
        # Adding an icon for the Connection
        invitation_splitted = invitation_link.split("=", 1)
        temp = json.loads(base64.b64decode(invitation_splitted[1]))
        temp.update({"imageUrl": "https://raw.githubusercontent.com/Jana-Gl/git-test/master/Icon_HR.png"})
        temp = base64.b64encode(json.dumps(temp).encode("utf-8")).decode("utf-8")
        invitation_splitted[1] = temp
        invitation_link = "=".join(invitation_splitted)
        # Generating the QR code
        qr_code = "https://api.qrserver.com/v1/create-qr-code/?data=" + invitation_link + "&amp;size=600x600"
        context['qr_code'] = qr_code
    return render(request, 'hr_dept/connection.html', context)

def schema_view(request):
    created_schema = requests.get(url + '/schemas/created').json()['schema_ids']
    context = {
        'title': 'Schema'
    }
    if len(created_schema) > 0:
        context['created_schema'] = created_schema[0]
        context['attributes'] = requests.get(url + '/schemas/' + context['created_schema']).json()['schema']['attrNames']
    else:
        pass
    # Publish a new SCHEMA
    if request.method == 'POST':
        schema = {
            "attributes": [
                "Name",
                "Company",
                "Division",
                "Job Title"
            ],
            "schema_name": str(time.time())[:10],
            "schema_version": "1.0"
        }
        requests.post(url + '/schemas', json=schema)
        return redirect('.')
    return render(request, 'hr_dept/schema.html', context)

def cred_def_view(request):
    context = {
        'title': 'Credential Definition'
    }
    # Checks if there are suitable SCHEMAS in the wallet
    created_schema = requests.get(url + '/schemas/created').json()['schema_ids']
    if len(created_schema) < 1:
        context['available_schema'] = 'There is no suitable schema available. Please go back and publish a new one first.'
    else:
        schema_name = requests.get(url + '/schemas/' + created_schema[0]).json()['schema']['name']
        # Checks if there are suitable REVOCABLE CREDENTIAL DEFINITIONS in the wallet
        created_credential_definitions_revocable = requests.get(url + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids']
        if len(created_credential_definitions_revocable) > 0:
            context['created_cred_def_rev'] = created_credential_definitions_revocable[0]
        else:
            # Publish a new CREDENTIAL DEFINITION
            if request.method == 'POST':
                schema_id = created_schema[0]
                credential_definition = {
                    "tag": "Certificate-of-Employment" + f"{round(time.time())}",
                    "support_revocation": True,
                    "schema_id": schema_id
                }
                requests.post(url + '/credential-definitions', json=credential_definition)
                return redirect('.')
    return render(request, 'hr_dept/cred_def.html', context)

def rev_reg_view(request):
    context = {
        'title': 'Revocation Registry'
    }
    # Checks if there are suitable SCHEMA in the wallet
    created_schema = requests.get(url + '/schemas/created').json()['schema_ids']
    if len(created_schema) < 1:
        context['available_schema'] = 'There is no suitable schema & credential definition available. Please go back and publish both first.'
    else:
        # Checks if there are suitable CREDENTIAL DEFINITIONS in the wallet
        schema_name = requests.get(url + '/schemas/' + created_schema[0]).json()['schema']['name']
        created_credential_definitions_revocable = requests.get(url + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids']
        if len(created_credential_definitions_revocable) < 1:
            context['available_cred_def'] = 'There is no suitable credential definition available. Please go back and publish a new one first.'
        else:
            # Checks if there is an active REVOCATION REGISTRY available
            cred_def_id = created_credential_definitions_revocable[0]
            revocation_registry_id = requests.get(url + '/revocation/registries/created?cred_def_id=' + cred_def_id + '&state=active').json()['rev_reg_ids']
            if len(revocation_registry_id) > 0:
                context['rev_reg'] = revocation_registry_id[0]
            else:
                # Publishes a new REVOCATION REGISTRY
                if request.method == 'POST':
                    cred_def_id = created_credential_definitions_revocable[0]
                    registry = {
                        "max_cred_num": 1000,
                        "credential_definition_id": cred_def_id
                    }
                    requests.post(url + '/revocation/create-registry', json=registry)
                    # Commit file to Github
                    if os.path.exists(os.path.join(Path(__file__).resolve().parent.parent, 'git-test')):
                        os.chdir(os.path.join(Path(__file__).resolve().parent.parent, 'git-test'))
                        os.system('git pull "https://github.com/Jana-Gl/git-test.git"')
                    else:
                        os.chdir(Path(__file__).resolve().parent.parent)
                        os.system('git clone https://github.com/Jana-Gl/git-test')
                        os.chdir('git-test')
                    rev_reg = requests.get(url + '/revocation/registries/created?state=generated').json()['rev_reg_ids'][0]
                    link = requests.get(url + '/revocation/registry/' + rev_reg + '/tails-file').url[14:500]
                    filename = str(time.time())[:10]
                    urllib.request.urlretrieve('http://127.0.0.1' + link, filename)
                    os.system('git add ' + filename)
                    os.system('git commit -m "Upload via demo"')
                    os.system('git push https://Jana-Gl:ycRMtJtmmEZNDs3@github.com/Jana-Gl/git-test.git --all')
                    os.chdir('../')
                    tails_public_uri = {
                        "tails_public_uri": "https://github.com/Jana-Gl/git-test/raw/master/" + filename
                    }
                    requests.patch(url + '/revocation/registry/' + rev_reg, json=tails_public_uri)
                    requests.post(url + '/revocation/registry/' + rev_reg + '/publish')
                    return redirect('.')
    return render(request, 'hr_dept/rev_reg.html', context)

def issue_cred_view(request):
    # Updates the STATE of all CONNECTIONS that do not have the state 'active' or 'response'
    update_state = Connection.objects.all()
    for object in update_state:
        connection = requests.get(url + '/connections/' + object.connection_id).status_code
        if connection == 200:
            state = requests.get(url + '/connections/' + object.connection_id).json()['state']
            Connection.objects.filter(id=object.id).update(state=state)
        else:
            Connection.objects.filter(id=object.id).delete()
    form = CredentialForm(request.POST or None)
    context = {
        'title': 'Issue Credential',
        'form': form
    }
    # Checks if there is a suitable SCHEMA
    created_schema = requests.get(url + '/schemas/created').json()['schema_ids']
    if len(created_schema) < 1:
        context['available_schema'] = True
    else:
        # Checks if there is a suitable CREDENTIAL DEFINITION
        schema_name = requests.get(url + '/schemas/' + created_schema[0]).json()['schema']['name']
        created_credential_definitions_revocable = requests.get(url + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids']
        if len(created_credential_definitions_revocable) < 1:
            context['available_cred_def'] = True
        else:
            # Checks if there is a suitable REVOCATION REGISTRY
            cred_def_id = created_credential_definitions_revocable[0]
            revocation_registry_id = requests.get(url + '/revocation/registries/created?cred_def_id=' + cred_def_id + '&state=active').json()['rev_reg_ids']
            if len(revocation_registry_id) < 1:
                context['rev_reg'] = True
            else:
                if form.is_valid():
                    # Saving the data in the database
                    form.save()
                    form = CredentialForm()
                    # Sending the data to the employee
                    schema = requests.get(url + '/schemas/' + created_schema[0]).json()['schema']
                    schema_name = schema['name']
                    schema_id = schema['id']
                    schema_version = schema['version']
                    schema_issuer_did = requests.get(url + '/wallet/did/public').json()['result']['did']
                    credential_definition_id = requests.get(url + '/credential-definitions/created?schema_name=' + schema_name).json()['credential_definition_ids'][0]
                    rev_reg_id = requests.get(url + '/revocation/registries/created?cred_def_id=' + credential_definition_id + '&state=active').json()['rev_reg_ids'][0]
                    issuer_did = requests.get(url + '/wallet/did/public').json()['result']['did']
                    connection_id = request.POST.get('connection_id')
                    credential = {
                        "schema_name": schema_name,
                        "auto_remove": True,
                        "revoc_reg_id": rev_reg_id,
                        "schema_issuer_did": schema_issuer_did,
                        "schema_version": schema_version,
                        "schema_id": schema_id,
                        "credential_proposal": {
                            "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",
                            "attributes": [
                                {
                                    "name": "Name",
                                    "value": request.POST.get('fullname')
                                },
                                {
                                    "name": "Company",
                                    "value": request.POST.get('company')
                                },
                                {
                                    "name": "Division",
                                    "value": request.POST.get('division')
                                },
                                {
                                    "name": "Job Title",
                                    "value": request.POST.get('jobtitle')
                                }
                            ]
                        },
                        "credential_def_id": credential_definition_id,
                        "issuer_did": issuer_did,
                        "connection_id": connection_id,
                        "trace": False
                    }
                    issue_cred = requests.post(url + '/issue-credential/send', json=credential)
                    # Updating the object in the database with the thread-id
                    thread_id = issue_cred.json()['credential_offer_dict']['@id']
                    Credential.objects.filter(id=Credential.objects.latest('date_added').id).update(thread_id=thread_id)
                    context['form'] = form
                    context['name'] = request.POST.get('fullname')
    return render(request, 'hr_dept/issue_cred.html', context)

def revoke_cred_view(request):
    # Updates all issued Credentials
    update_credential = Credential.objects.all()
    for object in update_credential:
        credential = requests.get(url + '/issue-credential/records?thread_id=' + str(object.thread_id)).json()['results']
        if len(credential) < 1:
            Credential.objects.filter(id=object.id).delete()
        else:
            if object.state == "credential_issued":
                pass
            else:
                state = credential[0]['state']
                Credential.objects.filter(id=object.id).update(state=state)
    queryset = Credential.objects.filter(revoked=False, state__contains="credential_issued").order_by('-id')
    context = {
        'title': 'Revoke Credential',
        'object_list': queryset,
        'len': len(queryset)
    }
    return render(request, 'hr_dept/revoke_cred.html', context)

def cred_detail_view(request, id):
    obj = get_object_or_404(Credential, id=id)
    if obj.rev_id == None:
        credential = requests.get(url + '/issue-credential/records?thread_id=' + obj.thread_id).json()['results'][0]
        state = credential['state']
        if state == 'credential_issued':
            rev_id = credential['revocation_id']
            obj.rev_id = rev_id
    if request.method == 'POST':
        rev_reg_id = requests.get(url + '/revocation/registries/created?state=active').json()['rev_reg_ids'][0]
        requests.post(url + '/issue-credential/revoke?cred_rev_id=' + obj.rev_id + '&rev_reg_id=' + rev_reg_id + '&publish=true')
        obj.revoked = True
        obj.save()
        return redirect('.')
    context = {
        'title': 'Credential Detail',
        'object': obj
    }
    return render(request, 'hr_dept/cred_detail.html', context)
