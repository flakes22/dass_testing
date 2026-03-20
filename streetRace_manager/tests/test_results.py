from core.system_state import SystemState
from modules.results import ResultsModule
from models.crew import CrewMember
from models.race import Race
from models.car import Car


def run_results_tests():
    state = SystemState()
    results = ResultsModule(state)

    print("Running Unit Tests for Results Module...\n")

    # --- Setup: create driver ---
    driver = CrewMember(1, "Alex")
    driver.role = "driver"

    # --- Setup: create race ---
    race = Race(101)
    race.driver = driver

    state.races.append(race)

    # TEST GROUP 1: Valid Result (Win)

    result = results.record_result(101, "win")
    assert "Success" in result
    assert race.result == "win"
    assert state.rankings["Alex"] == 10
    assert state.cash == 1000
    print("Test 1 Passed: Win updates ranking and cash")

    # TEST GROUP 2: Valid Result (Lose)

    race2 = Race(102)
    race2.driver = driver
    state.races.append(race2)

    result = results.record_result(102, "lose")
    assert "Success" in result
    assert race2.result == "lose"
    assert state.rankings["Alex"] == 10   # unchanged
    assert state.cash == 1000             # unchanged
    print("Test 2 Passed: Loss does not change ranking or cash")

    # TEST GROUP 3: Invalid Result Input

    result = results.record_result(101, "draw")
    assert "Error" in result
    print("Test 3 Passed: Invalid result rejected")

    # TEST GROUP 4: No Driver Assigned

    race3 = Race(103)
    state.races.append(race3)

    result = results.record_result(103, "win")
    assert "Error" in result
    print("Test 4 Passed: Missing driver handled")

    # TEST GROUP 5: Non-existent Race

    result = results.record_result(999, "win")
    assert "Error" in result
    print("Test 5 Passed: Missing race handled")

    # TEST GROUP 6: Multiple Wins Accumulation

    race4 = Race(104)
    race4.driver = driver
    state.races.append(race4)

    results.record_result(104, "win")

    assert state.rankings["Alex"] == 20
    assert state.cash == 2000
    print("Test 6 Passed: Multiple wins accumulate correctly")

    # TEST GROUP 7: Car Damage on Loss

    car = Car("CAR_DMG")
    car.condition = 100
    state.cars.append(car)

    race5 = Race(105)
    race5.driver = driver
    race5.car = car
    state.races.append(race5)

    results.record_result(105, "lose")
    assert car.condition == 70   # 100 - 30
    print("Test 7 Passed: Car damaged on loss")

    # TEST GROUP 8: Car Condition Floor at 0

    car2 = Car("CAR_LOW")
    car2.condition = 10
    state.cars.append(car2)

    race6 = Race(106)
    race6.driver = driver
    race6.car = car2
    state.races.append(race6)

    results.record_result(106, "lose")
    assert car2.condition == 0   # max(0, 10 - 30)
    print("Test 8 Passed: Car condition floors at 0")

    print("\nAll Unit Tests for Results Module Passed!")
    print("----------------------------------------")