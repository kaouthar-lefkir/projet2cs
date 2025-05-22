# check_alerts_status.py - Run this to check alert system status
import os
import django
import sys
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from PetroMonitore.models import Alerte, Projet, Operation
from django.utils import timezone

def check_alert_system_status():
    """Check the status of the alert system"""
    
    print("🔍 PetroMonitore Alert System Status Check")
    print("=" * 50)
    
    # 1. Database Connection
    try:
        total_alerts = Alerte.objects.count()
        print(f"✅ Database Connected - {total_alerts} total alerts")
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return
    
    # 2. Recent Alerts (last 24 hours)
    yesterday = timezone.now() - timedelta(days=1)
    recent_alerts = Alerte.objects.filter(date_alerte__gte=yesterday)
    print(f"📅 Recent Alerts (24h): {recent_alerts.count()}")
    
    # 3. Alert Levels Distribution
    for niveau in ['CRITIQUE', 'WARNING', 'INFO']:
        count = Alerte.objects.filter(niveau=niveau).count()
        emoji = '🔴' if niveau == 'CRITIQUE' else '🟡' if niveau == 'WARNING' else '🔵'
        print(f"{emoji} {niveau}: {count}")
    
    # 4. Unread Alerts
    unread_count = Alerte.objects.filter(statut='NON_LU').count()
    critical_unread = Alerte.objects.filter(statut='NON_LU', niveau='CRITIQUE').count()
    print(f"📬 Unread Alerts: {unread_count} (Critical: {critical_unread})")
    
    # 5. Active Projects that might trigger alerts
    active_projects = Projet.objects.filter(statut__in=['EN_COURS', 'PLANIFIE'])
    projects_over_budget = 0
    projects_overdue = 0
    
    for project in active_projects:
        if (project.budget_initial and project.cout_actuel and 
            project.cout_actuel > project.budget_initial * 0.8):
            projects_over_budget += 1
        
        if project.date_fin_prevue and timezone.now().date() > project.date_fin_prevue:
            projects_overdue += 1
    
    print(f"🏗️  Active Projects: {active_projects.count()}")
    print(f"💰 Over Budget: {projects_over_budget}")
    print(f"⏰ Overdue: {projects_overdue}")
    
    # 6. Recent Alert Types
    print("\n📊 Recent Alert Types:")
    recent_types = recent_alerts.values_list('type_alerte', flat=True)
    for alert_type in set(recent_types):
        count = recent_types.filter(type_alerte=alert_type).count()
        print(f"   • {alert_type}: {count}")
    
    # 7. System Health Recommendations
    print("\n💡 Recommendations:")
    if critical_unread > 0:
        print(f"   ⚠️  {critical_unread} critical alerts need immediate attention!")
    if projects_over_budget > 0:
        print(f"   💸 {projects_over_budget} projects are over budget threshold")
    if projects_overdue > 0:
        print(f"   📅 {projects_overdue} projects are overdue")
    
    if critical_unread == 0 and projects_over_budget == 0 and projects_overdue == 0:
        print("   ✅ System is healthy - no critical issues detected")

def trigger_manual_detection():
    """Manually trigger alert detection"""
    print("\n🔄 Triggering manual alert detection...")
    
    try:
        from PetroMonitore.alerts.utils import detecter_toutes_alertes
        nouvelles_alertes = detecter_toutes_alertes()
        print(f"✅ Detection completed: {len(nouvelles_alertes)} new alerts created")
        
        for alerte in nouvelles_alertes:
            print(f"   • {alerte.niveau}: {alerte.type_alerte} - {alerte.message[:50]}...")
            
    except Exception as e:
        print(f"❌ Detection failed: {e}")

if __name__ == "__main__":
    check_alert_system_status()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--detect":
        trigger_manual_detection()
    else:
        print(f"\n💡 To manually trigger alert detection, run:")
        print(f"   python check_alerts_status.py --detect")