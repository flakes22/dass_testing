class Mission:
    def __init__(self, mission_type, required_roles):
        self.mission_type = mission_type
        self.required_roles = required_roles
        self.status = "pending"