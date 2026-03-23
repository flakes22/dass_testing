from pathlib import Path
import sys

CODE_DIR = Path(__file__).resolve().parents[1] / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

try:
    from .test_registration import run_registration_tests
    from .test_crew_management import run_crew_management_tests
    from .test_inventory import run_inventory_tests
    from .test_race_management import run_race_management_tests
    from .test_results import run_results_tests
    from .test_mission_planning import run_mission_tests
    from .test_vehicle_upgrade import run_vehicle_upgrade_tests
    from .test_mission_reward import run_mission_rewards_tests
    from .integration_test import run_integration_tests
except ImportError:
    from test_registration import run_registration_tests
    from test_crew_management import run_crew_management_tests
    from test_inventory import run_inventory_tests
    from test_race_management import run_race_management_tests
    from test_results import run_results_tests
    from test_mission_planning import run_mission_tests
    from test_vehicle_upgrade import run_vehicle_upgrade_tests
    from test_mission_reward import run_mission_rewards_tests
    from integration_test import run_integration_tests

if __name__ == "__main__":
    run_registration_tests()
    run_crew_management_tests()
    run_inventory_tests()
    run_race_management_tests()
    run_results_tests()
    run_mission_tests()
    run_vehicle_upgrade_tests()
    run_mission_rewards_tests()
    print("\n========================================")
    print("Running Integration Tests...")
    print("========================================\n")
    run_integration_tests()
    print("\n========================================")
    print("ALL TESTS PASSED!")
    print("========================================")
