# White-Box Testing Report for MoneyPoly

This report outlines the white-box test cases created for the MoneyPoly game, explaining the purpose of each test case (based on the internal code paths and branch conditions) and detailing the bugs and logical issues discovered during execution. The full test code is located in `test_whitebox.py`.

## 1. Bank Module Tests (`test_bank_*`)

**Why they are needed:**
The `Bank` module manages the central economy. Testing it ensures that all conditions (positive additions, negative edge cases, sufficient funds checks, and state modifications for loans) are correctly branch-covered.
- `test_bank_collect` and `test_bank_collect_negative`: Verify the branch logic handling incoming funds and ignoring illegal negative amounts.
- `test_bank_give_loan`: Verifies the branch where a player receives money and the bank's internal balance drops.

**Errors Found:**
- **Bug 1: Negative collections reduce funds.** The `collect(amount)` function documentation states negative amounts are silently ignored, but the code simply uses `self._funds += amount`. Because the amount is negative, the bank's balance actually decreases instead of rejecting it.
- **Bug 2: Loans do not decrease bank funds.** The `give_loan(player, amount)` function credits the player’s balance but completely forgets to deduct the loaned amount from the bank's `self._funds`, creating money out of thin air.

## 2. Player Module Tests (`test_player_*`)

**Why they are needed:**
The `Player` class holds game state. Tests must cover adding/deducting money (raising ValueErrors for negatives), movement logic (wrapping around the board's modulo arithmetic), and jail placement. 
- `test_player_move_land_on_go` and `test_player_move_pass_go`: specifically cover the condition `if self.position == 0` vs wrapping past `0` to verify `GO_SALARY` distribution.

**Errors Found:**
- **Bug 3: Passing Go doesn't award salary.** The logic `if self.position == 0:` only triggers if the player lands *exactly* on Go (Tile 0). If they roll a high number and wrap around (e.g., jumping from 38 to 2), they are not awarded the $200 salary, breaking standard gameplay rules.

## 3. Property & Board Tests (`test_property_*`, `test_board_*`)

**Why they are needed:**
Testing properties involves checking the rent calculation branches (`if self.is_mortgaged`, `if self.group.all_owned_by(...)`) and board initializations to ensure all properties map to correct special tiles and bounds.
- `test_property_get_rent`: Specifically targets the branch computing double rent for a fully owned color group.

**Errors Found:**
- **Bug 4: Rent doubles incorrectly on partial groups.** The `all_owned_by(player)` function in `PropertyGroup` mistakenly uses `any(...)` instead of `all(...)`. Because of this, rent doubles if a player owns *at least one* property in the group, rather than exclusively triggering when they own *all* of them.

## 4. Dice Module Tests (`test_dice_*`)

**Why they are needed:**
To cover the paths testing doubles conditions and tracking streaks (`if self.is_doubles()`). The edge cases involve roll boundaries.

**Errors Found:**
- **Bug 5: Dice are broken (capped at 5).** Uncovered by running a 100-roll test where no 6 was ever rolled. The `roll()` implementation uses `random.randint(1, 5)` instead of `random.randint(1, 6)`.

## 5. Game Logic Tests (`test_trade_logic`, `test_jail_pay_fine`, etc.)

**Why they are needed:**
The `Game` class binds everything together. Test cases check branches for buying, paying rent, interacting with chance cards, bankruptcy loop removals, trades between two player states, and evaluating jail logic branches (using a card, paying, or waiting 3 turns).
- `test_trade_logic`: Evaluates the execution block of property and cash exchanges.
- `test_jail_pay_fine`: Validates the exact branch executing a voluntary pay-fine exit.

**Errors Found:**
- **Bug 6: Trade transactions "delete" money.** When executing a property trade, `game.trade()` successfully deducts the `cash_amount` from the buyer but missing `seller.add_money()` logic means the seller never actually receives the cash. The cash disappears.
- **Bug 7: Paying to leave jail is free.** In `_handle_jail_turn`, when a player voluntarily chooses to pay the $50 jail fine, the code calls `self.bank.collect(JAIL_FINE)` but completely forgets to call `player.deduct_money(JAIL_FINE)`. The bank receives $50 from nowhere, and the player gets out without losing any money. (Note: The mandatory release on turn 3 correctly deducts the money).
- **Logical Issue: Cannot try to roll doubles.** Standard rules dictate players can attempt to roll doubles to escape jail freely. The `_handle_jail_turn` forces them to skip their rolling phase altogether if they decide not to pay or use a card, meaning they are just artificially stuck for 3 turns.

## Conclusion
The white-box structure coverage ensures not just the "happy paths" are walked, but verifies complex if/else and dependency graphs across module lines. The 7 core bugs discovered represent significant mechanical failures that simple black-box playtesting might easily misdiagnose or overlook entirely.
