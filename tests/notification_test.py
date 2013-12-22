import unittest

import notification

class BasicNotificationTest(unittest.TestCase):     
    def test_processor_registration(self):
        notification_system = notification.NotificationSystem()
        processor = notification.NotificationProcessor()
        processor2 = notification.NotificationProcessor()
        notification_system.register(processor, "A")
        notification_system.register(processor, "B")
        notification_system.register(processor, "C", "D")
        notification_system.register(processor2, "E", "A")
        self.assertRaises(notification.NotificationSystemException, notification_system.unregister, processor, "E")
        self.assertRaises(notification.NotificationSystemException, notification_system.unregister, processor, "G")
        
        notification_system.unregister(processor, "A")
        self.assertRaises(notification.NotificationSystemException, notification_system.unregister, processor, "A")
        notification_system.unregister(processor2, "A")
        notification_system.unregister(processor, "B", "C")
        self.assertRaises(notification.NotificationSystemException, notification_system.unregister, processor, "B")
        self.assertRaises(notification.NotificationSystemException, notification_system.unregister, processor, "C")
    
    def test_notification_processing(self):
        #stampprocessors acts on stampnotifications and mark that the notifications have been processed
        class StampProcessor(notification.NotificationProcessor):
            def __init__(self, str):
                self.str = str
                
            def __repr__(self):
                return self.str
                
            def process(self, notification):
                notification.stamps.add(self)
            
                
        class StampNotification(notification.Notification):
            def __init__(self):
                self.stamps = set()
        
        system = notification.NotificationSystem()
        processor1 = StampProcessor("p1")
        processor2 = StampProcessor("p2")
        processor3 = StampProcessor("p3")
        
        system.register(processor1, "*")
        system.register(processor2, "A", "B")
        system.register(processor3, "A", "C")
        
        stamp1 = StampNotification()
        system.add_notification(stamp1, "B")
        system.process() #*:1; A: 2,3; B: 2; C: 3
        self.assertEqual(set([processor1, processor2]), stamp1.stamps)
        
        stamp2 = StampNotification()
        system.add_notification(stamp2, "A")
        system.process() #*:1; A: 2,3; B: 2; C: 3
        self.assertEqual(set([processor1, processor2, processor3]), stamp2.stamps)
        
        stamp1 = StampNotification()
        stamp2 = StampNotification()
        system.add_notification(stamp1, "A")
        system.add_notification(stamp2, "A")
        system.process() #*:1; A: 2,3; B: 2; C: 3
        self.assertEqual(set([processor1, processor2, processor3]), stamp1.stamps)
        self.assertEqual(set([processor1, processor2, processor3]), stamp2.stamps)
        
        stamp1 = StampNotification()
        stamp2 = StampNotification()
        system.unregister(processor2, "A")
        system.add_notification(stamp1, "A")
        system.process() #*:1; A: 3; B: 2; C: 3
        self.assertEqual(set([processor1, processor3]), stamp1.stamps)
        
        stamp1 = StampNotification()
        stamp2 = StampNotification()
        system.unregister(processor2, "B")
        system.register(processor2, "C")
        system.add_notification(stamp1, "A")
        system.add_notification(stamp2, "C")
        system.process() #*:1; A: 3; B: ; C: 2,3
        self.assertEqual(set([processor1, processor3]), stamp1.stamps)
        self.assertEqual(set([processor1, processor2, processor3]), stamp2.stamps)