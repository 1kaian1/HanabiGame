import random
import time


class Game:

    def __init__(self, id, password, nickname):

        self.bonuses = ["+1 hint", "+1 hint", "recycling", "recycling", "superhint", "adrenalin"]
        self.fireworks = {"blue": 0, "green": 0, "purple": 0, "red": 0, "yellow": 0}
        self.player_status = {"player": None, "status": None}
        self.on_turn = {"player": -1, "action": False}
        self.bonus = {"bonus": None, "player": None}
        self.hint = {"player": None, "hint": None}
        self.players = {0: nickname}
        self.general_message = None
        self.discard_package = []
        self.available_hints = 8
        self.password = password
        self.players_cards = {}
        self.all_cards = ["blue1", "blue1", "blue1", "blue2", "blue2", "blue3", "blue3", "blue4", "blue4", "blue5",
                          "green1", "green1", "green1", "green2", "green2", "green3", "green3", "green4", "green4",
                          "green5",
                          "purple1", "purple1", "purple1", "purple2", "purple2", "purple3", "purple3", "purple4",
                          "purple4", "purple5",
                          "red1", "red1", "red1", "red2", "red2", "red3", "red3", "red4", "red4", "red5",
                          "yellow1", "yellow1", "yellow1", "yellow2", "yellow2", "yellow3", "yellow3", "yellow4",
                          "yellow4", "yellow5"]
        self.finished = False
        self.break_ = False
        self.ready = False
        self.strikes = 0
        self.id = id

    def start_game(self):

        self.ready = True

        if len(self.players) <= 3:
            k = 5
        else:
            k = 4

        player_cards = []

        for player in self.players:

            for _ in range(k):

                card = random.choice(self.all_cards)
                player_cards.append(card)

                index = self.all_cards.index(card)
                del self.all_cards[index]

            self.players_cards[player] = player_cards
            player_cards = []

        self.next_turn()

    def event_hint(self, player_number, card_id, who):

        self.break_ = True
        self.on_turn["action"] = False

        if self.available_hints != 0:
            self.available_hints -= 1

        self.hint = {"player": who, "hint": card_id}
        self.player_status = {"player": player_number,
                              "status": f"Hint \"{card_id}\" to \"{self.players[who]}\""}

        time.sleep(3)
        self.next_turn()

    def event_discard(self, player_number, card_id, card_index):

        self.break_ = True
        self.on_turn["action"] = False

        if self.available_hints != 8:
            self.available_hints += 1

        self.discard_package.append(card_id)
        self.player_status = {"player": player_number,
                              "status": f"Discard \"{card_id}\""}

        self.get_new_card(player_number, card_index)
        time.sleep(3)
        self.next_turn()

    def event_play(self, player_number, card_id, card_index):

        self.break_ = True
        self.on_turn["action"] = False

        self.player_status = {"player": player_number,
                              "status": f"Play \"{card_id}\""}

        self.get_new_card(player_number, card_index)

        if self.fireworks[card_id[:-1]] + 1 == int(card_id[-1]):

            self.fireworks[card_id[:-1]] += 1

            for firework in self.fireworks:
                if self.fireworks[firework] != 5:
                    break
            else:
                self.general_message = "All fireworks completed!"
                time.sleep(10)
                self.finished = True

            if int(card_id[-1]) == 5:

                self.general_message = "Firework completed!"
                time.sleep(2)

                bonus = random.choice(self.bonuses)
                index = self.bonuses.index(bonus)
                del self.bonuses[index]

                self.general_message = f"Bonus: {bonus}!"
                time.sleep(3)
                self.general_message = None

                if bonus == "+1 hint":

                    if self.available_hints != 8:
                        self.available_hints += 1

                    time.sleep(3)
                    self.next_turn()

                elif bonus == "recycling" and len(self.discard_package) == 0:

                    time.sleep(3)
                    self.next_turn()

                else:
                    self.bonus = {"bonus": bonus, "player": player_number}

            else:

                time.sleep(3)
                self.next_turn()

        else:

            self.discard_package.append(card_id)
            self.strikes += 1

            if self.strikes < 3:
                self.general_message = f"{self.strikes}. strike"

                time.sleep(3)

                self.general_message = None
                self.next_turn()

            else:
                self.general_message = "Game over!"
                time.sleep(10)
                self.finished = True

    def event_superhint(self, player_number, card_id, who):

        self.bonus = {"bonus": None, "player": None}

        self.hint = {"player": who, "hint": card_id}
        self.player_status = {"player": player_number,
                              "status": f"Superhint \"{card_id}\" to \"{self.players[who]}\""}

        time.sleep(3)
        self.next_turn()

    def event_recycling(self, player_number, card_id):

        self.bonus = {"bonus": None, "player": None}

        self.player_status = {"player": player_number,
                              "status": f"Recycling \"{card_id}\""}

        index = self.discard_package.index(card_id)
        del self.discard_package[index]
        self.all_cards.append(card_id)

        time.sleep(3)
        self.next_turn()

    def event_adrenalin(self, player_number, card_id):

        self.bonus = {"bonus": None, "player": None}

        self.player_status = {"player": player_number,
                              "status": f"Added \"{card_id}\" tokens"}

        self.strikes += int(card_id)

        if self.available_hints + int(card_id) > 8:
            self.available_hints = 8
        else:
            self.available_hints += int(card_id)

        time.sleep(3)
        self.next_turn()

    def next_turn(self):

        if self.on_turn["player"] == -1:
            self.on_turn["player"] = random.randrange(0, len(self.players))
        elif self.on_turn["player"] == len(self.players) - 1:
            self.on_turn["player"] = 0
        else:
            self.on_turn["player"] = self.on_turn["player"] + 1

        self.hint = {"player": None, "hint": None}
        self.player_status = {"player": None, "status": None}
        self.general_message = ""

        self.break_ = False

        time.sleep(3)

        self.on_turn["action"] = True

    def get_new_card(self, player_number, card_index):

        if len(self.all_cards) != 0:
            new_card = random.choice(self.all_cards)
            index = self.all_cards.index(new_card)
            del self.all_cards[index]
        else:
            new_card = None

        self.players_cards[player_number][card_index] = new_card

    def join(self, nickname, password):

        if self.ready is True:
            return "The game is already running."

        elif password == self.password:
            if len(self.players) != 5:
                self.players[len(self.players)] = nickname
                return len(self.players)-1
            else:
                return "Room is full."

        else:
            return "Incorrect password."
