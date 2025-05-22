from rest_framework.permissions import BasePermission
from rest_framework import permissions


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'TOP_MANAGEMENT'

class IsIngenieurTerrain(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'INGENIEUR_TERRAIN'

class IsExpert(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'EXPERT'
    
    
class IsProjectResponsible(permissions.BasePermission):
    """
    Permission pour n'autoriser que le responsable du projet ou le TOP_MANAGEMENT
    """
    def has_object_permission(self, request, view, obj):
        # TOP_MANAGEMENT a toujours accès
        if request.user.role == 'TOP_MANAGEMENT':
            return True
        
        # Le responsable du projet a accès
        return request.user == obj.responsable