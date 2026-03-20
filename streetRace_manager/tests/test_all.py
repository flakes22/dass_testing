from test_registration import run_registration_tests
from test_crew_management import run_crew_management_tests
from test_inventory import run_inventory_tests
from test_race_management import run_race_management_tests
from test_results import run_results_tests

if __name__ == "__main__":
    run_registration_tests()
    run_crew_management_tests()
    run_inventory_tests()
    run_race_management_tests()
    run_results_tests()

