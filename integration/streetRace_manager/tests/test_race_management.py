from core.system_state import SystemState
from modules.race_management import RaceManagementModule
from models.crew import CrewMember
from models.car import Car


def run_race_management_tests():
    state = SystemState()
    race_module = RaceManagementModule(state)

    print("Running Unit Tests for Race Management...\n")

    # --- Setup: manually add crew ---
    driver = CrewMember(1, "Alex")
    driver.role = "driver"

    mechanic = CrewMember(2, "Bob")
    mechanic.role = "mechanic"

    state.crew_members.append(driver)
    state.crew_members.append(mechanic)

    # --- Setup: manually add cars ---
    car1 = Car("CAR1")
    car1.condition = 100

    car2 = Car("CAR2")
    car2.condition = 0   # unusable

    state.cars.append(car1)
    state.cars.append(car2)

    # TEST GROUP 1: Create Race

    result = race_module.create_race(101)
    assert "Success" in result
    assert len(state.races) == 1
    print("Test 1 Passed: Race created")

    result = race_module.create_race(101)
    assert "Error" in result
    print("Test 2 Passed: Duplicate race prevented")

    # TEST GROUP 2: Assign Driver

    # --- Valid driver ---
    result = race_module.assign_driver(101, 1)
    assert "Success" in result
    assert state.races[0].driver == driver
    print("Test 3 Passed: Valid driver assigned")

    # --- Non-driver role ---
    result = race_module.assign_driver(101, 2)
    assert "Error" in result
    print("Test 4 Passed: Non-driver rejected")

    # --- Non-existent crew ---
    result = race_module.assign_driver(101, 999)
    assert "Error" in result
    print("Test 5 Passed: Missing crew handled")

    # --- Non-existent race ---
    result = race_module.assign_driver(999, 1)
    assert "Error" in result
    print("Test 6 Passed: Missing race handled")

    # TEST GROUP 3: Assign Car

    # --- Valid car ---
    result = race_module.assign_car(101, "CAR1")
    assert "Success" in result
    assert state.races[0].car == car1
    print("Test 7 Passed: Valid car assigned")

    # --- Unusable car ---
    result = race_module.assign_car(101, "CAR2")
    assert "Error" in result
    print("Test 8 Passed: Unusable car rejected")

    # --- Non-existent car ---
    result = race_module.assign_car(101, "CAR999")
    assert "Error" in result
    print("Test 9 Passed: Missing car handled")

    # --- Non-existent race ---
    result = race_module.assign_car(999, "CAR1")
    assert "Error" in result
    print("Test 10 Passed: Missing race handled")

    # TEST GROUP 4: State Integrity


    assert state.races[0].driver == driver
    assert state.races[0].car == car1
    print("Test 11 Passed: State integrity maintained")

    print("\nAll Unit Tests for Race Management Passed!")
    print("----------------------------------------")