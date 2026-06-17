from django.urls import path
from .views import (
    ListCreateOrganizationView,
    RetrieveUpdateOrganizationView,
    InviteMemberView,
    AcceptInvitationView,
    ListMembershipsView,
    UpdateMembershipView,
)

urlpatterns = [
    path('', ListCreateOrganizationView.as_view(), name='organization-list-create'),
    path('<str:org_id>/', RetrieveUpdateOrganizationView.as_view(), name='organization-retrieve-update'),
    path('<str:org_id>/invitations/', InviteMemberView.as_view(), name='invite-member'),
    path('invitations/accept/', AcceptInvitationView.as_view(), name='accept-invitation'),
    path('<str:org_id>/members/', ListMembershipsView.as_view(), name='list-memberships'),
    path('<str:org_id>/members/<str:user_id>/', UpdateMembershipView.as_view(), name='update-membership'),
]