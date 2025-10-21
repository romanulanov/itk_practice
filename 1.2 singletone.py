import turtle as t1
import turtle as t2

print(t1 is t2)


class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class MyClass(metaclass=SingletonMeta):
    pass


a = MyClass()
b = MyClass()
print(a is b)
