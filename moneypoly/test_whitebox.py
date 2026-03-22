import pytest
import io
import sys
from unittest.mock import patch, MagicMock

from moneypoly.bank import Bank
from moneypoly.player import Player
from moneypoly.property import Property, PropertyGroup
from moneypoly.dice import Dice
from moneypoly.cards import CardDeck, CHANCE_CARDS
from moneypoly.board import Board
from moneypoly.game import Game
from moneypoly.config import (
    BANK_STARTING_FUNDS, STARTING_BALANCE, GO_SALARY, JAIL_FINE,
    AUCTION_MIN_INCREMENT, BOARD_SIZE
)
from moneypoly import ui

# --- BANK TESTS ---
def test_bank_initialization():
    bank = Bank()
    assert bank.get_balance() == BANK_STARTING_FUNDS
    assert bank.total_loans_issued() == 0

def test_bank_collect():
    bank = Bank()
    bank.collect(500)
    assert bank.get_balance() == BANK_STARTING_FUNDS + 500

def test_bank_collect_negative():
    bank = Bank()
    # Code says negative amounts are silently ignored
    bank.collect(-100)
    # The bank balance should NOT decrease! If it does, our test FAILS to reveal the bug.
    assert bank.get_balance() == BANK_STARTING_FUNDS, "Bank collect() with negative amount reduced funds!"

def test_bank_pay_out():
    bank = Bank()
    bank.pay_out(100)
    assert bank.get_balance() == BANK_STARTING_FUNDS - 100
    
    assert bank.pay_out(-50) == 0  # Should return 0 for non-positive amounts
    
    with pytest.raises(ValueError):
        bank.pay_out(BANK_STARTING_FUNDS + 1000)

def test_bank_give_loan():
    bank = Bank()
    player = Player("Alice")
    bank.give_loan(player, 500)
    assert player.balance == STARTING_BALANCE + 500
    # Bank funds should be reduced accordingly
    assert bank.get_balance() == BANK_STARTING_FUNDS - 500, "Bank funds were not reduced after giving a loan!"
    assert bank.loan_count() == 1
    assert bank.total_loans_issued() == 500
    
    bank.give_loan(player, -20)  # Should return immediately

def test_bank_summary(capsys):
    bank = Bank()
    bank.summary()
    out, _ = capsys.readouterr()
    assert "Bank reserves" in out

def test_bank_repr():
    bank = Bank()
    assert "Bank(funds=" in repr(bank)


# --- PLAYER TESTS ---
def test_player_initialization():
    player = Player("Bob")
    assert player.name == "Bob"
    assert player.balance == STARTING_BALANCE

def test_player_add_deduct_money():
    player = Player("Bob")
    player.add_money(100)
    assert player.balance == STARTING_BALANCE + 100
    
    with pytest.raises(ValueError):
        player.add_money(-10)
        
    player.deduct_money(50)
    assert player.balance == STARTING_BALANCE + 50
    
    with pytest.raises(ValueError):
        player.deduct_money(-10)

def test_player_net_worth():
    player = Player("Bob")
    assert player.net_worth() == STARTING_BALANCE

def test_player_move_land_on_go():
    player = Player("Bob")
    player.move(BOARD_SIZE)  # Move exactly around the board to 0
    assert player.position == 0
    assert player.balance == STARTING_BALANCE + GO_SALARY

def test_player_move_pass_go():
    player = Player("Bob")
    # Position player at 38
    player.position = 38
    # Move forward 4 steps, passing Go (0), ending up at 2.
    player.move(4)
    assert player.position == 2
    # Should be awarded Go salary because they passed Go
    assert player.balance == STARTING_BALANCE + GO_SALARY, "Passing go did not award Salary!"

def test_player_go_to_jail():
    player = Player("Bob")
    player.go_to_jail()
    assert player.in_jail is True
    assert player.position == 10

def test_player_property_management():
    player = Player("Bob")
    prop = Property("Test Prop", 1, 100, 10)
    player.add_property(prop)
    assert prop in player.properties
    assert player.count_properties() == 1
    
    # Adding twice should not duplicate
    player.add_property(prop)
    assert player.count_properties() == 1
    
    player.remove_property(prop)
    assert player.count_properties() == 0

def test_player_status():
    player = Player("Bob")
    status = player.status_line()
    assert "Bob" in status
    assert repr(player).startswith("Player('Bob'")


# --- PROPERTY TESTS ---
def test_property_initialization():
    g = PropertyGroup("Green", "green")
    p = Property("Test Prop", 2, 200, 20, group=g)
    assert p.group == g
    assert p in g.properties

def test_property_get_rent():
    g = PropertyGroup("Green", "green")
    p1 = Property("P1", 1, 100, 10, group=g)
    p2 = Property("P2", 2, 100, 10, group=g)
    
    player = Player("Owner")
    p1.owner = player
    # Not all owned
    assert p1.get_rent() == 10
    
    p2.owner = player
    # All owned by 'Owner' -> double rent
    assert p1.get_rent() == 20
    
    # Mortgaged
    p1.is_mortgaged = True
    assert p1.get_rent() == 0

def test_property_mortgage():
    p = Property("P1", 1, 100, 10)
    # mortgage() returns mortgage_value which is 50
    assert p.mortgage() == 50
    assert p.is_mortgaged is True
    assert p.mortgage() == 0  # Already mortgaged
    assert not p.is_available()

def test_property_unmortgage():
    p = Property("P1", 1, 100, 10)
    p.mortgage()
    assert p.unmortgage() == int(50 * 1.1)
    assert p.is_mortgaged is False
    assert p.unmortgage() == 0

def test_property_group_methods():
    g = PropertyGroup("Test", "blue")
    p = Property("P1", 1, 100, 10)
    g.add_property(p)
    assert p.group == g
    assert g.size() == 1
    
    p.owner = Player("P1")
    assert g.get_owner_counts()[p.owner] == 1
    assert repr(g).startswith("PropertyGroup")


# --- DICE TESTS ---
def test_dice_roll():
    dice = Dice()
    totals = set()
    six_rolled = False
    
    for _ in range(100):
        val = dice.roll()
        totals.add(val)
        if dice.die1 == 6 or dice.die2 == 6:
            six_rolled = True
            
    # A standard die should be able to roll a 6
    assert six_rolled, "Dice never rolled a 6 in 100 tries! Looks like it's capped at 5."
    
def test_dice_doubles():
    with patch("random.randint", return_value=3):
        dice = Dice()
        dice.roll()
        assert dice.is_doubles() is True
        assert dice.doubles_streak == 1
        
        dice.roll()
        assert dice.doubles_streak == 2
        
    with patch("random.randint", side_effect=[3, 4]):
        dice.roll()
        assert dice.is_doubles() is False
        assert dice.doubles_streak == 0
        assert "3 + 4 = 7" in dice.describe()


# --- CARDS TESTS ---
def test_card_deck_operations():
    deck = CardDeck([{"action": "test1"}, {"action": "test2"}])
    assert len(deck) == 2
    assert deck.peek()["action"] == "test1"
    
    c1 = deck.draw()
    assert c1["action"] == "test1"
    
    c2 = deck.draw()
    assert c2["action"] == "test2"
    
    # Cycles back
    c3 = deck.draw()
    assert c3["action"] == "test1"
    
    assert deck.cards_remaining() == 1
    deck.reshuffle()
    assert deck.index == 0
    
    empty_deck = CardDeck([])
    assert empty_deck.draw() is None
    assert empty_deck.peek() is None


# --- BOARD TESTS ---
def test_board_properties():
    board = Board()
    assert len(board.properties) == 22
    assert board.get_property_at(1).name == "Mediterranean Avenue"
    assert board.get_property_at(99) is None
    
def test_board_tile_types():
    board = Board()
    assert board.get_tile_type(0) == "go"
    assert board.get_tile_type(1) == "property"
    assert board.get_tile_type(2) == "community_chest"
    assert board.get_tile_type(99) == "blank"
    
    assert board.is_purchasable(1) is True
    assert board.is_purchasable(0) is False
    assert board.is_special_tile(0) is True
    
    player = Player("A")
    prop = board.get_property_at(1)
    prop.owner = player
    assert board.properties_owned_by(player) == [prop]
    
    # One property is owned, unowned should be 21
    assert len(board.unowned_properties()) == 21
    
    prop.is_mortgaged = True
    assert board.is_purchasable(1) is False


# --- GAME TESTS ---
def test_game_initialization():
    game = Game(["Alice", "Bob"])
    assert len(game.players) == 2
    assert game.current_player().name == "Alice"

def test_trade_logic():
    game = Game(["Alice", "Bob"])
    alice = game.players[0]
    bob = game.players[1]
    
    prop = game.board.get_property_at(1)
    prop.owner = alice
    alice.add_property(prop)
    
    alice_initial_balance = alice.balance
    bob_initial_balance = bob.balance
    
    # Trade: Alice sells prop to Bob for 100
    success = game.trade(seller=alice, buyer=bob, prop=prop, cash_amount=100)
    assert success is True
    assert prop.owner == bob
    assert bob.balance == bob_initial_balance - 100
    
    # The bug: Seller never receives the money!
    assert alice.balance == alice_initial_balance + 100, "Trade bug: Seller did not receive the money!"
    
def test_trade_edge_cases():
    game = Game(["Alice", "Bob"])
    alice = game.players[0]
    bob = game.players[1]
    
    prop = game.board.get_property_at(1)
    prop.owner = alice
    alice.add_property(prop)
    
    # Buyer cannot afford
    assert game.trade(alice, bob, prop, bob.balance + 100) is False
    
    # Seller doesn't own
    prop.owner = bob
    assert game.trade(alice, bob, prop, 100) is False

def test_bankruptcy_logic():
    game = Game(["Alice", "Bob", "Charlie"])
    alice = game.players[0]
    
    # Assign property
    prop = game.board.get_property_at(1)
    prop.owner = alice
    alice.add_property(prop)
    
    # Make bankrupt
    alice.balance = -10
    game._check_bankruptcy(alice)
    
    assert alice.is_eliminated is True
    assert prop.owner is None
    assert prop.is_mortgaged is False
    assert "Alice" not in [p.name for p in game.players]

def test_jail_turn_no_card_no_pay():
    game = Game(["Alice"])
    alice = game.players[0]
    alice.go_to_jail()
    
    with patch("moneypoly.ui.confirm", return_value=False):
        # Turn 1
        game._handle_jail_turn(alice)
        assert alice.jail_turns == 1
        assert alice.in_jail is True
        
        # Turn 2
        game._handle_jail_turn(alice)
        assert alice.jail_turns == 2
        
        with patch.object(game.dice, 'roll', return_value=4), patch('builtins.input', return_value='s'):
            game._handle_jail_turn(alice)
            assert alice.in_jail is False
            assert alice.jail_turns == 0
            assert alice.balance == STARTING_BALANCE - JAIL_FINE

def test_jail_card_usage():
    game = Game(["Alice"])
    alice = game.players[0]
    alice.go_to_jail()
    alice.get_out_of_jail_cards = 1
    
    with patch("moneypoly.ui.confirm", return_value=True), patch('builtins.input', return_value='s'):
        game._handle_jail_turn(alice)
        assert alice.in_jail is False
        assert alice.get_out_of_jail_cards == 0

def test_jail_pay_fine():
    game = Game(["Alice"])
    alice = game.players[0]
    alice.go_to_jail()
    
    with patch("moneypoly.ui.confirm", return_value=True), patch.object(game.dice, 'roll', return_value=4), patch('builtins.input', return_value='s'): # True for pay
        game._handle_jail_turn(alice)
        assert alice.in_jail is False
        assert alice.balance == STARTING_BALANCE - JAIL_FINE
        
def test_buy_property():
    game = Game(["Alice"])
    alice = game.players[0]
    prop = game.board.get_property_at(1)
    
    success = game.buy_property(alice, prop)
    assert success is True
    assert prop.owner == alice
    assert alice.balance == STARTING_BALANCE - prop.price
    assert prop in alice.properties
    
    # Can't afford
    alice.balance = 0
    prop2 = game.board.get_property_at(3)
    assert game.buy_property(alice, prop2) is False

def test_pay_rent():
    game = Game(["Alice", "Bob"])
    alice = game.players[0]
    bob = game.players[1]
    
    prop = game.board.get_property_at(1)
    prop.owner = bob
    
    game.pay_rent(alice, prop)
    assert alice.balance == STARTING_BALANCE - prop.get_rent()

def test_mortgage_actions():
    game = Game(["Alice"])
    alice = game.players[0]
    prop = game.board.get_property_at(1)
    
    prop.owner = alice
    alice.add_property(prop)
    
    # Mortgage
    assert game.mortgage_property(alice, prop) is True
    assert alice.balance == STARTING_BALANCE + prop.mortgage_value
    
    assert game.mortgage_property(alice, prop) is False # Already mortgaged
    
    # Unmortgage
    cost = int(prop.mortgage_value * 1.1)
    assert game.unmortgage_property(alice, prop) is True
    assert alice.balance == STARTING_BALANCE + prop.mortgage_value - cost
    
    assert game.unmortgage_property(alice, prop) is False # Already unmortgaged

def test_apply_card_actions():
    game = Game(["Alice", "Bob"])
    alice = game.players[0]
    bob = game.players[1]
    
    # Collect
    game._apply_card(alice, {"action": "collect", "value": 50, "description": ""})
    assert alice.balance == STARTING_BALANCE + 50
    
    # Pay
    game._apply_card(alice, {"action": "pay", "value": 20, "description": ""})
    assert alice.balance == STARTING_BALANCE + 30
    
    # Jail
    game._apply_card(alice, {"action": "jail", "value": 0, "description": ""})
    assert alice.in_jail is True
    
    # Move to Go
    game._apply_card(alice, {"action": "move_to", "value": 0, "description": ""})
    assert alice.position == 0
    # Should get Go salary because move_to Go with old pos 10 is value < old_pos
    
    # Birthday
    bob_bal = bob.balance
    ali_bal = alice.balance
    game._apply_card(alice, {"action": "birthday", "value": 10, "description": ""})
    assert bob.balance == bob_bal - 10
    assert alice.balance == ali_bal + 10

def test_play_turn_doubles_streak():
    game = Game(["Alice", "Bob"])
    alice = game.players[0]
    
    with patch.object(game.dice, 'roll', return_value=4), patch.object(game.dice, 'is_doubles', return_value=True):
        game.dice.doubles_streak = 3
        game.play_turn()
        assert alice.in_jail is True
        assert game.current_index == 1 # Advanced turn

def test_auction():
    game = Game(["Alice", "Bob"])
    prop = game.board.get_property_at(1)
    
    # Bob bids 50, Alice passes
    with patch("moneypoly.ui.safe_int_input", side_effect=[0, 50]):
        game.auction_property(prop)
        assert prop.owner == game.players[1]
        assert game.players[1].balance == STARTING_BALANCE - 50

# --- UI TESTS ---
def test_ui_components(capsys):
    player = Player("Alice")
    player.go_to_jail()
    player.get_out_of_jail_cards = 1
    player.add_property(Property("Test", 1, 10, 2))
    player.properties[0].is_mortgaged = True
    
    ui.print_player_card(player)
    out, _ = capsys.readouterr()
    assert "Alice" in out
    assert "IN JAIL" in out
    
    board = Board()
    ui.print_board_ownership(board)
    out, _ = capsys.readouterr()
    assert "[ Property Register ]" in out
    
    assert ui.format_currency(1500) == "$1,500"
    
    with patch("builtins.input", return_value="y"):
        assert ui.confirm("prompt") is True

if __name__ == "__main__":
    pytest.main(["-v", "test_whitebox.py"])
