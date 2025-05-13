from rest_framework_simplejwt.tokens import RefreshToken
from .models import Projet, Phase, Operation
from decimal import Decimal
from django.db.models import Sum


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def update_project_costs(project_id):
    """
    Met à jour le coût actuel d'un projet en fonction des coûts de ses phases
    """
    try:
        projet = Projet.objects.get(pk=project_id)
        
        # Calcul du coût total des phases
        cout_phases = projet.phases.aggregate(total=Sum('cout_actuel'))['total'] or Decimal('0.00')
        
        # Mise à jour du coût actuel du projet
        projet.cout_actuel = cout_phases
        projet.save(update_fields=['cout_actuel'])
        
        return True
    except Projet.DoesNotExist:
        return False


def update_phase_costs(phase_id):
    """
    Met à jour le coût actuel d'une phase en fonction des coûts de ses opérations
    """
    try:
        phase = Phase.objects.get(pk=phase_id)
        
        # Calcul du coût total des opérations
        cout_operations = phase.operations.aggregate(total=Sum('cout_reel'))['total'] or Decimal('0.00')
        
        # Mise à jour du coût actuel de la phase
        phase.cout_actuel = cout_operations
        phase.save(update_fields=['cout_actuel'])
        
        # Mise à jour du coût du projet parent
        update_project_costs(phase.projet.id)
        
        return True
    except Phase.DoesNotExist:
        return False


def calculate_project_progress(project_id):
    """
    Calcule la progression globale d'un projet basée sur la progression de ses phases
    """
    try:
        projet = Projet.objects.get(pk=project_id)
        phases = projet.phases.all()
        
        if not phases:
            return 0
        
        total_weight = len(phases)
        progress_sum = sum(phase.progression for phase in phases)
        
        # Calcul de la progression moyenne
        progress = progress_sum / total_weight if total_weight > 0 else 0
        
        return round(progress, 2)
    except Projet.DoesNotExist:
        return 0