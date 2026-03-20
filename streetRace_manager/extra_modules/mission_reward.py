class MissionRewardsSystem:
    def __init__(self, state):
        self.state = state

    # --- Assign Rewards ---
    def assign_rewards(self, mission):
        # --- Validate mission completion ---
        if mission.status != "completed":
            return "Error: Mission not completed"

        mission_type = mission.mission_type

        # --- Delivery Mission ---
        if mission_type == "delivery":
            self.state.cash += 500
            return "Success: Cash reward granted"

        # --- Repair Mission ---
        elif mission_type == "repair":
            self.state.parts["spare_part"] = self.state.parts.get("spare_part", 0) + 1
            return "Success: Spare part reward granted"

        # --- Rescue Mission ---
        elif mission_type == "rescue":
            # Give reputation to ALL crew (simple model)
            for member in self.state.crew_members:
                self.state.reputation[member.name] = self.state.reputation.get(member.name, 0) + 10
            return "Success: Reputation reward granted"

        # --- Unknown mission ---
        return "Error: Unknown mission type"