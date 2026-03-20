from core.system_state import SystemState

def main():
    state = SystemState()

    # initialize modules

    while True:
        print("\n--- StreetRace Manager ---")
        print("1. Register Crew")
        print("2. Manage Crew")
        print("3. Inventory")
        print("4. Create Race")
        print("5. Record Result")
        print("6. Plan Mission")
        print("7. Exit")

        choice = input("Enter choice: ")

        if choice == "7":
            break