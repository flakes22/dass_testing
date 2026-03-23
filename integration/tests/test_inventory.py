from pathlib import Path
import sys

CODE_DIR = Path(__file__).resolve().parents[1] / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from core.system_state import SystemState
from modules.inventory import InventoryModule


def run_inventory_tests():
    state = SystemState()
    inventory = InventoryModule(state)

    print("Running Unit Tests for Inventory Module...\n")

    # TEST GROUP 1: Cars

    # --- Test 1: Add car ---
    result = inventory.add_car("CAR1")
    assert "Success" in result
    assert len(state.cars) == 1
    print("Test 1 Passed: Car added")

    # --- Test 2: Duplicate car ---
    result = inventory.add_car("CAR1")
    assert "Error" in result
    assert len(state.cars) == 1
    print("Test 2 Passed: Duplicate car prevented")

    # TEST GROUP 2: Cash

    # --- Test 3: Add cash ---
    result = inventory.update_cash(1000)
    assert "Success" in result
    assert state.cash == 1000
    print("Test 3 Passed: Cash added")

    # --- Test 4: Deduct cash ---
    result = inventory.update_cash(-500)
    assert "Success" in result
    assert state.cash == 500
    print("Test 4 Passed: Cash deducted")

    # --- Test 5: Insufficient funds ---
    result = inventory.update_cash(-1000)
    assert "Error" in result
    assert state.cash == 500
    print("Test 5 Passed: Negative balance prevented")

    # --- Test 6: Add tool ---
    result = inventory.add_tool("wrench", 5)
    assert "Success" in result
    assert state.tools["wrench"] == 5
    print("Test 6 Passed: Tool added")

    # --- Test 7: Use tool ---
    result = inventory.use_tool("wrench", 3)
    assert "Success" in result
    assert state.tools["wrench"] == 2
    print("Test 7 Passed: Tool used")

    # --- Test 8: Overuse tool ---
    result = inventory.use_tool("wrench", 5)
    assert "Error" in result
    print("Test 8 Passed: Tool overuse prevented")

    # --- Test 9: Tool not found ---
    result = inventory.use_tool("hammer", 1)
    assert "Error" in result
    print("Test 9 Passed: Missing tool handled")

    # TEST GROUP 4: Parts

    # --- Test 10: Add part ---
    result = inventory.add_part("engine", 2)
    assert "Success" in result
    assert state.parts["engine"] == 2
    print("Test 10 Passed: Part added")

    # --- Test 11: Use part ---
    result = inventory.use_part("engine", 1)
    assert "Success" in result
    assert state.parts["engine"] == 1
    print("Test 11 Passed: Part used")

    # --- Test 12: Overuse part ---
    result = inventory.use_part("engine", 5)
    assert "Error" in result
    print("Test 12 Passed: Part overuse prevented")

    # --- Test 13: Part not found ---
    result = inventory.use_part("wheel", 1)
    assert "Error" in result
    print("Test 13 Passed: Missing part handled")

   
    # TEST GROUP 5: Edge Cases

    # --- Test 14: Invalid quantity ---
    result = inventory.add_tool("screwdriver", -1)
    assert "Error" in result
    print("Test 14 Passed: Negative quantity rejected")

    result = inventory.use_tool("wrench", 0)
    assert "Error" in result
    print("Test 15 Passed: Zero quantity rejected")

    print("\nAll Unit Tests for Inventory Module Passed!")
    print("----------------------------------------")
