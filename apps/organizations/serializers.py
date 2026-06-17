from rest_framework import serializers
from .models import Organization, Membership, Invitation


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'slug', 'logo_url', 'plan', 'created_at', 'updated_at']


class OrgCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['name']
    
    def create(self, validated_data):
        user = self.context['request'].user
        organization = Organization.objects.create(owner=user, **validated_data)
        Membership.objects.create(organization=organization, user=user, role='owner')
        return organization


class OrgUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['name', 'logo_url']


class InviteMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ['email', 'role']


class AcceptInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ['token']


class UpdateMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ['role']


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ['user_id', 'organization_id', 'role', 'created_at', 'updated_at']