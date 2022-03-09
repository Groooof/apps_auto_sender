class Subject:
    def __init__(self):
        self.observers: [Observer] = list()

    def attach(self, observer):
        self.observers.append(observer)

    def detach(self, observer):
        self.observers.remove(observer)

    def notify(self, data):
        for observer in self.observers:
            observer.update(data)


class Observer:
    def update(self, data: dict):
        pass
