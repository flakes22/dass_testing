class VehicleUpgradeSystem:
    def __init__(self, state):
        self.state = state

    # --- Helper ---
    def _find_car(self, car_id):
        for car in self.state.cars:
            if car.car_id == car_id:
                return car
        return None

    # --- Engine Upgrade ---
    def upgrade_engine(self, car_id):
        car = self._find_car(car_id)

        if not car:
            return "Error: Car not found"

        # Requirements
        if self.state.parts.get("engine_part", 0) < 1:
            return "Error: Not enough engine parts"

        if self.state.cash < 1000:
            return "Error: Not enough cash"

        # Apply upgrade
        self.state.parts["engine_part"] -= 1
        self.state.cash -= 1000

        car.speed += 20
        return f"Success: Engine upgraded for '{car_id}'"

    # --- Armor Upgrade ---
    def upgrade_armor(self, car_id):
        car = self._find_car(car_id)

        if not car:
            return "Error: Car not found"

        # Requirements
        if self.state.parts.get("armor_part", 0) < 1:
            return "Error: Not enough armor parts"

        if self.state.cash < 800:
            return "Error: Not enough cash"

        # Apply upgrade
        self.state.parts["armor_part"] -= 1
        self.state.cash -= 800

        car.condition = min(100, car.condition + 30)
        return f"Success: Armor upgraded for '{car_id}'"