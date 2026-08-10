from services.reminder_service import send_monthly_reminders

print("=" * 60)
print("Running EMI Reminder Job")
print("=" * 60)

send_monthly_reminders()

print("=" * 60)
print("Reminder Job Completed")
print("=" * 60)