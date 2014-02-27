import time

class NotificationSystem(object):
    """Manage notification queue and processing"""
    def __init__(self):
        self._notification_queue = []
        self._notification_map = {"*":[]}
        
    def register(self, processor, *notification_types):
        """Register processor as a handler for notifications of any type listed in notification_types"""
        for notification_type in notification_types:
            if notification_type not in self._notification_map:
                self._notification_map[notification_type] = []
            if processor not in self._notification_map[notification_type]:
                self._notification_map[notification_type].append(processor)
                
    def unregister(self, processor, *notification_types):
        """Unregister processor from handling notifications with any type in notification_types"""
        for notification_type in notification_types:
            if notification_type not in self._notification_map:
                raise NotificationSystemException("No such notification type exists: " + notification_type)
            if processor not in self._notification_map[notification_type]:
                raise NotificationSystemException("Processor does not handle notification type " + notification_type)
            self._notification_map[notification_type].remove(processor)
            
    def add_notification(self, notification, notification_type):
        """Adds a notification to the queue"""
        self._notification_queue.append((notification_type, notification))
            
    def process(self):
        """Process all notifications in the queue"""
        queue = self._notification_queue
        self._notification_queue = [] #keep newly generated notifications separate from current queue
        for notification in queue:
            if notification[0] in self._notification_map: #note that notifications are stored as a tuple
                for processor in self._notification_map[notification[0]]:
                    processor.process(notification[1])
            for processor in self._notification_map["*"]:
                processor.process(notification[1])

                
class Notification(object):
    def __init__(self):
        self.timestamp = time.time()

        
class NotificationProcessor(object):
    def process(self, notification):
        pass
 
 
class NotificationGenerator(object):
    def run():
        pass
    
    
class NotificationSystemException(Exception):
    pass

