from core.system_state import SystemState
from modules.crew_management import CrewManagementModule
from models.crew import CrewMember


def run_crew_management_tests():
    state = SystemState()
    crew_module = CrewManagementModule(state)

    print("Running Unit Tests for Crew Management...\n")

    # --- Setup: manually add crew (NO registration module) ---
    member1 = CrewMember(1, "Alex")
    member2 = CrewMember(2, "Bob")

    state.crew_members.append(member1)
    state.crew_members.append(member2)

    # TEST GROUP 1: assign_role()

    # --- Test 1: Valid role assignment ---
    result = crew_module.assign_role(1, "driver")
    assert "Success" in result
    assert member1.role == "driver"
    print("Test 1 Passed: Valid role assignment")

    # --- Test 2: Invalid role ---
    result = crew_module.assign_role(1, "pilot")
    assert "Error" in result
    assert member1.role == "driver"   # unchanged
    print("Test 2 Passed: Invalid role rejected")

    # --- Test 3: Non-existent crew ---
    result = crew_module.assign_role(999, "driver")
    assert "Error" in result
    print("Test 3 Passed: Non-existent crew handled")

    # --- Test 4: Change role ---
    result = crew_module.assign_role(1, "mechanic")
    assert "Success" in result
    assert member1.role == "mechanic"
    print("Test 4 Passed: Role update works")

    # TEST GROUP 2: update_skill()

    # --- Test 5: Valid skill update ---
    result = crew_module.update_skill(1, 75)
    assert "Success" in result
    assert member1.skill == 75
    print("Test 5 Passed: Skill updated correctly")

    # --- Test 6: Zero skill (edge case) ---
    result = crew_module.update_skill(1, 0)
    assert "Success" in result
    assert member1.skill == 0
    print("Test 6 Passed: Zero skill handled")

    # --- Test 7: Negative skill ---
    result = crew_module.update_skill(1, -5)
    assert "Error" in result
    assert member1.skill == 0   # unchanged
    print("Test 7 Passed: Negative skill rejected")

    # --- Test 8: Non-existent crew skill update ---
    result = crew_module.update_skill(999, 50)
    assert "Error" in result
    print("Test 8 Passed: Non-existent crew skill update handled")

    # TEST GROUP 3: State Integrity
    
    # --- Test 9: Ensure other members unaffected ---
    assert member2.role is None
    assert member2.skill == 0
    print("Test 9 Passed: No unintended side effects")

    print("\nAll Unit Tests for Crew Management Passed!\n")
    print("----------------------------------------")