from winsdk.windows.ui.notifications.management import UserNotificationListener, UserNotificationListenerAccessStatus
# from winsdk.windows.ui.notifications import NotificationKinds, KnownNotificationBindings

def handler(listener, event):
    notification = listener.get_notification(event.user_notification_id)

    # get some app info if available
    if hasattr(notification, "app_info"):
        print("App Name: ", notification.app_info.display_info.display_name)

def main():
    
    listener = UserNotificationListener.current
    accessStatus = listener.request_access_async()

    if accessStatus != UserNotificationListenerAccessStatus.ALLOWED:
        print("Access to UserNotificationListener is not allowed.")
        exit()


    listener.add_notification_changed(handler)   

if __name__ == "__main__":
    main()