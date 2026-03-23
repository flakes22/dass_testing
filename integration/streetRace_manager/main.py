from core.system_state import SystemState
from modules.registration import RegistrationModule
from modules.crew_management import CrewManagementModule
from modules.inventory import InventoryModule
from modules.race_management import RaceManagementModule
from modules.results import ResultsModule
from modules.mission_planning import MissionPlanningModule
from extra_modules.mission_reward import MissionRewardsSystem
from extra_modules.vehicle_upgrade import VehicleUpgradeSystem


def main():
    state = SystemState()

    # initialize modules
    reg = RegistrationModule(state)
    crew = CrewManagementModule(state)
    inv = InventoryModule(state)
    race = RaceManagementModule(state)
    results = ResultsModule(state)
    mission = MissionPlanningModule(state)
    rewards = MissionRewardsSystem(state)
    upgrade = VehicleUpgradeSystem(state)

    while True:
        print("\n--- StreetRace Manager ---")
        print("1. Register Crew")
        print("2. Manage Crew")
        print("3. Inventory")
        print("4. Create Race")
        print("5. Record Result")
        print("6. Plan Mission")
        print("7. Vehicle Upgrade")
        print("8. Mission Rewards")
        print("9. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            name = input("Enter crew member name: ")
            role = input("Enter role (driver/mechanic/strategist) or press Enter for unassigned: ").strip()
            if not role:
                role = "unassigned"
            print(reg.register_crew(name, role))

        elif choice == "2":
            sub = input("1. Assign Role  2. Update Skill: ")
            if sub == "1":
                crew_id = int(input("Crew ID: "))
                role = input("Role (driver/mechanic/strategist): ")
                print(crew.assign_role(crew_id, role))
            elif sub == "2":
                crew_id = int(input("Crew ID: "))
                skill = int(input("Skill Level: "))
                print(crew.update_skill(crew_id, skill))

        elif choice == "3":
            sub = input("1. Add Car  2. Update Cash  3. Add Tool  4. Use Tool  5. Add Part  6. Use Part: ")
            if sub == "1":
                car_id = input("Car ID: ")
                print(inv.add_car(car_id))
            elif sub == "2":
                amount = int(input("Amount (+/-): "))
                print(inv.update_cash(amount))
            elif sub == "3":
                name = input("Tool name: ")
                qty = int(input("Quantity: "))
                print(inv.add_tool(name, qty))
            elif sub == "4":
                name = input("Tool name: ")
                qty = int(input("Quantity: "))
                print(inv.use_tool(name, qty))
            elif sub == "5":
                name = input("Part name: ")
                qty = int(input("Quantity: "))
                print(inv.add_part(name, qty))
            elif sub == "6":
                name = input("Part name: ")
                qty = int(input("Quantity: "))
                print(inv.use_part(name, qty))

        elif choice == "4":
            race_id = int(input("Race ID: "))
            print(race.create_race(race_id))
            driver_id = input("Assign driver? Enter crew ID or skip: ").strip()
            if driver_id:
                print(race.assign_driver(race_id, int(driver_id)))
            car_id = input("Assign car? Enter car ID or skip: ").strip()
            if car_id:
                print(race.assign_car(race_id, car_id))

        elif choice == "5":
            race_id = int(input("Race ID: "))
            result = input("Result (win/lose): ")
            print(results.record_result(race_id, result))

        elif choice == "6":
            mission_type = input("Mission type (delivery/repair/rescue): ")
            roles = input("Required roles (comma-separated): ").split(",")
            roles = [r.strip() for r in roles if r.strip()]
            mission.create_mission(mission_type, roles)
            m = state.missions[-1]
            start = input("Start mission now? (y/n): ")
            if start.lower() == "y":
                result = mission.start_mission(m)
                print(result)
                if "Success" in result:
                    print(rewards.assign_rewards(m))

        elif choice == "7":
            sub = input("1. Upgrade Engine  2. Upgrade Armor: ")
            car_id = input("Car ID: ")
            if sub == "1":
                print(upgrade.upgrade_engine(car_id))
            elif sub == "2":
                print(upgrade.upgrade_armor(car_id))

        elif choice == "8":
            if not state.missions:
                print("No missions available")
            else:
                for i, m in enumerate(state.missions):
                    print(f"{i}: {m.mission_type} ({m.status})")
                idx = int(input("Mission index: "))
                if 0 <= idx < len(state.missions):
                    print(rewards.assign_rewards(state.missions[idx]))

        elif choice == "9":
            break


if __name__ == "__main__":
    main()