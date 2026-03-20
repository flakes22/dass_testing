from core.system_state import SystemState
from extra_modules.vehicle_upgrade import VehicleUpgradeSystem
from models.car import Car


def run_vehicle_upgrade_tests():
    state = SystemState()
    upgrade = VehicleUpgradeSystem(state)

    print("Running Unit Tests for Vehicle Upgrade Module...\n")

    # --- Setup ---
    car = Car("CAR1")
    car.speed = 50
    car.condition = 50

    state.cars.append(car)

    state.parts["engine_part"] = 2
    state.parts["armor_part"] = 2
    state.cash = 2000

    # TEST GROUP 1: Engine Upgrade

    result = upgrade.upgrade_engine("CAR1")
    assert "Success" in result
    assert car.speed == 70
    assert state.cash == 1000
    assert state.parts["engine_part"] == 1
    print("Test 1 Passed: Engine upgrade successful")

    # --- Insufficient parts ---
    state.parts["engine_part"] = 0
    result = upgrade.upgrade_engine("CAR1")
    assert "Error" in result
    print("Test 2 Passed: Engine part validation")

    # --- Insufficient cash ---
    state.parts["engine_part"] = 1
    state.cash = 500
    result = upgrade.upgrade_engine("CAR1")
    assert "Error" in result
    print("Test 3 Passed: Cash validation")

    # TEST GROUP 2: Armor Upgrade

    state.cash = 2000
    state.parts["armor_part"] = 1
    car.condition = 50

    result = upgrade.upgrade_armor("CAR1")
    assert "Success" in result
    assert car.condition == 80
    assert state.cash == 1200
    assert state.parts["armor_part"] == 0
    print("Test 4 Passed: Armor upgrade successful")

    # --- Condition cap at 100 ---
    state.parts["armor_part"] = 1
    state.cash = 2000
    car.condition = 90

    upgrade.upgrade_armor("CAR1")
    assert car.condition == 100
    print("Test 5 Passed: Condition capped at 100")

    # --- Missing car ---
    result = upgrade.upgrade_engine("CAR999")
    assert "Error" in result
    print("Test 6 Passed: Missing car handled")

    # TEST GROUP 3: State Integrity

    # Ensure no negative resources
    assert state.cash >= 0
    assert state.parts["engine_part"] >= 0
    print("Test 7 Passed: No negative resource states")

    print("\nAll Unit Tests for Vehicle Upgrade Module Passed!")
    print("----------------------------------------")