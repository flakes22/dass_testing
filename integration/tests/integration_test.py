from pathlib import Path
import sys

CODE_DIR = Path(__file__).resolve().parents[1] / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from core.system_state import SystemState

from modules.registration import RegistrationModule
from modules.crew_management import CrewManagementModule
from modules.inventory import InventoryModule
from modules.race_management import RaceManagementModule
from modules.results import ResultsModule
from modules.mission_planning import MissionPlanningModule
from extra_modules.mission_reward import MissionRewardsSystem
from extra_modules.vehicle_upgrade import VehicleUpgradeSystem
def run_integration_tests():

    # TEST CASE 1: Register crew and assign role
    state = SystemState()
    reg = RegistrationModule(state)
    crew = CrewManagementModule(state)

    reg.register_crew("Alex")
    result = crew.assign_role(1, "driver")

    assert "Success" in result
    assert state.crew_members[0].role == "driver"
    print("Test 1 Passed")

    # TEST CASE 2: Add car and assign to race
    state = SystemState()
    inv = InventoryModule(state)
    race = RaceManagementModule(state)

    inv.add_car("CAR1")
    race.create_race(101)
    result = race.assign_car(101, "CAR1")

    assert "Success" in result
    assert state.races[0].car.car_id == "CAR1"
    print("Test 2 Passed")

    # TEST CASE 3: Assign unusable car to race
    state = SystemState()
    inv = InventoryModule(state)
    race = RaceManagementModule(state)

    inv.add_car("CAR2")
    state.cars[0].condition = 0

    race.create_race(102)
    result = race.assign_car(102, "CAR2")

    assert "Error" in result
    print("Test 3 Passed")

    # TEST CASE 4: Complete race and update inventory
    state = SystemState()

    reg = RegistrationModule(state)
    crew = CrewManagementModule(state)
    inv = InventoryModule(state)
    race = RaceManagementModule(state)
    results = ResultsModule(state)

    reg.register_crew("Alex")
    crew.assign_role(1, "driver")

    inv.add_car("CAR1")

    race.create_race(201)
    race.assign_driver(201, 1)
    race.assign_car(201, "CAR1")

    result = results.record_result(201, "win")

    assert "Success" in result
    assert state.cash == 1000
    assert state.rankings["Alex"] == 10

    print("Test 4 Passed")
        # TEST CASE 5: Assign driver with invalid role
    state = SystemState()

    reg = RegistrationModule(state)
    crew = CrewManagementModule(state)
    race = RaceManagementModule(state)

    reg.register_crew("Bob")
    crew.assign_role(1, "mechanic")

    race.create_race(301)
    result = race.assign_driver(301, 1)

    assert "Error" in result
    print("Test 5 Passed")

    # TEST CASE 6: Assign driver without registration
    state = SystemState()

    race = RaceManagementModule(state)

    race.create_race(302)
    result = race.assign_driver(302, 1)

    assert "Error" in result
    print("Test 6 Passed")

    # TEST CASE 7: Record result without assigning driver
    state = SystemState()

    race = RaceManagementModule(state)
    results = ResultsModule(state)

    race.create_race(303)
    result = results.record_result(303, "win")

    assert "Error" in result
    print("Test 7 Passed")

    # TEST CASE 8: Record result for non-existent race
    state = SystemState()

    results = ResultsModule(state)

    result = results.record_result(999, "win")

    assert "Error" in result
    print("Test 8 Passed")

    # TEST CASE 9: Lose race does not change cash
    state = SystemState()

    reg = RegistrationModule(state)
    crew = CrewManagementModule(state)
    inv = InventoryModule(state)
    race = RaceManagementModule(state)
    results = ResultsModule(state)

    reg.register_crew("Alex")
    crew.assign_role(1, "driver")
    inv.add_car("CAR1")

    race.create_race(304)
    race.assign_driver(304, 1)
    race.assign_car(304, "CAR1")

    results.record_result(304, "lose")

    assert state.cash == 0
    print("Test 9 Passed")

    # TEST CASE 10: Multiple race wins accumulate cash and ranking
    state = SystemState()

    reg = RegistrationModule(state)
    crew = CrewManagementModule(state)
    inv = InventoryModule(state)
    race = RaceManagementModule(state)
    results = ResultsModule(state)

    reg.register_crew("Alex")
    crew.assign_role(1, "driver")
    inv.add_car("CAR1")

    race.create_race(305)
    race.assign_driver(305, 1)
    race.assign_car(305, "CAR1")
    results.record_result(305, "win")

    race.create_race(306)
    race.assign_driver(306, 1)
    race.assign_car(306, "CAR1")
    results.record_result(306, "win")

    assert state.cash == 2000
    assert state.rankings["Alex"] == 20
    print("Test 10 Passed")

    # TEST CASE 11: Assign car to non-existent race
    state = SystemState()

    inv = InventoryModule(state)
    race = RaceManagementModule(state)

    inv.add_car("CAR1")
    result = race.assign_car(999, "CAR1")

    assert "Error" in result
    print("Test 11 Passed")

    # TEST CASE 12: Assign non-existent car to race
    state = SystemState()

    race = RaceManagementModule(state)

    race.create_race(307)
    result = race.assign_car(307, "CAR999")

    assert "Error" in result
    print("Test 12 Passed")
        # TEST CASE 13: Mission success with required role
    state = SystemState()

    reg = RegistrationModule(state)
    crew = CrewManagementModule(state)
    mission_mod = MissionPlanningModule(state)

    reg.register_crew("Alice")
    crew.assign_role(1, "mechanic")

    mission_mod.create_mission("repair", ["mechanic"])
    mission = state.missions[0]

    result = mission_mod.start_mission(mission)

    assert "Success" in result
    assert mission.status == "completed"
    print("Test 13 Passed")

    # TEST CASE 14: Mission fails due to missing role
    state = SystemState()

    mission_mod = MissionPlanningModule(state)

    mission_mod.create_mission("repair", ["mechanic"])
    mission = state.missions[0]

    result = mission_mod.start_mission(mission)

    assert "Error" in result
    print("Test 14 Passed")

    # TEST CASE 15: Mission reward adds cash
    state = SystemState()

    mission_mod = MissionPlanningModule(state)
    rewards = MissionRewardsSystem(state)

    mission_mod.create_mission("delivery", [])
    mission = state.missions[0]
    mission.status = "completed"

    rewards.assign_rewards(mission)

    assert state.cash == 500
    print("Test 15 Passed")

    # TEST CASE 16: Mission reward adds spare parts
    state = SystemState()

    mission_mod = MissionPlanningModule(state)
    rewards = MissionRewardsSystem(state)

    mission_mod.create_mission("repair", [])
    mission = state.missions[0]
    mission.status = "completed"

    rewards.assign_rewards(mission)

    assert state.parts["spare_part"] == 1
    print("Test 16 Passed")

    # TEST CASE 17: Mission reward adds reputation
    state = SystemState()

    reg = RegistrationModule(state)
    crew = CrewManagementModule(state)
    mission_mod = MissionPlanningModule(state)
    rewards = MissionRewardsSystem(state)

    reg.register_crew("Alex")
    crew.assign_role(1, "driver")

    mission_mod.create_mission("rescue", [])
    mission = state.missions[0]
    mission.status = "completed"

    rewards.assign_rewards(mission)

    assert state.reputation["Alex"] == 10
    print("Test 17 Passed")

    # TEST CASE 18: Reward not given if mission not completed
    state = SystemState()

    mission_mod = MissionPlanningModule(state)
    rewards = MissionRewardsSystem(state)

    mission_mod.create_mission("delivery", [])
    mission = state.missions[0]   # status = pending

    result = rewards.assign_rewards(mission)

    assert "Error" in result
    print("Test 18 Passed")

    # TEST CASE 19: Unknown mission type handling
    state = SystemState()

    mission_mod = MissionPlanningModule(state)
    rewards = MissionRewardsSystem(state)

    mission_mod.create_mission("unknown", [])
    mission = state.missions[0]
    mission.status = "completed"

    result = rewards.assign_rewards(mission)

    assert "Error" in result
    print("Test 19 Passed")
        # TEST CASE 20: Assign driver twice to same race
    state = SystemState()

    reg = RegistrationModule(state)
    crew = CrewManagementModule(state)
    race = RaceManagementModule(state)

    reg.register_crew("Alex")
    crew.assign_role(1, "driver")

    race.create_race(401)

    result1 = race.assign_driver(401, 1)
    result2 = race.assign_driver(401, 1)

    assert "Success" in result1
    assert "Success" in result2   # current system allows overwrite
    print("Test 20 Passed")

    # TEST CASE 21: Create duplicate race IDs
    state = SystemState()

    race = RaceManagementModule(state)

    result1 = race.create_race(402)
    result2 = race.create_race(402)

    assert "Success" in result1
    assert "Error" in result2
    print("Test 21 Passed")

    # TEST CASE 22: Upgrade car then use in race
    state = SystemState()

    inv = InventoryModule(state)
    upgrade = VehicleUpgradeSystem(state)
    race = RaceManagementModule(state)

    inv.add_car("CAR1")
    state.parts["engine_part"] = 1
    state.cash = 2000

    upgrade.upgrade_engine("CAR1")

    race.create_race(403)
    result = race.assign_car(403, "CAR1")

    assert "Success" in result
    assert state.cars[0].speed == 20
    print("Test 22 Passed")

    # TEST CASE 23: Mission with multiple required roles (all available)
    state = SystemState()

    reg = RegistrationModule(state)
    crew = CrewManagementModule(state)
    mission_mod = MissionPlanningModule(state)

    reg.register_crew("Alex")
    crew.assign_role(1, "driver")

    reg.register_crew("Bob")
    crew.assign_role(2, "mechanic")

    mission_mod.create_mission("complex", ["driver", "mechanic"])
    mission = state.missions[0]

    result = mission_mod.start_mission(mission)

    assert "Success" in result
    print("Test 23 Passed")

    # TEST CASE 24: Full system flow (race → mission → upgrade → race)
    state = SystemState()

    reg = RegistrationModule(state)
    crew = CrewManagementModule(state)
    inv = InventoryModule(state)
    race = RaceManagementModule(state)
    results = ResultsModule(state)
    mission_mod = MissionPlanningModule(state)
    rewards = MissionRewardsSystem(state)
    upgrade = VehicleUpgradeSystem(state)

    # Setup crew
    reg.register_crew("Alex")
    crew.assign_role(1, "driver")

    reg.register_crew("Bob")
    crew.assign_role(2, "mechanic")

    # Setup car
    inv.add_car("CAR1")

    # First race
    race.create_race(404)
    race.assign_driver(404, 1)
    race.assign_car(404, "CAR1")
    results.record_result(404, "win")

    # Mission + rewards
    mission_mod.create_mission("repair", ["mechanic"])
    mission = state.missions[0]
    mission.status = "completed"
    rewards.assign_rewards(mission)

    # Upgrade
    state.parts["engine_part"] = 1
    upgrade.upgrade_engine("CAR1")

    # Second race
    race.create_race(405)
    race.assign_driver(405, 1)
    race.assign_car(405, "CAR1")
    results.record_result(405, "win")

    assert state.cash == 1000 
    print("Test 24 Passed")

    # TEST CASE 25: Car damaged during race → mechanic mission needed
    state = SystemState()

    reg = RegistrationModule(state)
    crew = CrewManagementModule(state)
    inv = InventoryModule(state)
    race = RaceManagementModule(state)
    results = ResultsModule(state)
    mission_mod = MissionPlanningModule(state)

    reg.register_crew("Alex")
    crew.assign_role(1, "driver")
    reg.register_crew("Bob")
    crew.assign_role(2, "mechanic")

    inv.add_car("CAR1")
    race.create_race(501)
    race.assign_driver(501, 1)
    race.assign_car(501, "CAR1")

    # Lose race → car gets damaged
    results.record_result(501, "lose")
    assert state.cars[0].condition == 70   # 100 - 30

    # Mechanic is available → repair mission should succeed
    mission_mod.create_mission("repair", ["mechanic"])
    mission = state.missions[0]
    result = mission_mod.start_mission(mission)
    assert "Success" in result
    print("Test 25 Passed")

    # TEST CASE 26: Damaged car but no mechanic available
    state = SystemState()

    reg = RegistrationModule(state)
    crew = CrewManagementModule(state)
    inv = InventoryModule(state)
    race = RaceManagementModule(state)
    results = ResultsModule(state)
    mission_mod = MissionPlanningModule(state)

    reg.register_crew("Alex")
    crew.assign_role(1, "driver")

    inv.add_car("CAR1")
    race.create_race(502)
    race.assign_driver(502, 1)
    race.assign_car(502, "CAR1")

    results.record_result(502, "lose")
    assert state.cars[0].condition == 70

    # No mechanic registered → repair mission should fail
    mission_mod.create_mission("repair", ["mechanic"])
    mission = state.missions[0]
    result = mission_mod.start_mission(mission)
    assert "Error" in result
    print("Test 26 Passed")

if __name__ == "__main__":
    run_integration_tests()
