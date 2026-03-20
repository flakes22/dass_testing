from core.system_state import SystemState
from modules.registration import RegistrationModule


def run_registration_tests():
    state = SystemState()
    reg = RegistrationModule(state)

    print("Running Registration Module Tests...\n")

    # --- Test 1: Valid registration ---
    result = reg.register_crew("Alex")
    assert "Success" in result
    assert state.crew_members[0].id == 1
    print("Test 1 Passed: Valid registration with ID")

    # --- Test 2: Case-insensitive duplicate ---
    result = reg.register_crew("alex")
    assert "Error" in result
    assert len(state.crew_members) == 1
    print("Test 2 Passed: Case-insensitive duplicate prevented")

    # --- Test 3: Another valid registration ---
    reg.register_crew("Brian")
    assert state.crew_members[1].id == 2
    print("Test 3 Passed: Sequential ID assignment")

    # --- Test 4: Empty name ---
    result = reg.register_crew("")
    assert "Error" in result
    print("Test 4 Passed: Empty name rejected")

    # --- Test 5: Whitespace ---
    result = reg.register_crew("   ")
    assert "Error" in result
    print("Test 5 Passed: Whitespace rejected")

    # --- Test 6: Multiple valid entries ---
    reg.register_crew("Charlie")
    reg.register_crew("David")

    ids = [m.id for m in state.crew_members]
    assert ids == [1, 2, 3, 4]
    print("Test 6 Passed: IDs increment correctly")

    # --- Test 7: Name normalization behavior ---
    reg.register_crew("Eve")
    result = reg.register_crew("EVE")
    assert "Error" in result
    print("Test 7 Passed: Normalization consistency")

    print("\nAll Registration Unit Tests Passed!\n")
    print("----------------------------------------")