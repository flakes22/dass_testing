class ResultsModule:
    def __init__(self, state):
        self.state = state

    # --- Helper ---
    def _find_race(self, race_id):
        for race in self.state.races:
            if race.race_id == race_id:
                return race
        return None

    # --- Record Result ---
    def record_result(self, race_id, result):
        """
        result: "win" or "lose"
        """

        race = self._find_race(race_id)

        # --- Validation: race exists ---
        if not race:
            return "Error: Race not found"

        # --- Validation: driver assigned ---
        if not race.driver:
            return "Error: No driver assigned"

        # --- Validation: valid result ---
        if result not in ["win", "lose"]:
            return "Error: Invalid result"

        race.result = result
        driver_name = race.driver.name

        # --- Update rankings ---
        if result == "win":
            self.state.rankings[driver_name] = self.state.rankings.get(driver_name, 0) + 10

            # --- Update cash ---
            self.state.cash += 1000

        return f"Success: Result recorded for race {race_id}"