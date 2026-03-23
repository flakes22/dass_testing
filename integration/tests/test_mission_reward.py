from pathlib import Path
import sys

CODE_DIR = Path(__file__).resolve().parents[1] / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from core.system_state import SystemState
from extra_modules.mission_reward import MissionRewardsSystem
from models.mission import Mission
from models.crew import CrewMember


def run_mission_rewards_tests():
    state = SystemState()
    rewards = MissionRewardsSystem(state)

    print("Running Unit Tests for Mission Rewards Module...\n")

    # --- Setup crew ---
    member1 = CrewMember(1, "Alex")
    member2 = CrewMember(2, "Bob")

    state.crew_members.extend([member1, member2])

    # TEST GROUP 1: Delivery Reward (Cash)

    mission = Mission("delivery", [])
    mission.status = "completed"

    result = rewards.assign_rewards(mission)
    assert "Success" in result
    assert state.cash == 500
    print("Test 1 Passed: Cash reward applied")

    # TEST GROUP 2: Repair Reward (Parts)

    mission2 = Mission("repair", [])
    mission2.status = "completed"

    result = rewards.assign_rewards(mission2)
    assert "Success" in result
    assert state.parts["spare_part"] == 1
    print("Test 2 Passed: Spare part reward applied")

    # TEST GROUP 3: Rescue Reward (Reputation)

    mission3 = Mission("rescue", [])
    mission3.status = "completed"

    result = rewards.assign_rewards(mission3)
    assert "Success" in result
    assert state.reputation["Alex"] == 10
    assert state.reputation["Bob"] == 10
    print("Test 3 Passed: Reputation reward applied")

    # TEST GROUP 4: Mission Not Completed

    mission4 = Mission("delivery", [])
    mission4.status = "pending"

    result = rewards.assign_rewards(mission4)
    assert "Error" in result
    print("Test 4 Passed: Completion validation enforced")

    # TEST GROUP 5: Unknown Mission Type

    mission5 = Mission("unknown", [])
    mission5.status = "completed"

    result = rewards.assign_rewards(mission5)
    assert "Error" in result
    print("Test 5 Passed: Unknown mission handled")

    # TEST GROUP 6: Accumulation Check

    mission6 = Mission("delivery", [])
    mission6.status = "completed"

    rewards.assign_rewards(mission6)

    assert state.cash == 1000
    print("Test 6 Passed: Rewards accumulate correctly")

    print("\nAll Unit Tests for Mission Rewards Module Passed!")
    print("----------------------------------------")
