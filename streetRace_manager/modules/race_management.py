class RaceManagementModule:
    def __init__(self, state):
        self.state = state

    # --- Helpers ---
    def _find_race(self, race_id):
        for race in self.state.races:
            if race.race_id == race_id:
                return race
        return None

    def _find_member(self, crew_id):
        for member in self.state.crew_members:
            if member.id == crew_id:
                return member
        return None

    def _find_car(self, car_id):
        for car in self.state.cars:
            if car.car_id == car_id:
                return car
        return None

    # --- Create Race ---
    def create_race(self, race_id):
        if self._find_race(race_id):
            return "Error: Race already exists"

        from models.race import Race
        new_race = Race(race_id)
        self.state.races.append(new_race)

        return f"Success: Race '{race_id}' created"

    # --- Assign Driver ---
    def assign_driver(self, race_id, crew_id):
        race = self._find_race(race_id)
        if not race:
            return "Error: Race not found"

        member = self._find_member(crew_id)
        if not member:
            return "Error: Crew member not found"

        if member.role != "driver":
            return "Error: Only drivers can be assigned"

        race.driver = member
        return f"Success: Driver '{member.name}' assigned"

    # --- Assign Car ---
    def assign_car(self, race_id, car_id):
        race = self._find_race(race_id)
        if not race:
            return "Error: Race not found"

        car = self._find_car(car_id)
        if not car:
            return "Error: Car not found"

        if car.condition <= 0:
            return "Error: Car is not usable"

        race.car = car
        return f"Success: Car '{car_id}' assigned"