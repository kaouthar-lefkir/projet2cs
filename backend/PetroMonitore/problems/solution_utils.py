from django.utils import timezone
from ..models import Solution

def get_solution_statistics(probleme_id=None, projet_id=None):
    """
    Retourne des statistiques sur les solutions
    
    Args:
        probleme_id (int, optional): ID du problème pour filtrer
        projet_id (int, optional): ID du projet pour filtrer
        
    Returns:
        dict: Statistiques des solutions
    """
    from django.db.models import Count, Avg, Min, Max
    
    # Construire le filtre de base
    filter_kwargs = {}
    if probleme_id:
        filter_kwargs['probleme_id'] = probleme_id
    if projet_id:
        filter_kwargs['probleme__projet_id'] = projet_id
    
    # Récupérer les données
    solutions = Solution.objects.filter(**filter_kwargs)
    
    # Compter par statut
    statut_counts = solutions.values('statut').annotate(count=Count('id'))
    status_stats = {item['statut']: item['count'] for item in statut_counts}
    
    # Statistiques sur les coûts estimés
    cout_stats = solutions.aggregate(
        cout_moyen=Avg('cout_estime'),
        cout_min=Min('cout_estime'),
        cout_max=Max('cout_estime')
    )
    
    # Statistiques sur les délais estimés
    delai_stats = solutions.aggregate(
        delai_moyen=Avg('delai_estime'),
        delai_min=Min('delai_estime'),
        delai_max=Max('delai_estime')
    )
    
    # Compter le total
    total = solutions.count()
    
    # Calculer les pourcentages de validation et mise en œuvre
    validees = status_stats.get('VALIDEE', 0) + status_stats.get('MISE_EN_OEUVRE', 0)
    taux_validation = (validees / total * 100) if total > 0 else 0
    
    en_oeuvre = status_stats.get('MISE_EN_OEUVRE', 0)
    taux_mise_en_oeuvre = (en_oeuvre / validees * 100) if validees > 0 else 0
    
    return {
        'total': total,
        'par_statut': status_stats,
        'cout': cout_stats,
        'delai': delai_stats,
        'taux_validation': round(taux_validation, 2),
        'taux_mise_en_oeuvre': round(taux_mise_en_oeuvre, 2)
    }

def get_solutions_to_implement(projet_id=None):
    """
    Retourne les solutions validées mais non encore mises en œuvre
    
    Args:
        projet_id (int, optional): ID du projet pour filtrer
        
    Returns:
        QuerySet: Solutions validées à mettre en œuvre
    """
    filter_kwargs = {
        'statut': 'VALIDEE'
    }
    
    if projet_id:
        filter_kwargs['probleme__projet_id'] = projet_id
    
    return Solution.objects.filter(**filter_kwargs)