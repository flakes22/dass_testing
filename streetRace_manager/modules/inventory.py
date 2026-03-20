from models.car import Car

class InventoryModule:
    def __init__(self, state):
        self.state = state

    # --- Add Car ---
    def add_car(self, car_id):
        # Check duplicate
        for car in self.state.cars:
            if car.car_id == car_id:
                return "Error: Car already exists"

        new_car = Car(car_id)
        self.state.cars.append(new_car)
        return f"Success: Car '{car_id}' added"

    # --- Update Cash ---
    def update_cash(self, amount):
        if self.state.cash + amount < 0:
            return "Error: Insufficient funds"

        self.state.cash += amount
        return f"Success: Cash updated to {self.state.cash}"

    # --- Add Tool ---
    def add_tool(self, tool_name, quantity):
        if quantity <= 0:
            return "Error: Quantity must be positive"

        self.state.tools[tool_name] = self.state.tools.get(tool_name, 0) + quantity
        return f"Success: Tool '{tool_name}' updated"

    # --- Use Tool ---
    def use_tool(self, tool_name, quantity):
        if tool_name not in self.state.tools:
            return "Error: Tool not found"

        if quantity <= 0:
            return "Error: Quantity must be positive"

        if self.state.tools[tool_name] < quantity:
            return "Error: Not enough tools"

        self.state.tools[tool_name] -= quantity
        return f"Success: Tool '{tool_name}' used"

    # --- Add Part ---
    def add_part(self, part_name, quantity):
        if quantity <= 0:
            return "Error: Quantity must be positive"

        self.state.parts[part_name] = self.state.parts.get(part_name, 0) + quantity
        return f"Success: Part '{part_name}' updated"

    # --- Use Part ---
    def use_part(self, part_name, quantity):
        if part_name not in self.state.parts:
            return "Error: Part not found"

        if quantity <= 0:
            return "Error: Quantity must be positive"

        if self.state.parts[part_name] < quantity:
            return "Error: Not enough parts"

        self.state.parts[part_name] -= quantity
        return f"Success: Part '{part_name}' used"