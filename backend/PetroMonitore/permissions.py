from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'TOP_MANAGEMENT'

class IsIngenieurTerrain(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'INGENIEUR_TERRAIN'

class IsExpert(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'EXPERT'