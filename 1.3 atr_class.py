from datetime import datetime


class Meta(type):
    def __init__(cls, name, bases, namespace):
        cls.created_at = datetime.now()
        super(Meta, cls).__init__(name, bases, namespace)
