from windows_toasts import Toast, WindowsToaster

print("🔔  start Notification test...")

toaster = WindowsToaster("Alzheimer Voice Assistant")

toast = Toast()

toast.text_fields = [
    "Alzheimer Voice Assistant",
    "🔔 Reminder Test",
    "this notification working properly!"
]

toaster.show_toast(toast)

print("✅ Notification test sent!")