# backend/celery.py
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Periodic tasks configuration
app.conf.beat_schedule = {
    # Détecter les alertes toutes les 30 minutes
    'detecter-alertes-periodique': {
        'task': 'PetroMonitore.alerts.tasks.detecter_alertes_periodique',
        'schedule': 30.0 * 60,  # 30 minutes
    },
    
    # Envoyer un résumé quotidien à 8h00
    'resume-alertes-quotidien': {
        'task': 'PetroMonitore.alerts.tasks.envoyer_resume_alertes_quotidien',
        'schedule': crontab(hour=8, minute=0),
    },
    
    # Nettoyer les anciennes alertes chaque dimanche à 2h00
    'nettoyer-alertes': {
        'task': 'PetroMonitore.alerts.tasks.nettoyer_alertes_periodique',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),
    },
    
    # Générer un rapport hebdomadaire chaque lundi à 9h00
    'rapport-hebdomadaire': {
        'task': 'PetroMonitore.alerts.tasks.generer_rapport_hebdomadaire',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')