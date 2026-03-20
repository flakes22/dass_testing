class SystemState:
    def __init__(self):
        # Crew
        self.crew_members = []     # list of CrewMember
        self.next_crew_id = 1
        # Inventory
        self.cars = []             # list of Car
        self.tools = {}            # {"tool_name": quantity}
        self.parts = {}            # {"part_name": quantity}
        self.cash = 0

        # Race & Results
        self.races = []            # list of Race
        self.rankings = {}         # {"name": score}

        # Missions
        self.missions = []         # list of Mission

        # Extra modules
        self.reputation = {}       # {"name": reputation_score}