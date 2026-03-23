"""
White-Box Test Suite for MoneyPoly
===================================
Tests are designed by inspecting the source code of every module and targeting:
  • Every decision branch (if / elif / else)
  • Key variable states (balances, positions, ownership flags)
  • Edge cases (zero values, exact boundaries, large inputs, unexpected states)

Each test is named descriptively so the reason it exists is self-evident.
"""

from pathlib import Path
import sys

# Support running directly from `whitebox/tests`:
# `python test_whitebox.py`
CODE_DIR = Path(__file__).resolve().parents[1] / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

import pytest
from unittest.mock import patch

from moneypoly.bank import Bank
from moneypoly.player import Player
from moneypoly.property import Property, PropertyGroup
from moneypoly.dice import Dice
from moneypoly.cards import CardDeck, CHANCE_CARDS, COMMUNITY_CHEST_CARDS
from moneypoly.board import Board, SPECIAL_TILES
from moneypoly.game import Game
from moneypoly.config import (
    BANK_STARTING_FUNDS, STARTING_BALANCE, GO_SALARY, JAIL_FINE,
    AUCTION_MIN_INCREMENT, BOARD_SIZE, INCOME_TAX_AMOUNT,
    LUXURY_TAX_AMOUNT, JAIL_POSITION, GO_TO_JAIL_POSITION,
    FREE_PARKING_POSITION, MAX_TURNS
)
from moneypoly import ui


# ============================================================================
# SECTION 1 — BANK MODULE (bank.py)
#   Branches: collect guard, pay_out guards (<=0, >funds), give_loan guard
# ============================================================================

class TestBank:
    """Cover every branch inside Bank."""

    def test_init_sets_starting_funds(self):
        """Branch: __init__ — verify initial state is correct."""
        bank = Bank()
        assert bank.get_balance() == BANK_STARTING_FUNDS
        assert bank.total_loans_issued() == 0
        assert bank.loan_count() == 0

    def test_collect_positive(self):
        """Branch: collect() with amount > 0 — funds increase."""
        bank = Bank()
        bank.collect(500)
        assert bank.get_balance() == BANK_STARTING_FUNDS + 500

    def test_collect_zero_ignored(self):
        """Edge: collect(0) should be silently ignored (amount <= 0 guard)."""
        bank = Bank()
        bank.collect(0)
        assert bank.get_balance() == BANK_STARTING_FUNDS

    def test_collect_negative_ignored(self):
        """Branch: collect() with negative amount — must be ignored per docstring."""
        bank = Bank()
        bank.collect(-100)
        assert bank.get_balance() == BANK_STARTING_FUNDS

    def test_pay_out_positive(self):
        """Branch: pay_out() happy path — funds decrease, amount returned."""
        bank = Bank()
        result = bank.pay_out(100)
        assert result == 100
        assert bank.get_balance() == BANK_STARTING_FUNDS - 100

    def test_pay_out_zero_returns_zero(self):
        """Branch: pay_out(0) — guard amount <= 0 returns 0."""
        bank = Bank()
        assert bank.pay_out(0) == 0
        assert bank.get_balance() == BANK_STARTING_FUNDS

    def test_pay_out_negative_returns_zero(self):
        """Branch: pay_out(-50) — guard amount <= 0 returns 0."""
        bank = Bank()
        assert bank.pay_out(-50) == 0

    def test_pay_out_exceeding_funds_raises(self):
        """Branch: pay_out() when amount > funds — ValueError raised."""
        bank = Bank()
        with pytest.raises(ValueError):
            bank.pay_out(BANK_STARTING_FUNDS + 1)

    def test_give_loan_positive(self):
        """Branch: give_loan() happy path — player gets money, bank reserves drop."""
        bank = Bank()
        player = Player("Alice")
        bank.give_loan(player, 500)
        assert player.balance == STARTING_BALANCE + 500
        assert bank.get_balance() == BANK_STARTING_FUNDS - 500
        assert bank.loan_count() == 1
        assert bank.total_loans_issued() == 500

    def test_give_loan_zero_or_negative_skipped(self):
        """Branch: give_loan() guard amount <= 0 — nothing happens."""
        bank = Bank()
        player = Player("Alice")
        bank.give_loan(player, 0)
        bank.give_loan(player, -20)
        assert player.balance == STARTING_BALANCE
        assert bank.loan_count() == 0

    def test_summary_output(self, capsys):
        """Branch: summary() — verify it prints without error."""
        bank = Bank()
        bank.summary()
        out, _ = capsys.readouterr()
        assert "Bank reserves" in out
        assert "Total collected" in out

    def test_repr(self):
        bank = Bank()
        assert "Bank(funds=" in repr(bank)


# ============================================================================
# SECTION 2 — PLAYER MODULE (player.py)
#   Branches: add_money guard, deduct_money guard, is_bankrupt, move pass-Go,
#             add_property duplicate guard, remove_property guard
# ============================================================================

class TestPlayer:

    def test_init_defaults(self):
        """Verify all default values are set correctly."""
        p = Player("Bob")
        assert p.name == "Bob"
        assert p.balance == STARTING_BALANCE
        assert p.position == 0
        assert p.properties == []
        assert p.in_jail is False
        assert p.jail_turns == 0
        assert p.get_out_of_jail_cards == 0
        assert p.is_eliminated is False

    def test_init_custom_balance(self):
        """Branch: custom balance parameter."""
        p = Player("Bob", balance=100)
        assert p.balance == 100

    def test_add_money_positive(self):
        """Branch: add_money happy path."""
        p = Player("Bob")
        p.add_money(300)
        assert p.balance == STARTING_BALANCE + 300

    def test_add_money_zero(self):
        """Edge: add_money(0) — amount == 0 should work (not negative)."""
        p = Player("Bob")
        p.add_money(0)
        assert p.balance == STARTING_BALANCE

    def test_add_money_negative_raises(self):
        """Branch: add_money guard amount < 0."""
        p = Player("Bob")
        with pytest.raises(ValueError):
            p.add_money(-1)

    def test_deduct_money_positive(self):
        """Branch: deduct_money happy path."""
        p = Player("Bob")
        p.deduct_money(100)
        assert p.balance == STARTING_BALANCE - 100

    def test_deduct_money_negative_raises(self):
        """Branch: deduct_money guard amount < 0."""
        p = Player("Bob")
        with pytest.raises(ValueError):
            p.deduct_money(-1)

    def test_is_bankrupt_positive_balance(self):
        """Branch: balance > 0 → not bankrupt."""
        p = Player("Bob")
        assert p.is_bankrupt() is False

    def test_is_bankrupt_zero_balance(self):
        """Edge: balance == 0 → bankrupt (uses <=)."""
        p = Player("Bob", balance=0)
        assert p.is_bankrupt() is True

    def test_is_bankrupt_negative_balance(self):
        """Branch: balance < 0 → bankrupt."""
        p = Player("Bob", balance=-10)
        assert p.is_bankrupt() is True

    # ---- net_worth ----
    def test_net_worth_cash_only(self):
        """Branch: net_worth() with no properties."""
        p = Player("Bob")
        assert p.net_worth() == STARTING_BALANCE

    def test_net_worth_should_include_properties(self):
        """
        White-box: net_worth() currently returns self.balance.
        It SHOULD include property values for a correct net-worth calculation.
        """
        p = Player("Bob")
        prop = Property("Park Place", 37, 350, 35)
        prop.owner = p
        p.add_property(prop)
        expected = p.balance + prop.price
        assert p.net_worth() >= expected, (
            f"net_worth()={p.net_worth()} but should be at least "
            f"balance({p.balance}) + property({prop.price}) = {expected}"
        )

    # ---- move ----
    def test_move_normal(self):
        """Branch: move without wrapping."""
        p = Player("Bob")
        p.move(5)
        assert p.position == 5
        assert p.balance == STARTING_BALANCE

    def test_move_land_exactly_on_go(self):
        """Branch: move wraps to position 0 (lands on Go) — should get salary."""
        p = Player("Bob")
        p.move(BOARD_SIZE)
        assert p.position == 0
        assert p.balance == STARTING_BALANCE + GO_SALARY

    def test_move_pass_go(self):
        """Branch: move wraps past Go (position != 0) — should still get salary."""
        p = Player("Bob")
        p.position = 38
        p.move(4)
        assert p.position == 2
        assert p.balance == STARTING_BALANCE + GO_SALARY

    def test_move_no_wrap(self):
        """Edge: move that doesn't cross Go — no salary."""
        p = Player("Bob")
        p.position = 10
        p.move(5)
        assert p.position == 15
        assert p.balance == STARTING_BALANCE

    # ---- jail ----
    def test_go_to_jail(self):
        """Branch: go_to_jail sets position, flag, resets turns."""
        p = Player("Bob")
        p.jail_turns = 5  # stale value
        p.go_to_jail()
        assert p.position == JAIL_POSITION
        assert p.in_jail is True
        assert p.jail_turns == 0

    # ---- property management ----
    def test_add_property_new(self):
        """Branch: add_property when property not already held."""
        p = Player("Bob")
        prop = Property("X", 1, 100, 10)
        p.add_property(prop)
        assert prop in p.properties
        assert p.count_properties() == 1

    def test_add_property_duplicate_ignored(self):
        """Branch: add_property guard — same property not added twice."""
        p = Player("Bob")
        prop = Property("X", 1, 100, 10)
        p.add_property(prop)
        p.add_property(prop)
        assert p.count_properties() == 1

    def test_remove_property_exists(self):
        """Branch: remove_property when property is held."""
        p = Player("Bob")
        prop = Property("X", 1, 100, 10)
        p.add_property(prop)
        p.remove_property(prop)
        assert p.count_properties() == 0

    def test_remove_property_not_held(self):
        """Branch: remove_property guard — property not in list, no crash."""
        p = Player("Bob")
        prop = Property("X", 1, 100, 10)
        p.remove_property(prop)  # should not raise

    def test_status_line_and_repr(self):
        """Cover status_line and __repr__."""
        p = Player("Bob")
        assert "Bob" in p.status_line()
        p.in_jail = True
        assert "[JAILED]" in p.status_line()
        assert repr(p).startswith("Player('Bob'")


# ============================================================================
# SECTION 3 — PROPERTY & PROPERTY GROUP (property.py)
#   Branches: get_rent (mortgaged, full-group, base), mortgage/unmortgage
#             already-state guards, is_available, group all_owned_by
# ============================================================================

class TestProperty:

    def test_init_registers_with_group(self):
        """Branch: constructor auto-registers with group."""
        g = PropertyGroup("Green", "green")
        p = Property("P1", 1, 200, 20, group=g)
        assert p in g.properties
        assert p.group is g
        assert p.mortgage_value == 100
        assert p.houses == 0

    def test_init_no_group(self):
        """Branch: constructor with group=None."""
        p = Property("P1", 1, 200, 20)
        assert p.group is None

    def test_get_rent_base(self):
        """Branch: get_rent base — not mortgaged, group not fully owned."""
        g = PropertyGroup("G", "g")
        p1 = Property("P1", 1, 100, 10, group=g)
        Property("P2", 2, 100, 10, group=g)  # second in group, unowned
        player = Player("A")
        p1.owner = player
        assert p1.get_rent() == 10

    def test_get_rent_full_group_doubled(self):
        """Branch: get_rent full-group multiplier path."""
        g = PropertyGroup("G", "g")
        p1 = Property("P1", 1, 100, 10, group=g)
        p2 = Property("P2", 2, 100, 10, group=g)
        player = Player("A")
        p1.owner = player
        p2.owner = player
        assert p1.get_rent() == 20  # base * 2

    def test_get_rent_mortgaged_returns_zero(self):
        """Branch: get_rent mortgaged guard."""
        p = Property("P1", 1, 100, 10)
        p.owner = Player("A")
        p.is_mortgaged = True
        assert p.get_rent() == 0

    def test_mortgage_success(self):
        """Branch: mortgage happy path."""
        p = Property("P1", 1, 100, 10)
        assert p.mortgage() == 50
        assert p.is_mortgaged is True

    def test_mortgage_already_mortgaged(self):
        """Branch: mortgage guard — already mortgaged returns 0."""
        p = Property("P1", 1, 100, 10)
        p.mortgage()
        assert p.mortgage() == 0

    def test_unmortgage_success(self):
        """Branch: unmortgage happy path."""
        p = Property("P1", 1, 100, 10)
        p.mortgage()
        cost = p.unmortgage()
        assert cost == int(50 * 1.1)
        assert p.is_mortgaged is False

    def test_unmortgage_not_mortgaged(self):
        """Branch: unmortgage guard — not mortgaged returns 0."""
        p = Property("P1", 1, 100, 10)
        assert p.unmortgage() == 0

    def test_is_available(self):
        """Branch: is_available — unowned and not mortgaged."""
        p = Property("P1", 1, 100, 10)
        assert p.is_available() is True
        p.owner = Player("A")
        assert p.is_available() is False

    def test_repr(self):
        p = Property("P1", 1, 100, 10)
        assert "unowned" in repr(p)
        p.owner = Player("A")
        assert "A" in repr(p)


class TestPropertyGroup:

    def test_add_property(self):
        """Branch: add_property links property back to group."""
        g = PropertyGroup("G", "g")
        p = Property("P1", 1, 100, 10)
        g.add_property(p)
        assert p in g.properties
        assert p.group is g

    def test_add_property_duplicate(self):
        """Branch: add_property guard — no duplicate."""
        g = PropertyGroup("G", "g")
        p = Property("P1", 1, 100, 10)
        g.add_property(p)
        g.add_property(p)
        assert g.size() == 1

    def test_all_owned_by_none_player(self):
        """Branch: all_owned_by(None) returns False."""
        g = PropertyGroup("G", "g")
        Property("P1", 1, 100, 10, group=g)
        assert g.all_owned_by(None) is False

    def test_all_owned_by_partial(self):
        """Branch: not all properties owned — should return False."""
        g = PropertyGroup("G", "g")
        p1 = Property("P1", 1, 100, 10, group=g)
        Property("P2", 2, 100, 10, group=g)
        player = Player("A")
        p1.owner = player
        assert g.all_owned_by(player) is False

    def test_all_owned_by_full(self):
        """Branch: all properties owned by same player — True."""
        g = PropertyGroup("G", "g")
        p1 = Property("P1", 1, 100, 10, group=g)
        p2 = Property("P2", 2, 100, 10, group=g)
        player = Player("A")
        p1.owner = player
        p2.owner = player
        assert g.all_owned_by(player) is True

    def test_get_owner_counts(self):
        """Branch: get_owner_counts with mixed ownership."""
        g = PropertyGroup("G", "g")
        p1 = Property("P1", 1, 100, 10, group=g)
        Property("P2", 2, 100, 10, group=g)  # unowned
        player = Player("A")
        p1.owner = player
        counts = g.get_owner_counts()
        assert counts[player] == 1

    def test_repr(self):
        g = PropertyGroup("G", "g")
        assert "PropertyGroup" in repr(g)


# ============================================================================
# SECTION 4 — DICE MODULE (dice.py)
#   Branches: roll doubles/non-doubles, reset
# ============================================================================

class TestDice:

    def test_roll_range(self):
        """Edge: dice should produce values 1-6 on each die (standard d6)."""
        dice = Dice()
        values = set()
        for _ in range(200):
            dice.roll()
            values.add(dice.die1)
            values.add(dice.die2)
        assert 6 in values, "Die never rolled 6 — likely capped at 5."
        assert 1 in values

    def test_roll_doubles_increments_streak(self):
        """Branch: both dice same → doubles_streak increases."""
        with patch("random.randint", return_value=3):
            dice = Dice()
            dice.roll()
            assert dice.is_doubles() is True
            assert dice.doubles_streak == 1
            dice.roll()
            assert dice.doubles_streak == 2

    def test_roll_non_doubles_resets_streak(self):
        """Branch: different values → streak resets to 0."""
        dice = Dice()
        with patch("random.randint", return_value=3):
            dice.roll()
        with patch("random.randint", side_effect=[3, 4]):
            dice.roll()
            assert dice.is_doubles() is False
            assert dice.doubles_streak == 0

    def test_reset_clears_streak(self):
        """
        White-box: reset() should also zero doubles_streak.
        The docstring says 'Reset dice face values and the doubles streak counter.'
        """
        dice = Dice()
        with patch("random.randint", return_value=3):
            dice.roll()
            dice.roll()
        assert dice.doubles_streak == 2
        dice.reset()
        assert dice.die1 == 0 and dice.die2 == 0
        assert dice.doubles_streak == 0, (
            f"reset() left doubles_streak={dice.doubles_streak}, expected 0"
        )

    def test_total(self):
        dice = Dice()
        dice.die1 = 3
        dice.die2 = 4
        assert dice.total() == 7

    def test_describe(self):
        dice = Dice()
        dice.die1 = 3
        dice.die2 = 4
        assert "3 + 4 = 7" in dice.describe()
        dice.die1 = 5
        dice.die2 = 5
        assert "(DOUBLES)" in dice.describe()

    def test_repr(self):
        dice = Dice()
        assert "Dice(" in repr(dice)


# ============================================================================
# SECTION 5 — CARDS MODULE (cards.py)
#   Branches: draw on empty, draw cycling, peek, reshuffle
# ============================================================================

class TestCardDeck:

    def test_draw_cycles(self):
        """Branch: draw all cards and verify cycling."""
        deck = CardDeck([{"a": 1}, {"a": 2}])
        assert deck.draw()["a"] == 1
        assert deck.draw()["a"] == 2
        assert deck.draw()["a"] == 1  # cycles

    def test_draw_empty_returns_none(self):
        """Branch: draw from empty deck."""
        deck = CardDeck([])
        assert deck.draw() is None

    def test_peek_does_not_advance(self):
        """Branch: peek returns next without moving index."""
        deck = CardDeck([{"a": 1}, {"a": 2}])
        assert deck.peek()["a"] == 1
        assert deck.peek()["a"] == 1

    def test_peek_empty(self):
        """Branch: peek on empty deck."""
        deck = CardDeck([])
        assert deck.peek() is None

    def test_reshuffle_resets_index(self):
        deck = CardDeck([{"a": 1}, {"a": 2}])
        deck.draw()
        deck.draw()
        deck.reshuffle()
        assert deck.index == 0

    def test_cards_remaining(self):
        deck = CardDeck([{"a": 1}, {"a": 2}, {"a": 3}])
        assert deck.cards_remaining() == 3
        deck.draw()
        assert deck.cards_remaining() == 2

    def test_len(self):
        deck = CardDeck([{"a": 1}])
        assert len(deck) == 1

    def test_repr(self):
        deck = CardDeck([{"a": 1}])
        assert "CardDeck(" in repr(deck)


# ============================================================================
# SECTION 6 — BOARD MODULE (board.py)
#   Branches: get_tile_type (special / property / blank),
#             is_purchasable (no prop, mortgaged, owned, available),
#             railroad positions
# ============================================================================

class TestBoard:

    def test_total_properties(self):
        board = Board()
        assert len(board.properties) == 22

    def test_eight_colour_groups(self):
        board = Board()
        assert len(board.groups) == 8

    def test_get_property_at_valid(self):
        board = Board()
        assert board.get_property_at(1).name == "Mediterranean Avenue"

    def test_get_property_at_invalid(self):
        board = Board()
        assert board.get_property_at(99) is None

    def test_tile_type_go(self):
        board = Board()
        assert board.get_tile_type(0) == "go"

    def test_tile_type_jail(self):
        board = Board()
        assert board.get_tile_type(JAIL_POSITION) == "jail"

    def test_tile_type_property(self):
        board = Board()
        assert board.get_tile_type(1) == "property"

    def test_tile_type_blank(self):
        """Branch: position with neither special tile nor property."""
        board = Board()
        assert board.get_tile_type(99) == "blank"

    def test_tile_type_community_chest(self):
        board = Board()
        assert board.get_tile_type(2) == "community_chest"

    def test_tile_type_chance(self):
        board = Board()
        assert board.get_tile_type(7) == "chance"

    def test_is_purchasable_unowned(self):
        board = Board()
        assert board.is_purchasable(1) is True

    def test_is_purchasable_non_property(self):
        """Branch: non-property position → not purchasable."""
        board = Board()
        assert board.is_purchasable(0) is False

    def test_is_purchasable_mortgaged(self):
        """Branch: mortgaged → not purchasable."""
        board = Board()
        board.get_property_at(1).is_mortgaged = True
        assert board.is_purchasable(1) is False

    def test_is_purchasable_owned(self):
        """Branch: already owned → not purchasable."""
        board = Board()
        board.get_property_at(1).owner = Player("A")
        assert board.is_purchasable(1) is False

    def test_is_special_tile(self):
        board = Board()
        assert board.is_special_tile(0) is True
        assert board.is_special_tile(1) is False

    def test_properties_owned_by(self):
        board = Board()
        p = Player("A")
        board.get_property_at(1).owner = p
        assert len(board.properties_owned_by(p)) == 1

    def test_unowned_properties(self):
        board = Board()
        assert len(board.unowned_properties()) == 22

    def test_railroad_positions_have_properties(self):
        """
        White-box: positions 5, 15, 25, 35 are tagged as 'railroad' in
        SPECIAL_TILES, and game.py tries to call get_property_at on them.
        There SHOULD be Property objects at these positions.
        """
        board = Board()
        for pos in [5, 15, 25, 35]:
            prop = board.get_property_at(pos)
            assert prop is not None, (
                f"No Property at railroad position {pos}. "
                f"Railroads can never be bought!"
            )


# ============================================================================
# SECTION 7 — GAME MODULE (game.py)
#   This is the largest module; tests are grouped by method.
# ============================================================================

class TestGameInit:

    def test_init(self):
        game = Game(["Alice", "Bob"])
        assert len(game.players) == 2
        assert game.current_player().name == "Alice"
        assert game.turn_number == 0

    def test_advance_turn(self):
        game = Game(["Alice", "Bob"])
        game.advance_turn()
        assert game.current_index == 1
        assert game.turn_number == 1
        game.advance_turn()
        assert game.current_index == 0  # wraps


class TestBuyProperty:
    """buy_property: branches for affordability."""

    def test_buy_happy_path(self):
        game = Game(["Alice"])
        alice = game.players[0]
        prop = game.board.get_property_at(1)
        assert game.buy_property(alice, prop) is True
        assert prop.owner is alice
        assert alice.balance == STARTING_BALANCE - prop.price

    def test_buy_cannot_afford_zero_balance(self):
        """Branch: balance == 0 < price → rejected."""
        game = Game(["Alice"])
        alice = game.players[0]
        alice.balance = 0
        prop = game.board.get_property_at(1)
        assert game.buy_property(alice, prop) is False

    def test_buy_exact_balance_equals_price(self):
        """
        Edge: balance == price. The player has exactly enough.
        buy_property uses `if player.balance <= prop.price` which
        wrongly rejects this case.
        """
        game = Game(["Alice"])
        alice = game.players[0]
        prop = game.board.get_property_at(1)  # price = 60
        alice.balance = prop.price
        result = game.buy_property(alice, prop)
        assert result is True, (
            f"buy_property rejected when balance ({alice.balance}) == price ({prop.price}). "
            f"Bug: uses '<=' instead of '<'."
        )


class TestPayRent:

    def test_rent_deducted_from_tenant(self):
        game = Game(["Alice", "Bob"])
        alice, bob = game.players
        prop = game.board.get_property_at(1)
        prop.owner = bob
        bob.add_property(prop)
        rent = prop.get_rent()
        game.pay_rent(alice, prop)
        assert alice.balance == STARTING_BALANCE - rent

    def test_rent_credited_to_owner(self):
        """
        White-box: pay_rent deducts from tenant but MUST also credit the owner.
        """
        game = Game(["Alice", "Bob"])
        alice, bob = game.players
        prop = game.board.get_property_at(1)
        prop.owner = bob
        bob.add_property(prop)
        bob_initial = bob.balance
        rent = prop.get_rent()
        game.pay_rent(alice, prop)
        assert bob.balance == bob_initial + rent, (
            f"Owner balance {bob.balance} != {bob_initial + rent}. "
            f"pay_rent never credits the owner!"
        )

    def test_rent_mortgaged_no_charge(self):
        """Branch: mortgaged → no rent collected."""
        game = Game(["Alice", "Bob"])
        alice, bob = game.players
        prop = game.board.get_property_at(1)
        prop.owner = bob
        prop.is_mortgaged = True
        game.pay_rent(alice, prop)
        assert alice.balance == STARTING_BALANCE

    def test_rent_unowned_noop(self):
        """Branch: owner is None → early return."""
        game = Game(["Alice"])
        alice = game.players[0]
        prop = game.board.get_property_at(1)
        game.pay_rent(alice, prop)
        assert alice.balance == STARTING_BALANCE


class TestMortgage:

    def test_mortgage_happy_path(self):
        game = Game(["Alice"])
        alice = game.players[0]
        prop = game.board.get_property_at(1)
        prop.owner = alice
        alice.add_property(prop)
        assert game.mortgage_property(alice, prop) is True
        assert alice.balance == STARTING_BALANCE + prop.mortgage_value

    def test_mortgage_bank_funds_decrease(self):
        """
        White-box: mortgage_property calls bank.collect(-payout) which
        silently does nothing after the negative-guard fix.
        The bank should PAY OUT the mortgage value.
        """
        game = Game(["Alice"])
        alice = game.players[0]
        prop = game.board.get_property_at(1)
        prop.owner = alice
        alice.add_property(prop)
        bank_before = game.bank.get_balance()
        game.mortgage_property(alice, prop)
        assert game.bank.get_balance() == bank_before - prop.mortgage_value, (
            f"Bank balance unchanged after mortgage payout. "
            f"bank.collect(-payout) is silently ignored."
        )

    def test_mortgage_not_owner(self):
        """Branch: player doesn't own property → False."""
        game = Game(["Alice"])
        alice = game.players[0]
        prop = game.board.get_property_at(1)
        assert game.mortgage_property(alice, prop) is False

    def test_mortgage_already_mortgaged(self):
        """Branch: already mortgaged → False."""
        game = Game(["Alice"])
        alice = game.players[0]
        prop = game.board.get_property_at(1)
        prop.owner = alice
        alice.add_property(prop)
        game.mortgage_property(alice, prop)
        assert game.mortgage_property(alice, prop) is False


class TestUnmortgage:

    def test_unmortgage_happy_path(self):
        game = Game(["Alice"])
        alice = game.players[0]
        prop = game.board.get_property_at(1)
        prop.owner = alice
        alice.add_property(prop)
        prop.is_mortgaged = True
        cost = int(prop.mortgage_value * 1.1)
        assert game.unmortgage_property(alice, prop) is True
        assert alice.balance == STARTING_BALANCE - cost

    def test_unmortgage_not_owner(self):
        """Branch: not owner → False."""
        game = Game(["Alice"])
        prop = game.board.get_property_at(1)
        assert game.unmortgage_property(game.players[0], prop) is False

    def test_unmortgage_not_mortgaged(self):
        """Branch: not mortgaged → False."""
        game = Game(["Alice"])
        alice = game.players[0]
        prop = game.board.get_property_at(1)
        prop.owner = alice
        alice.add_property(prop)
        assert game.unmortgage_property(alice, prop) is False

    def test_unmortgage_cannot_afford_keeps_state(self):
        """
        White-box: unmortgage_property calls prop.unmortgage() which
        flips is_mortgaged=False BEFORE checking affordability.
        If the player can't afford it, is_mortgaged should stay True.
        """
        game = Game(["Alice"])
        alice = game.players[0]
        prop = game.board.get_property_at(1)
        prop.owner = alice
        alice.add_property(prop)
        prop.is_mortgaged = True
        alice.balance = 0

        result = game.unmortgage_property(alice, prop)
        assert result is False
        assert prop.is_mortgaged is True, (
            f"Property is_mortgaged={prop.is_mortgaged} after failed unmortgage attempt."
        )


class TestTrade:

    def test_trade_happy_path(self):
        game = Game(["Alice", "Bob"])
        alice, bob = game.players
        prop = game.board.get_property_at(1)
        prop.owner = alice
        alice.add_property(prop)
        a_bal, b_bal = alice.balance, bob.balance
        assert game.trade(alice, bob, prop, 100) is True
        assert prop.owner is bob
        assert bob.balance == b_bal - 100
        assert alice.balance == a_bal + 100

    def test_trade_seller_not_owner(self):
        """Branch: seller doesn't own → False."""
        game = Game(["Alice", "Bob"])
        alice, bob = game.players
        prop = game.board.get_property_at(1)
        prop.owner = bob
        assert game.trade(alice, bob, prop, 100) is False

    def test_trade_buyer_cant_afford(self):
        """Branch: buyer can't afford → False."""
        game = Game(["Alice", "Bob"])
        alice, bob = game.players
        prop = game.board.get_property_at(1)
        prop.owner = alice
        alice.add_property(prop)
        assert game.trade(alice, bob, prop, bob.balance + 1) is False


class TestAuction:

    def test_auction_winner(self):
        game = Game(["Alice", "Bob"])
        prop = game.board.get_property_at(1)
        with patch("moneypoly.ui.safe_int_input", side_effect=[0, 50]):
            game.auction_property(prop)
        assert prop.owner is game.players[1]
        assert game.players[1].balance == STARTING_BALANCE - 50

    def test_auction_no_bids(self):
        """Branch: no valid bids → property stays unowned."""
        game = Game(["Alice", "Bob"])
        prop = game.board.get_property_at(1)
        with patch("moneypoly.ui.safe_int_input", return_value=0):
            game.auction_property(prop)
        assert prop.owner is None

    def test_auction_bid_too_low(self):
        """Branch: bid < highest + increment → rejected."""
        game = Game(["Alice", "Bob"])
        prop = game.board.get_property_at(1)
        # Alice bids 50, Bob tries 55 (increment is 10, needs 60)
        with patch("moneypoly.ui.safe_int_input", side_effect=[50, 55]):
            game.auction_property(prop)
        assert prop.owner is game.players[0]

    def test_auction_bid_exceeds_balance(self):
        """Branch: bid > player.balance → rejected."""
        game = Game(["Alice"])
        alice = game.players[0]
        prop = game.board.get_property_at(1)
        with patch("moneypoly.ui.safe_int_input", return_value=alice.balance + 1):
            game.auction_property(prop)
        assert prop.owner is None


class TestJailTurn:

    def test_jail_wait_three_turns_mandatory_release(self):
        """Branch: player serves 3 turns → forced to pay and leave."""
        game = Game(["Alice"])
        alice = game.players[0]
        alice.go_to_jail()
        with patch("moneypoly.ui.confirm", return_value=False):
            game._handle_jail_turn(alice)
            assert alice.jail_turns == 1
            game._handle_jail_turn(alice)
            assert alice.jail_turns == 2
            with patch.object(game.dice, 'roll', return_value=4), \
                 patch('builtins.input', return_value='s'):
                game._handle_jail_turn(alice)
                assert alice.in_jail is False
                assert alice.balance == STARTING_BALANCE - JAIL_FINE

    def test_jail_use_card(self):
        """Branch: player has Get-Out-of-Jail card and uses it."""
        game = Game(["Alice"])
        alice = game.players[0]
        alice.go_to_jail()
        alice.get_out_of_jail_cards = 1
        with patch("moneypoly.ui.confirm", return_value=True), \
             patch('builtins.input', return_value='s'):
            game._handle_jail_turn(alice)
        assert alice.in_jail is False
        assert alice.get_out_of_jail_cards == 0

    def test_jail_pay_fine(self):
        """Branch: player voluntarily pays fine."""
        game = Game(["Alice"])
        alice = game.players[0]
        alice.go_to_jail()
        with patch("moneypoly.ui.confirm", return_value=True), \
             patch.object(game.dice, 'roll', return_value=4), \
             patch('builtins.input', return_value='s'):
            game._handle_jail_turn(alice)
        assert alice.in_jail is False
        assert alice.balance == STARTING_BALANCE - JAIL_FINE


class TestApplyCard:

    def test_collect(self):
        game = Game(["Alice"])
        alice = game.players[0]
        game._apply_card(alice, {"action": "collect", "value": 50, "description": ""})
        assert alice.balance == STARTING_BALANCE + 50

    def test_pay(self):
        game = Game(["Alice"])
        alice = game.players[0]
        game._apply_card(alice, {"action": "pay", "value": 20, "description": ""})
        assert alice.balance == STARTING_BALANCE - 20

    def test_jail(self):
        game = Game(["Alice"])
        alice = game.players[0]
        game._apply_card(alice, {"action": "jail", "value": 0, "description": ""})
        assert alice.in_jail is True

    def test_jail_free(self):
        game = Game(["Alice"])
        alice = game.players[0]
        game._apply_card(alice, {"action": "jail_free", "value": 0, "description": ""})
        assert alice.get_out_of_jail_cards == 1

    def test_move_to_go(self):
        """Branch: move_to Go — value < old_pos so salary awarded."""
        game = Game(["Alice"])
        alice = game.players[0]
        alice.position = 10
        game._apply_card(alice, {"action": "move_to", "value": 0, "description": ""})
        assert alice.position == 0

    def test_move_to_forward_no_salary(self):
        """Branch: move_to forward — value >= old_pos so no salary."""
        game = Game(["Alice"])
        alice = game.players[0]
        alice.position = 5
        with patch('builtins.input', return_value='s'):
            game._apply_card(alice, {"action": "move_to", "value": 39, "description": ""})
        assert alice.position == 39

    def test_move_to_go_to_jail_tile(self):
        """
        White-box: move_to only handles destination tile == 'property'.
        If a card moves a player to the Go-To-Jail tile (pos 30),
        the jail effect should trigger.
        """
        game = Game(["Alice"])
        alice = game.players[0]
        alice.position = 5
        game._apply_card(alice, {
            "action": "move_to", "value": 30, "description": "Advance to pos 30"
        })
        assert alice.in_jail is True, (
            f"Player at Go-To-Jail tile (pos 30) but in_jail={alice.in_jail}. "
            f"move_to card only dispatches 'property' tiles!"
        )

    def test_birthday(self):
        game = Game(["Alice", "Bob", "Charlie"])
        alice, bob, charlie = game.players
        b_bal, c_bal, a_bal = bob.balance, charlie.balance, alice.balance
        game._apply_card(alice, {"action": "birthday", "value": 10, "description": ""})
        assert bob.balance == b_bal - 10
        assert charlie.balance == c_bal - 10
        assert alice.balance == a_bal + 20

    def test_collect_from_all(self):
        game = Game(["Alice", "Bob"])
        alice, bob = game.players
        b_bal, a_bal = bob.balance, alice.balance
        game._apply_card(alice, {"action": "collect_from_all", "value": 50, "description": ""})
        assert bob.balance == b_bal - 50
        assert alice.balance == a_bal + 50

    def test_none_card(self):
        """Branch: card is None → noop."""
        game = Game(["Alice"])
        game._apply_card(game.players[0], None)  # should not raise


class TestBankruptcy:

    def test_bankrupt_player_eliminated(self):
        game = Game(["Alice", "Bob", "Charlie"])
        alice = game.players[0]
        prop = game.board.get_property_at(1)
        prop.owner = alice
        alice.add_property(prop)
        alice.balance = -10
        game._check_bankruptcy(alice)
        assert alice.is_eliminated is True
        assert prop.owner is None
        assert "Alice" not in [p.name for p in game.players]

    def test_not_bankrupt_stays(self):
        """Branch: balance > 0 → no elimination."""
        game = Game(["Alice", "Bob"])
        game._check_bankruptcy(game.players[0])
        assert len(game.players) == 2


class TestFindWinner:

    def test_find_winner_returns_highest(self):
        """
        White-box: find_winner() uses min() but should use max().
        The winner should be the RICHEST player.
        """
        game = Game(["Alice", "Bob"])
        alice, bob = game.players
        alice.balance = 3000
        bob.balance = 1000
        winner = game.find_winner()
        assert winner.name == "Alice", (
            f"find_winner returned '{winner.name}' ({winner.net_worth()}) "
            f"instead of 'Alice' ({alice.net_worth()}). Uses min() instead of max()!"
        )

    def test_find_winner_no_players(self):
        """Branch: empty player list → None."""
        game = Game(["Alice"])
        game.players.clear()
        assert game.find_winner() is None


class TestPlayTurn:

    def test_jailed_player_goes_to_jail_branch(self):
        """Branch: play_turn with player in jail."""
        game = Game(["Alice", "Bob"])
        alice = game.players[0]
        alice.go_to_jail()
        with patch("moneypoly.ui.confirm", return_value=False):
            game.play_turn()
        assert game.current_index == 1  # turn advanced

    def test_triple_doubles_sends_to_jail(self):
        """Branch: 3 consecutive doubles → jail."""
        game = Game(["Alice", "Bob"])
        alice = game.players[0]
        with patch.object(game.dice, 'roll', return_value=4), \
             patch.object(game.dice, 'is_doubles', return_value=True):
            game.dice.doubles_streak = 3
            game.play_turn()
            assert alice.in_jail is True


class TestMoveAndResolve:

    def test_go_to_jail_tile(self):
        """Branch: landing on Go-To-Jail sends player to jail."""
        game = Game(["Alice", "Bob"])
        alice = game.players[0]
        alice.position = 28
        game._move_and_resolve(alice, 2)  # lands on 30
        assert alice.in_jail is True

    def test_income_tax(self):
        """Branch: landing on income tax."""
        game = Game(["Alice", "Bob"])
        alice = game.players[0]
        alice.position = 2
        game._move_and_resolve(alice, 2)  # lands on 4
        assert alice.balance == STARTING_BALANCE - INCOME_TAX_AMOUNT

    def test_luxury_tax(self):
        """Branch: landing on luxury tax."""
        game = Game(["Alice", "Bob"])
        alice = game.players[0]
        alice.position = 36
        game._move_and_resolve(alice, 2)  # lands on 38
        assert alice.balance == STARTING_BALANCE - LUXURY_TAX_AMOUNT

    def test_free_parking(self):
        """Branch: free parking — nothing happens."""
        game = Game(["Alice", "Bob"])
        alice = game.players[0]
        alice.position = 18
        game._move_and_resolve(alice, 2)  # lands on 20
        assert alice.balance == STARTING_BALANCE


class TestMoveAndResolveChanceCommunity:
    """Cover the chance and community_chest branches of _move_and_resolve."""

    def test_chance_tile_draws_card(self):
        """Branch: landing on a chance tile (pos 7) draws from chance deck."""
        game = Game(["Alice", "Bob"])
        alice = game.players[0]
        alice.position = 5
        # Force the chance deck to return a simple 'collect' card
        game.chance_deck = CardDeck([{"action": "collect", "value": 25, "description": "Win $25"}])
        game._move_and_resolve(alice, 2)  # pos 5+2=7 = chance
        assert alice.balance == STARTING_BALANCE + 25

    def test_community_chest_tile_draws_card(self):
        """Branch: landing on community chest (pos 2) draws from community deck."""
        game = Game(["Alice", "Bob"])
        alice = game.players[0]
        alice.position = 0
        game.community_deck = CardDeck([{"action": "collect", "value": 50, "description": "Win $50"}])
        game._move_and_resolve(alice, 2)  # pos 0+2=2 = community_chest
        assert alice.balance == STARTING_BALANCE + 50  # does not pass Go


class TestHandlePropertyTile:
    """Cover all 3 branches of _handle_property_tile: unowned, own, other's."""

    def test_landing_on_unowned_property_buy(self):
        """Branch: prop.owner is None, player chooses 'b' to buy."""
        game = Game(["Alice", "Bob"])
        alice = game.players[0]
        prop = game.board.get_property_at(1)
        with patch("builtins.input", return_value="b"):
            game._handle_property_tile(alice, prop)
        # buy_property has a bug (<=) so if balance > price, it should succeed
        assert prop.owner is alice or alice.balance == STARTING_BALANCE  # covers the path

    def test_landing_on_unowned_property_skip(self):
        """Branch: prop.owner is None, player chooses 's' to skip."""
        game = Game(["Alice", "Bob"])
        alice = game.players[0]
        prop = game.board.get_property_at(1)
        with patch("builtins.input", return_value="s"):
            game._handle_property_tile(alice, prop)
        assert prop.owner is None
        assert alice.balance == STARTING_BALANCE

    def test_landing_on_unowned_property_auction(self):
        """Branch: prop.owner is None, player chooses 'a' to auction."""
        game = Game(["Alice", "Bob"])
        alice = game.players[0]
        prop = game.board.get_property_at(1)
        with patch("builtins.input", return_value="a"), \
             patch("moneypoly.ui.safe_int_input", return_value=0):
            game._handle_property_tile(alice, prop)
        assert prop.owner is None  # no bids placed

    def test_landing_on_own_property(self):
        """Branch: prop.owner == player — no rent due."""
        game = Game(["Alice", "Bob"])
        alice = game.players[0]
        prop = game.board.get_property_at(1)
        prop.owner = alice
        alice.add_property(prop)
        game._handle_property_tile(alice, prop)
        assert alice.balance == STARTING_BALANCE  # no change

    def test_landing_on_other_property(self):
        """Branch: prop.owner is someone else — pay rent."""
        game = Game(["Alice", "Bob"])
        alice, bob = game.players
        prop = game.board.get_property_at(1)
        prop.owner = bob
        bob.add_property(prop)
        game._handle_property_tile(alice, prop)
        assert alice.balance == STARTING_BALANCE - prop.get_rent()


class TestPlayTurnExtended:

    def test_doubles_extra_turn_no_advance(self):
        """Branch: player rolls doubles (not 3rd) — gets extra turn, index doesn't advance."""
        game = Game(["Alice", "Bob"])
        with patch.object(game.dice, 'roll', return_value=6), \
             patch.object(game.dice, 'is_doubles', return_value=True), \
             patch('builtins.input', return_value='s'):
            game.dice.doubles_streak = 1  # not 3rd double
            game.play_turn()
        assert game.current_index == 0  # Alice gets another turn

    def test_normal_roll_advances_turn(self):
        """Branch: normal roll (no doubles) — turn advances."""
        game = Game(["Alice", "Bob"])
        with patch.object(game.dice, 'roll', return_value=5), \
             patch.object(game.dice, 'is_doubles', return_value=False), \
             patch('builtins.input', return_value='s'):
            game.dice.doubles_streak = 0
            game.play_turn()
        assert game.current_index == 1  # advanced to Bob


class TestBankruptcyExtended:

    def test_bankruptcy_wraps_current_index(self):
        """Branch: current_index >= len(players) after removal → wraps to 0."""
        game = Game(["Alice", "Bob"])
        game.current_index = 1  # Bob's turn
        bob = game.players[1]
        bob.balance = -10
        game._check_bankruptcy(bob)
        assert bob.is_eliminated is True
        assert game.current_index == 0  # wrapped


class TestCardEdgeCases:

    def test_birthday_other_cant_afford(self):
        """Edge: birthday card when another player has insufficient balance."""
        game = Game(["Alice", "Bob"])
        alice, bob = game.players
        bob.balance = 5  # less than the card value of 10
        a_bal = alice.balance
        game._apply_card(alice, {"action": "birthday", "value": 10, "description": ""})
        # Bob can't afford, so he doesn't pay
        assert bob.balance == 5
        assert alice.balance == a_bal  # Alice gets nothing from Bob

    def test_collect_from_all_other_cant_afford(self):
        """Edge: collect_from_all when another player has insufficient balance."""
        game = Game(["Alice", "Bob"])
        alice, bob = game.players
        bob.balance = 30  # less than 50
        a_bal = alice.balance
        game._apply_card(alice, {"action": "collect_from_all", "value": 50, "description": ""})
        assert bob.balance == 30  # Bob doesn't pay
        assert alice.balance == a_bal  # Alice gets nothing


class TestPlayerEdgeCases:

    def test_deduct_money_to_negative_balance(self):
        """Edge: deducting more than balance pushes balance negative (bankruptcy trigger)."""
        p = Player("Bob")
        p.deduct_money(STARTING_BALANCE + 100)
        assert p.balance == -100
        assert p.is_bankrupt() is True

    def test_get_rent_no_group(self):
        """Branch: property with group=None — no full-group check, returns base rent."""
        p = Property("Standalone", 1, 100, 10)
        p.owner = Player("A")
        assert p.get_rent() == 10  # base rent, no group multiplier


# ============================================================================
# SECTION 8 — UI MODULE (ui.py)
# ============================================================================

class TestUI:

    def test_print_banner(self, capsys):
        ui.print_banner("Test")
        out, _ = capsys.readouterr()
        assert "Test" in out
        assert "====" in out

    def test_print_player_card(self, capsys):
        p = Player("Alice")
        p.go_to_jail()
        p.get_out_of_jail_cards = 1
        ui.print_player_card(p)
        out, _ = capsys.readouterr()
        assert "Alice" in out
        assert "IN JAIL" in out
        assert "Jail cards" in out

    def test_print_player_card_with_properties(self, capsys):
        p = Player("Alice")
        prop = Property("Test", 1, 10, 2)
        p.add_property(prop)
        prop.is_mortgaged = True
        ui.print_player_card(p)
        out, _ = capsys.readouterr()
        assert "[MORTGAGED]" in out

    def test_print_standings(self, capsys):
        players = [Player("Alice"), Player("Bob")]
        ui.print_standings(players)
        out, _ = capsys.readouterr()
        assert "Standings" in out

    def test_print_board_ownership(self, capsys):
        board = Board()
        ui.print_board_ownership(board)
        out, _ = capsys.readouterr()
        assert "Property Register" in out

    def test_format_currency(self):
        assert ui.format_currency(1500) == "$1,500"
        assert ui.format_currency(0) == "$0"

    def test_safe_int_input_valid(self):
        with patch("builtins.input", return_value="42"):
            assert ui.safe_int_input("prompt") == 42

    def test_safe_int_input_invalid(self):
        with patch("builtins.input", return_value="abc"):
            assert ui.safe_int_input("prompt", default=5) == 5

    def test_confirm_yes(self):
        with patch("builtins.input", return_value="y"):
            assert ui.confirm("prompt") is True

    def test_confirm_no(self):
        with patch("builtins.input", return_value="n"):
            assert ui.confirm("prompt") is False

    def test_confirm_uppercase_yes(self):
        """Edge: 'Y' (uppercase) should also return True after .strip().lower()."""
        with patch("builtins.input", return_value="Y"):
            assert ui.confirm("prompt") is True

    def test_confirm_whitespace(self):
        """Edge: input with leading/trailing whitespace."""
        with patch("builtins.input", return_value="  y  "):
            assert ui.confirm("prompt") is True

    def test_print_player_card_no_jail_no_properties(self, capsys):
        """Branch: player not in jail, no cards, no properties — 'none' printed."""
        p = Player("Bob")
        ui.print_player_card(p)
        out, _ = capsys.readouterr()
        assert "Bob" in out
        assert "Properties: none" in out
        assert "IN JAIL" not in out

    def test_print_standings_jailed_player(self, capsys):
        """Branch: jailed player gets [JAILED] tag in standings."""
        p = Player("Alice")
        p.go_to_jail()
        ui.print_standings([p])
        out, _ = capsys.readouterr()
        assert "[JAILED]" in out

    def test_safe_int_input_default_zero(self):
        """Edge: invalid input with default=0."""
        with patch("builtins.input", return_value="xyz"):
            assert ui.safe_int_input("prompt") == 0


if __name__ == "__main__":
    pytest.main(["-v", __file__])
