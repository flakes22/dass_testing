from models.crew import CrewMember


class RegistrationModule:
    def __init__(self, state):
        self.state = state

    def register_crew(self, name):
        """
        Registers a new crew member.
        Improvements:
        - Case-insensitive uniqueness
        - Auto ID assignment
        """

        # --- Validation: empty ---
        if not name or not name.strip():
            return "Error: Name cannot be empty"

        name = name.strip()
        normalized_name = name.lower()

        # --- Duplicate check (case-insensitive) ---
        for member in self.state.crew_members:
            if member.name.lower() == normalized_name:
                return "Error: Crew member already exists"

        # --- Assign unique ID ---
        crew_id = self.state.next_crew_id
        self.state.next_crew_id += 1

        # --- Create member ---
        new_member = CrewMember(crew_id, name)
        self.state.crew_members.append(new_member)

        return f"Success: Crew member '{name}' registered with ID {crew_id}"