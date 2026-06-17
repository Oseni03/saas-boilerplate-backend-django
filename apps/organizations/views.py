from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Organization, Membership, Invitation
from .serializers import (
    OrganizationSerializer, 
    OrgCreateSerializer, 
    OrgUpdateSerializer, 
    InviteMemberSerializer, 
    AcceptInvitationSerializer, 
    UpdateMembershipSerializer, 
    MembershipSerializer
)
from django.core.mail import send_mail
from django.utils.crypto import get_random_string


# Create your views here.
class ListCreateOrganizationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organizations = Organization.objects.filter(memberships__user=request.user)
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrgCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            organization = serializer.save()
            return Response(OrganizationSerializer(organization).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RetrieveUpdateOrganizationView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, org_id):
        try:
            return Organization.objects.get(id=org_id, memberships__user=self.request.user)
        except Organization.DoesNotExist:
            return None

    def get(self, request, org_id):
        organization = self.get_object(org_id)
        if not organization:
            return Response({'detail': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrganizationSerializer(organization)
        return Response(serializer.data)

    def patch(self, request, org_id):
        organization = self.get_object(org_id)
        if not organization:
            return Response({'detail': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrgUpdateSerializer(organization, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(OrganizationSerializer(organization).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, org_id):
        organization = self.get_object(org_id)
        if not organization:
            return Response({'detail': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
        organization.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InviteMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, org_id):
        try:
            organization = Organization.objects.get(id=org_id, memberships__user=request.user, memberships__role__in=['owner', 'admin'])
        except Organization.DoesNotExist:
            return Response({'detail': 'Organization not found or insufficient permissions'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = InviteMemberSerializer(data=request.data)
        if serializer.is_valid():
            invitation = serializer.save(organization=organization)
            send_mail(
                subject=f"Invitation to join {organization.name}",
                message=f"You have been invited to join the organization '{organization.name}' as a {invitation.role}. Use the following token to accept the invitation: {invitation.token}",
                from_email="noreply@yourapp.com",
                recipient_list=[invitation.email]
            )
            return Response({'detail': f'Invitation sent to {invitation.email}'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AcceptInvitationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AcceptInvitationSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            try:
                invitation = Invitation.objects.get(token=token, accepted=False)
            except Invitation.DoesNotExist:
                return Response({'detail': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
            
            invitation.accepted = True
            invitation.save()
            Membership.objects.create(
                organization=invitation.organization,
                user=request.user,
                role=invitation.role
            )
            return Response({'detail': f'You have joined the organization {invitation.organization.name} as a {invitation.role}'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListMembershipsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, org_id):
        try:
            organization = Organization.objects.get(id=org_id, memberships__user=request.user)
        except Organization.DoesNotExist:
            return Response({'detail': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
        
        memberships = Membership.objects.filter(organization=organization)
        serializer = MembershipSerializer(memberships, many=True)
        return Response(serializer.data)


class UpdateMembershipView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, org_id, user_id):
        try:
            membership = Membership.objects.get(organization__id=org_id, user__id=user_id, organization__memberships__user=request.user, organization__memberships__role__in=['owner', 'admin'])
        except Membership.DoesNotExist:
            return Response({'detail': 'Membership not found or insufficient permissions'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UpdateMembershipSerializer(membership, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(MembershipSerializer(membership).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, org_id, user_id):
        try:
            membership = Membership.objects.get(organization__id=org_id, user__id=user_id, organization__memberships__user=request.user, organization__memberships__role__in=['owner', 'admin'])
        except Membership.DoesNotExist:
            return Response({'detail': 'Membership not found or insufficient permissions'}, status=status.HTTP_404_NOT_FOUND)
        
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
