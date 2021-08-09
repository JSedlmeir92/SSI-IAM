from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='start-home'),
    # manage agent
    path('manage_agent/', views.manage_agent_view, name='manage_agent-home'),
    # manage established connections & invitations
    path('manage_agent/connection-1/', views.remove_connection_1, name='manage_agent_1-remove_connection'),
    # manage issued credentials
    path('manage_agent/credential-1/', views.remove_credential_1, name='manage_agent_1-remove_credential'),
    # manage received proofs
    path('manage_agent/proof-1/', views.remove_proof_1, name='manage_agent_1-remove_proof'),
    # manage invitations
    path('manage_agent/invitation-1/', views.remove_invitation_1, name='manage_agent_1-remove_invitation'),
    # reset both agents
    path('manage_agent/reset', views.reset_agent, name='manage_agent-reset')
]