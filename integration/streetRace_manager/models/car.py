class Car:
    def __init__(self, car_id):
        self.car_id = car_id
        self.condition = 100      # 0–100
        self.speed = 0
        self.assigned_driver = None