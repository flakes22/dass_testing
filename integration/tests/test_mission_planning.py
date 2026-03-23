from pathlib import Path
import sys

CODE_DIR = Path(__file__).resolve().parents[1] / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from core.system_state import SystemState
from modules.mission_planning import MissionPlanningModule
from models.crew import CrewMember


def run_mission_tests():
    state = SystemState()
    mission_module = MissionPlanningModule(state)

    print("Running Unit Tests for Mission Planning...\n")

    # --- Setup: crew members ---
    driver = CrewMember(1, "Alex")
    driver.role = "driver"

    mechanic = CrewMember(2, "Bob")
    mechanic.role = "mechanic"

    strategist = CrewMember(3, "Charlie")
    strategist.role = "strategist"

    state.crew_members.extend([driver, mechanic, strategist])

    # TEST GROUP 1: Create Mission

    result = mission_module.create_mission("delivery", ["driver"])
    assert "Success" in result
    assert len(state.missions) == 1
    print("Test 1 Passed: Mission created")

    # TEST GROUP 2: Start Mission (Valid)

    mission = state.missions[0]

    result = mission_module.start_mission(mission)
    assert "Success" in result
    assert mission.status == "completed"
    print("Test 2 Passed: Mission completed successfully")

    # TEST GROUP 3: Missing Role

    mission2 = mission_module.create_mission("repair", ["mechanic", "driver"])
    mission2 = state.missions[1]

    result = mission_module.start_mission(mission2)
    assert "Success" in result
    print("Test 3 Passed: Multiple roles handled")

    # TEST GROUP 4: Role Not Available

    # Remove mechanic
    state.crew_members = [driver]

    mission3 = mission_module.create_mission("rescue", ["mechanic"])
    mission3 = state.missions[2]

    result = mission_module.start_mission(mission3)
    assert "Error" in result
    print("Test 4 Passed: Missing role detected")

    # TEST GROUP 5: Multiple Missing Roles

    mission4 = mission_module.create_mission("complex", ["driver", "mechanic", "strategist"])
    mission4 = state.missions[3]

    result = mission_module.start_mission(mission4)
    assert "Error" in result
    print("Test 5 Passed: Multiple missing roles handled")

    # TEST GROUP 6: Edge Case - Empty Roles

    mission5 = mission_module.create_mission("free", [])
    mission5 = state.missions[4]

    result = mission_module.start_mission(mission5)
    assert "Success" in result
    print("Test 6 Passed: No-role mission handled")

    print("\nAll Unit Tests for Mission Planning Passed!")
    print("----------------------------------------")
