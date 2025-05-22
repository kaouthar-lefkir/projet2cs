from django.apps import AppConfig


class PetromonitoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "PetroMonitore"
    
    
    def ready(self):
        # Force l'import de tasks au démarrage de Django
        import PetroMonitore.alerts.tasks
