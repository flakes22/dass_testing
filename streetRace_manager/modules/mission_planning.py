class MissionPlanningModule:
    def __init__(self, state):
        self.state = state

    # --- Helper: check role availability ---
    def _role_available(self, role):
        for member in self.state.crew_members:
            if member.role == role:
                return True
        return False

    # --- Create Mission ---
    def create_mission(self, mission_type, required_roles):
        from models.mission import Mission

        mission = Mission(mission_type, required_roles)
        self.state.missions.append(mission)

        return f"Success: Mission '{mission_type}' created"

    # --- Start Mission ---
    def start_mission(self, mission):
        # --- Validate roles ---
        for role in mission.required_roles:
            if not self._role_available(role):
                return f"Error: Required role '{role}' not available"

        mission.status = "completed"
        return f"Success: Mission '{mission.mission_type}' completed"