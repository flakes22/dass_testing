class CrewManagementModule:
    VALID_ROLES = ["driver", "mechanic", "strategist"]

    def __init__(self, state):
        self.state = state

    # --- Helper: find member by ID ---
    def _find_member(self, crew_id):
        for member in self.state.crew_members:
            if member.id == crew_id:
                return member
        return None

    # --- Assign Role ---
    def assign_role(self, crew_id, role):
        """
        Assigns a role to a crew member.
        Rules:
        - Crew must exist
        - Role must be valid
        """

        member = self._find_member(crew_id)

        # --- Validation: crew exists ---
        if member is None:
            return "Error: Crew member not found"

        # --- Validation: valid role ---
        if role not in self.VALID_ROLES:
            return "Error: Invalid role"

        member.role = role
        return f"Success: Role '{role}' assigned to {member.name}"

    # --- Update Skill ---
    def update_skill(self, crew_id, skill):
        """
        Updates skill level.
        Rules:
        - Crew must exist
        - Skill must be >= 0
        """

        member = self._find_member(crew_id)

        # --- Validation: crew exists ---
        if member is None:
            return "Error: Crew member not found"

        # --- Validation: skill value ---
        if skill < 0:
            return "Error: Skill cannot be negative"

        member.skill = skill
        return f"Success: Skill updated to {skill} for {member.name}"