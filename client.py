import sys
import pygame
import time
from network import Network

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
#screen_width, screen_height = pygame.display.list_modes(0, pygame.FULLSCREEN, 0)[0]
#screen = pygame.display.set_mode((screen_width, screen_height))
info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h

if (screen_width, screen_height) < (1024, 768):
    raise Exception("Invalid screen scale.")

clock = pygame.time.Clock()

# colors
black_col = (0, 0, 0)
grey_col = (127, 127, 127)
purple_col = (140, 0, 255)

# fonts
base_font_25 = pygame.font.Font(None, 25)
base_font_50 = pygame.font.Font(None, 50)
base_font_100 = pygame.font.Font(None, 100)

# variables
card_scale = (115, 180)

# loading images
menu_bg_img = pygame.image.load("materials/bg1.png")
table_img = pygame.image.load("materials/bg2.png")
separator_bg_img = pygame.image.load("materials/bg3.png")

join_room_img = pygame.image.load("materials/join_room.png")
create_room_img = pygame.image.load("materials/create_room.png")

confirm_img = pygame.image.load("materials/confirm.png")
back_img = pygame.image.load("materials/back.png")

start_img = pygame.image.load("materials/start.png")
cancel_img = pygame.image.load("materials/cancel.png")

color_img = pygame.image.load("materials/color.png")
number_img = pygame.image.load("materials/number.png")

quit_menu_img = pygame.image.load("materials/quit.png")
quit_game_img = pygame.image.load("materials/quit2.png")

play_default_img = pygame.image.load("materials/play.png")
play_green_img = pygame.image.load("materials/play_green.png")
play_red_img = pygame.image.load("materials/play_red.png")

discard_default_img = pygame.image.load("materials/discard.png")
discard_green_img = pygame.image.load("materials/discard_green.png")
discard_red_img = pygame.image.load("materials/discard_red.png")

hint_default_img = pygame.image.load("materials/hint.png")
hint_green_img = pygame.image.load("materials/hint_green.png")
hint_red_img = pygame.image.load("materials/hint_red.png")

zero_green_img = pygame.image.load("materials/0_green.png")
zero_red_img = pygame.image.load("materials/0_red.png")

one_green_img = pygame.image.load("materials/1_green.png")
one_red_img = pygame.image.load("materials/1_red.png")

two_green_img = pygame.image.load("materials/2_green.png")
two_red_img = pygame.image.load("materials/2_red.png")

rules_default_img = pygame.image.load("materials/rules.png")
rules_green_img = pygame.image.load("materials/rules_green.png")

game_rules_img = pygame.image.load("materials/game_rules.png")


cards_imgs = [pygame.image.load("materials/shadow_card.png")]

cards_colors = ["blue", "green", "purple", "red", "yellow"]

for x in cards_colors:

    for y in range(1, 6):

        img = pygame.image.load(f"materials/{x}{y}.png")
        cards_imgs.append(img)

cards = ["grey0",
         "blue1", "blue2", "blue3", "blue4", "blue5",
         "green1", "green2", "green3", "green4", "green5",
         "purple1", "purple2", "purple3", "purple4", "purple5",
         "red1", "red2", "red3", "red4", "red5",
         "yellow1", "yellow2", "yellow3", "yellow4", "yellow5"]

bases = {"down": (screen_width/2, screen_height*0.9),
         "middle": (screen_width/2, screen_height/7),
         "middle left": (screen_width/3.25, screen_height/7),
         "middle right": (screen_width*0.695, screen_height/7),
         "left": (screen_width/11, screen_height/2),
         "right": (screen_width*0.91, screen_height/2),
         "fireworks": (screen_width/2, screen_height/2),
         "discard_pack": (screen_width/2, screen_height/4.5)}

print("Process started")


class ObjectsDrawManager:

    @staticmethod
    def image(related_data):

        x, y = related_data["coordinates"]
        img = related_data["img"]

        if related_data.get("transform"):
            a, b = related_data["transform"]
            img = pygame.transform.scale(img, (int(a), int(b)))

        if related_data.get("rotate"):
            img = pygame.transform.rotate(img, related_data["rotate"])

        rect = img.get_rect()
        rect.center = (x, y)
        screen.blit(img, (rect.x, rect.y))

        return rect

    @staticmethod
    def text(related_data):

        text = related_data["text"]
        color = related_data["color"]
        font = related_data["font"]

        if related_data.get("line"):
            font.set_underline(True)
        else:
            font.set_underline(False)

        text_surface = font.render(text, True, color)

        related_data["img"] = text_surface

        return ObjectsDrawManager.image(related_data)


class Game:

    def __init__(self, my_player_number, network):

        self.cards_buttons = {"names": [], "rects": [], "players": []}
        self.local_data = {"event": "", "card_id": "", "whose": ""}
        self.server_data_dispatch = {"event": ""}
        self.my_player_number = my_player_number
        self.rules_y = screen_height / 2
        self.discard_buttons = {}
        self.network = network
        self.actual_bases = []
        self.rules_scroll = 0
        self.buttons = {}
        self.game = None

    def main(self):

        while True:

            clock.tick(60)

            try:
                self.game = self.network.send(self.server_data_dispatch)
            except:
                return "An [clienterror0] occured."

            if self.server_data_dispatch["event"] == "quit":
                return "You left the game."

            elif not self.game:
                return "An [clienterror1] occured."

            elif 0 not in self.game.players:
                return "Host left the game."

            elif len(self.game.players) == 1 and self.game.ready:
                return "Other players left the game."

            elif self.game.finished:
                return "Game finished!"

            else:
                self.server_data_dispatch = {"event": ""}

                self.reset_players_bases()

            self.buttons = {}
            self.discard_buttons = {}
            self.cards_buttons = {"ids": [], "rects": [], "players": []}

            ObjectsDrawManager.image({"img": table_img,
                                      "coordinates": (screen_width / 2, screen_height / 2),
                                      "transform": (screen_width, screen_height)})

            if self.game.ready:

                ObjectsDrawManager.text({"coordinates": (screen_width * 0.9, screen_height / 9),
                                         "font": base_font_50,
                                         "text": f"hints: {self.game.available_hints}",
                                         "color": black_col})
                ObjectsDrawManager.text({"coordinates": (screen_width * 0.907, screen_height / 13),
                                         "font": base_font_50,
                                         "text": f"strikes: {self.game.strikes}",
                                         "color": black_col})

                self.players_cards_printout()
                self.players_names_and_statuses_printout()
                self.fireworks_printout()

                self.action_buttons()

                if self.local_data["event"] == "rules":
                    self.discard_pack_printout()
                    self.rules_printout()
                else:
                    self.rules_printout()
                    self.discard_pack_printout()

                self.general_message_printout()

                if self.game.bonus["bonus"] == "adrenalin" and self.game.bonus["player"] == self.my_player_number:
                    self.event_adrenalin()

            else:

                ObjectsDrawManager.text({"coordinates": (screen_width / 2, screen_height / 1.8),
                                         "font": base_font_50,
                                         "text": "Waiting for players...",
                                         "color": black_col})
                ObjectsDrawManager.text({"coordinates": (screen_width / 2, screen_height / 1.6),
                                         "font": base_font_50,
                                         "text": f"{len(self.game.players)}/5   room {self.game.id}",
                                         "color": black_col})

                self.buttons["cancel"] = ObjectsDrawManager.image({"coordinates": (screen_width / 2, screen_height / 1.2),
                                                                   "img": cancel_img,
                                                                   "transform": (screen_width / 4, screen_height / 8)})

                if self.my_player_number == 0 and len(self.game.players) >= 2:
                    self.buttons["start"] = ObjectsDrawManager.image({"coordinates": (screen_width / 2, screen_height / 1.4),
                                                                      "img": start_img,
                                                                      "transform": (screen_width / 5, screen_height / 8)})

            for event in pygame.event.get():

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    none = False

                    for button in self.buttons:
                        if self.buttons[button].collidepoint(event.pos):
                            self.button_collide(button)
                            break
                    else:
                        none = True

                    for rect in self.cards_buttons["rects"]:
                        if rect.collidepoint(event.pos):
                            self.card_collide(rect)
                            break
                    else:
                        if none:
                            self.button_collide("")

                    for card_id in self.discard_buttons:
                        if self.discard_buttons[card_id].collidepoint(event.pos):
                            self.discard_collide(card_id)
                            break

                elif event.type == pygame.KEYDOWN:
                    pass

                elif event.type == pygame.MOUSEWHEEL:
                    if self.local_data["event"] == "rules":
                        self.rules_scroll = event.y

            pygame.display.update()

    def button_collide(self, button):

        if self.game.bonus["bonus"] is None or self.game.bonus["player"] != self.my_player_number:

            if button == "start":
                self.server_data_dispatch["event"] = "start"

            elif button == "cancel" or button == "quit":
                self.server_data_dispatch["event"] = "quit"

            elif button == "rules":
                if self.local_data["event"] != "rules":
                    self.local_data["event"] = "rules"

            elif button == "discard_pack":
                if self.local_data["event"] != "discard_pack":
                    self.local_data["event"] = "discard_pack"

            elif button == "number":
                self.server_data_dispatch["event"] = "hint"
                self.server_data_dispatch["card_id"] = self.local_data["card_id"][-1]
                self.server_data_dispatch["whose"] = self.local_data["whose"]
                self.server_data_dispatch["card_index"] = None
                self.local_data = {"event": "", "card_id": "", "whose": "", "rect": ""}

            elif button == "color":
                self.server_data_dispatch["event"] = "hint"
                self.server_data_dispatch["card_id"] = self.local_data["card_id"][:-1]
                self.server_data_dispatch["whose"] = self.local_data["whose"]
                self.server_data_dispatch["card_index"] = None
                self.local_data = {"event": "", "card_id": "", "whose": "", "rect": ""}

            elif button == "play" or button == "discard" or button == "hint":
                if self.game.on_turn["player"] == self.my_player_number and self.game.on_turn["action"]:
                    self.local_data["event"] = button
                    self.local_data["card_id"] = ""

            else:
                self.local_data = {"event": "", "card_id": "", "whose": "", "rect": ""}

        elif self.game.bonus["bonus"] == "adrenalin" and self.game.bonus["player"] == self.my_player_number:

            if button == "0":
                self.server_data_dispatch["event"] = "adrenalin"
                self.server_data_dispatch["card_id"] = button
            elif button == "1" and self.game.strikes != 2:
                self.server_data_dispatch["event"] = "adrenalin"
                self.server_data_dispatch["card_id"] = button
            elif button == "2" and not self.game.strikes >= 1:
                self.server_data_dispatch["event"] = "adrenalin"
                self.server_data_dispatch["card_id"] = button

    def card_collide(self, rect):

        card_index = self.cards_buttons["rects"].index(rect)
        player = self.cards_buttons["players"][card_index]
        card_id = self.cards_buttons["ids"][card_index]

        event = self.local_data["event"]

        if event == "play" or event == "discard" and player == self.my_player_number:
            self.server_data_dispatch["event"] = self.local_data["event"]
            self.server_data_dispatch["card_id"] = card_id
            self.server_data_dispatch["whose"] = None

            if len(self.cards_buttons["players"]) <= 5:
                self.server_data_dispatch["card_index"] = card_index % 5
            else:
                self.server_data_dispatch["card_index"] = card_index % 4

            self.local_data = {"event": "", "card_id": "", "whose": "", "rect": ""}

        elif event == "hint" and player != self.my_player_number:
            self.local_data["card_id"] = card_id
            self.local_data["whose"] = player

        elif self.game.bonus["bonus"] == "superhint" and self.game.bonus["player"] == self.my_player_number:
            if player != self.my_player_number:
                self.server_data_dispatch["event"] = "superhint"
                self.server_data_dispatch["card_id"] = card_id
                self.server_data_dispatch["whose"] = player
                self.server_data_dispatch["card_index"] = None

        else:
            self.local_data = {"event": "", "card_id": "", "whose": "", "rect": ""}

    def discard_collide(self, card_id):

        self.server_data_dispatch["event"] = "recycling"
        self.server_data_dispatch["card_id"] = card_id
        self.server_data_dispatch["whose"] = None
        self.server_data_dispatch["card_index"] = None

    def event_adrenalin(self):

        ObjectsDrawManager.image({"img": separator_bg_img,
                                  "coordinates": (screen_width / 2, screen_height / 2),
                                  "transform": (screen_width / 2, screen_height / 2)})
        ObjectsDrawManager.text({"coordinates": (screen_width / 2, screen_height / 2.6),
                                 "font": base_font_100,
                                 "text": "Adrenalin!",
                                 "color": black_col})

        zero_img = zero_green_img
        one_img = one_green_img
        two_img = two_green_img

        if self.game.strikes == 1:
            two_img = two_red_img
        elif self.game.strikes == 2:
            one_img = one_red_img
            two_img = two_red_img

        self.buttons["0"] = ObjectsDrawManager.image({"coordinates": (screen_width / 2.4, screen_height / 1.8),
                                                      "img": zero_img})
        self.buttons["1"] = ObjectsDrawManager.image({"coordinates": (screen_width / 2, screen_height / 1.8),
                                                      "img": one_img})
        self.buttons["2"] = ObjectsDrawManager.image({"coordinates": (screen_width / 1.7, screen_height / 1.8),
                                                      "img": two_img})

    def reset_players_bases(self):

        number_of_players = len(self.game.players)

        self.actual_bases = []

        if number_of_players == 2:
            self.actual_bases = ["middle"]

        elif number_of_players == 3:

            if self.my_player_number == 1:
                self.actual_bases = ["middle right", "middle left"]
            else:
                self.actual_bases = ["middle left", "middle right"]

        elif number_of_players == 4:

            if self.my_player_number == 1:
                self.actual_bases = ["right", "left", "middle"]
            elif self.my_player_number == 2:
                self.actual_bases = ["middle", "right", "left"]
            else:
                self.actual_bases = ["left", "middle", "right"]

        elif number_of_players == 5:

            if self.my_player_number == 1:
                self.actual_bases = ["right", "left", "middle left", "middle right"]
            elif self.my_player_number == 2:
                self.actual_bases = ["middle right", "right", "left", "middle left"]
            elif self.my_player_number == 3:
                self.actual_bases = ["middle left", "middle right", "right", "left"]
            else:
                self.actual_bases = ["left", "middle left", "middle right", "right"]

        self.actual_bases.insert(self.my_player_number, "down")

    def action_buttons(self):

        play_img = play_default_img
        discard_img = discard_default_img
        hint_img = hint_default_img

        event = self.local_data["event"]
        card_id = self.local_data["card_id"]

        player_on_turn = self.game.on_turn["player"]
        on_turn_active = self.game.on_turn["action"]

        if not self.game.break_:

            if player_on_turn == self.my_player_number and on_turn_active:

                if event == "play":
                    play_img = play_red_img
                else:
                    play_img = play_green_img

                if event == "discard":
                    discard_img = discard_red_img
                else:
                    discard_img = discard_green_img

                if event == "hint" and self.game.available_hints != 0:
                    hint_img = hint_red_img

                    if card_id != "":
                        ObjectsDrawManager.image({"img": separator_bg_img,
                                                  "coordinates": (screen_width / 2, screen_height / 2),
                                                  "transform": (screen_width / 4, screen_height / 4)})

                        self.buttons["number"] = ObjectsDrawManager.image({"coordinates": (screen_width / 2, screen_height / 1.83),
                                                                           "img": number_img,
                                                                           "transform": (screen_width / 7.5, screen_height / 14)})
                        self.buttons["color"] = ObjectsDrawManager.image({"coordinates": (screen_width / 2, screen_height / 2.2),
                                                                          "img": color_img,
                                                                          "transform": (screen_width / 10, screen_height / 14)})

                elif self.game.available_hints == 0:
                    hint_img = hint_default_img
                else:
                    hint_img = hint_green_img

        else:

            if self.game.bonus["bonus"] == "superhint" and self.game.bonus["player"] == self.my_player_number:
                hint_img = hint_red_img

        self.buttons["play"] = ObjectsDrawManager.image({"coordinates": (screen_width / 20, screen_height / 11 * 10),
                                                         "img": play_img,
                                                         "transform": (screen_width / 12, screen_height / 14)})
        self.buttons["discard"] = ObjectsDrawManager.image({"coordinates": (screen_width / 5.9, screen_height / 11 * 10),
                                                            "img": discard_img,
                                                            "transform": (screen_width / 7, screen_height / 14)})
        self.buttons["hint"] = ObjectsDrawManager.image({"coordinates": (screen_width / 3.45, screen_height / 11 * 10),
                                                         "img": hint_img,
                                                         "transform": (screen_width / 12, screen_height / 14)})
        self.buttons["quit"] = ObjectsDrawManager.image({"coordinates": (screen_width * 0.945, screen_height * 0.91),
                                                         "img": quit_game_img,
                                                         "transform": (screen_width / 11, screen_height / 14)})

    def general_message_printout(self):

        player_on_turn = self.game.on_turn["player"]
        on_turn_active = self.game.on_turn["action"]

        if not self.game.break_:

            if player_on_turn == self.my_player_number and not on_turn_active:
                text = "Your turn!"
            elif player_on_turn != self.my_player_number and not on_turn_active:
                text = f"{self.game.players[player_on_turn]} on turn!"
            else:
                text = self.game.general_message

        else:
            text = self.game.general_message

        ObjectsDrawManager.text({"coordinates": (screen_width / 2, screen_height / 2),
                                 "font": base_font_100,
                                 "text": text,
                                 "color": black_col})

    def fireworks_printout(self):

        gap = 10
        shift = -((5 / 2 - 0.5) * card_scale[0] + (5 / 2 - 0.5) * gap)

        for firework in self.game.fireworks:

            base_x, base_y = bases["fireworks"]
            base_x += shift

            if self.game.fireworks[firework] == 0:
                ObjectsDrawManager.text({"coordinates": (base_x, base_y),
                                         "font": base_font_25,
                                         "text": firework,
                                         "color": black_col})
            else:
                full_firework = firework + str(self.game.fireworks[firework])
                index = cards.index(full_firework)

                img = cards_imgs[index]

                ObjectsDrawManager.image({"img": img,
                                          "coordinates": (base_x, base_y),
                                          "transform": card_scale})

            shift += card_scale[0] + 10

    def players_names_and_statuses_printout(self):

        for player in self.game.players:

            base_x, base_y = bases[self.actual_bases[player]]
            name_base_x, event_base_x = base_x, base_x
            name_base_y, event_base_y = base_y, base_y

            if player != self.my_player_number:

                if self.actual_bases[player] == "left":
                    rotate = 90
                    name_base_x -= 120
                    event_base_x += 120

                elif self.actual_bases[player] == "right":
                    rotate = -90
                    name_base_x += 120
                    event_base_x -= 120

                else:
                    rotate = None
                    name_base_y -= 120
                    event_base_y += 120

                ObjectsDrawManager.text({"coordinates": (name_base_x, name_base_y),
                                         "font": base_font_50,
                                         "text": self.game.players[player],
                                         "color": black_col,
                                         "rotate": rotate})

                if player == self.game.player_status["player"]:
                    text = self.game.player_status["status"]
                elif player == self.game.on_turn["player"]:
                    text = "On turn"
                else:
                    text = None

                ObjectsDrawManager.text({"coordinates": (event_base_x, event_base_y),
                                         "font": base_font_25,
                                         "text": text,
                                         "color": black_col,
                                         "rotate": rotate})

    def players_cards_printout(self):

        for player in self.game.players:

            gap = 10
            number_of_cards = len(self.game.players_cards[player])

            shift = -((number_of_cards / 2 - 0.5) * card_scale[0] + (number_of_cards / 2 - 0.5) * gap)

            for card in self.game.players_cards[player]:

                if card is not None:

                    base_x, base_y = bases[self.actual_bases[player]]

                    if player == self.my_player_number:
                        img = cards_imgs[0]
                    else:
                        img = cards_imgs[cards.index(card)]

                    if self.actual_bases[player] == "left":
                        rotate = 90
                        base_y += shift
                    elif self.actual_bases[player] == "right":
                        rotate = -90
                        base_y += -shift
                    elif self.actual_bases[player] == "down":
                        lift = 0

                        if self.game.hint["player"] == self.my_player_number:
                            hint = self.game.hint["hint"]

                            if self.game.hint["hint"] in card and self.game.break_:
                                lift = -40
                                ObjectsDrawManager.text({"coordinates": (base_x + shift, base_y + lift - 120),
                                                         "font": base_font_25,
                                                         "text": hint,
                                                         "color": black_col})

                        rotate = None
                        base_x += shift
                        base_y += lift

                    else:
                        rotate = None
                        base_x += shift

                    rect = ObjectsDrawManager.image({"img": img,
                                                     "coordinates": (base_x, base_y),
                                                     "transform": card_scale,
                                                     "rotate": rotate})

                    self.cards_buttons["ids"].append(card)
                    self.cards_buttons["rects"].append(rect)
                    self.cards_buttons["players"].append(player)

                shift += card_scale[0] + 10

    def discard_pack_printout(self):

        event = self.local_data["event"]
        bonus = self.game.bonus["bonus"]
        player = self.game.bonus["player"]

        if len(self.game.discard_package) == 0:

            ObjectsDrawManager.text({"coordinates": (screen_width / 4 * 3, screen_height / 2),
                                     "font": base_font_25,
                                     "text": "discard pack",
                                     "color": black_col})

        elif event == "discard_pack" or (bonus == "recycling" and player == self.my_player_number):

            self.buttons["discard_pack"] = ObjectsDrawManager.image({"img": separator_bg_img,
                                                                     "coordinates": (screen_width / 2, screen_height / 2),
                                                                     "transform": (screen_width * 0.68, screen_height * 0.8)})

            shift_y = 0
            range_x = 0
            range_y = 0
            gap = 10

            number_of_cards = len(self.game.discard_package)

            run = True
            while run:

                shift_x = -((10 / 2 - 0.5) * card_scale[0] + (10 / 2 - 0.5) * gap)

                if range_y > number_of_cards:
                    range_y = None
                    run = False
                else:
                    range_y += 10

                for card in self.game.discard_package[range_x:range_y]:
                    base_x, base_y = bases["discard_pack"]

                    base_x += shift_x
                    base_y += shift_y

                    index = cards.index(card)
                    img = cards_imgs[index]

                    rect = ObjectsDrawManager.image({"img": img,
                                                     "coordinates": (base_x, base_y),
                                                     "transform": card_scale})

                    if bonus == "recycling" and player == self.my_player_number:
                        self.discard_buttons[card] = rect

                    shift_x += card_scale[0] + 10

                range_x += 10
                shift_y += 200

        else:

            index = cards.index(self.game.discard_package[-1])
            img = cards_imgs[index]

            self.buttons["discard_pack"] = ObjectsDrawManager.image({"img": img,
                                                                     "coordinates": (screen_width / 4 * 3, screen_height / 2),
                                                                     "transform": card_scale})

    def rules_printout(self):

        event = self.local_data["event"]

        if event == "rules":

            if self.rules_scroll == -1:
                self.rules_y += 50
            elif self.rules_scroll == 1:
                self.rules_y -= 50

            self.rules_scroll = 0

            ObjectsDrawManager.image({"coordinates": (screen_width * 0.843, screen_height * 0.91),
                                      "img": rules_green_img,
                                      "transform": (screen_width / 10, screen_height / 14)})

            self.buttons["rules"] = ObjectsDrawManager.image({"coordinates": (screen_width / 2, self.rules_y),
                                                              "img": game_rules_img,
                                                              "transform": (screen_width / 2, screen_height * 1.2)})

        else:

            self.buttons["rules"] = ObjectsDrawManager.image({"coordinates": (screen_width * 0.843, screen_height * 0.91),
                                                              "img": rules_default_img,
                                                              "transform": (screen_width / 10, screen_height / 14)})


class Menu:

    def __init__(self, event):

        self.act_color = black_col
        self.default_event = None
        self.event = event

        self.room_number = None
        self.nickname = None
        self.password = None

        self.text = ""

    def main(self):

        while True:

            buttons = {}

            clock.tick(60)

            if self.event == "menu":
                default_text = "nickname"
                text_len = 18
            elif self.event == "join":
                default_text = "room number"
                text_len = 5
            elif self.event == "create":
                default_text = "password"
                text_len = 18
            else:
                raise Exception("Invalid event occured.")

            if self.text == "":
                final_text = default_text
            else:
                final_text = self.text

            ObjectsDrawManager.image({"img": menu_bg_img,
                                      "coordinates": (screen_width / 2, screen_height / 2),
                                      "transform": (screen_width, screen_height)})
            ObjectsDrawManager.text({"coordinates": (screen_width / 2, screen_height / 1.8),
                                     "font": base_font_50,
                                     "text": final_text,
                                     "color": self.act_color,
                                     "line": True})

            if self.event == "menu":

                buttons["join"] = ObjectsDrawManager.image({"coordinates": (screen_width / 2, screen_height / 1.5),
                                                            "img": join_room_img,
                                                            "transform": (screen_width / 3, screen_height / 8)})
                buttons["create"] = ObjectsDrawManager.image({"coordinates": (screen_width / 2, screen_height / 1.25),
                                                              "img": create_room_img,
                                                              "transform": (screen_width / 2.5, screen_height / 8)})
                buttons["quit"] = ObjectsDrawManager.image({"coordinates": (screen_width / 2, screen_height / 1.075),
                                                            "img": quit_menu_img,
                                                            "transform": (screen_width / 6, screen_height / 8)})

            else:

                buttons["confirm"] = ObjectsDrawManager.image({"coordinates": (screen_width / 2, screen_height / 1.5),
                                                               "img": confirm_img,
                                                               "transform": (screen_width / 3.5, screen_height / 8)})
                buttons["back"] = ObjectsDrawManager.image({"coordinates": (screen_width / 2, screen_height / 1.25),
                                                            "img": back_img,
                                                            "transform": (screen_width / 6, screen_height / 8)})

            for event in pygame.event.get():

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    for button in buttons:
                        if buttons[button].collidepoint(event.pos):
                            self.button_collide(button, self.text, default_text)
                            self.text = ""

                elif event.type == pygame.KEYDOWN:
                    self.act_color = black_col

                    if event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    elif len(self.text) < text_len:
                        self.text += event.unicode

            pygame.display.update()

    def button_collide(self, button, text, default_text):

        if button == "join":
            self.default_event = "join"

            if text == "" or text == default_text:
                self.act_color = purple_col
            else:
                self.nickname = text
                self.event = "join"

        elif button == "create":
            self.default_event = "create"

            if text == "" or text == default_text:
                self.act_color = purple_col
            else:
                self.nickname = text
                self.event = "create"

        elif button == "confirm":

            if text == "" or text == default_text:
                self.act_color = purple_col
            else:
                if self.event == "join":
                    try:
                        self.room_number = int(text)
                        self.event = "create"
                    except ValueError:
                        self.act_color = purple_col

                elif self.event == "create":
                    self.password = text
                    self.connect()

        elif button == "back":
            self.act_color = black_col

            if self.event == "join":
                self.event = "menu"
            elif self.event == "create":

                if self.default_event == "join":
                    self.event = "join"
                elif self.default_event == "create":
                    self.event = "menu"

        elif button == "quit":
            print("Process finished")
            sys.exit()

    def connect(self):

        ObjectsDrawManager.image({"img": menu_bg_img,
                                  "coordinates": (screen_width / 2, screen_height / 2),
                                  "transform": (screen_width, screen_height)})
        ObjectsDrawManager.text({"coordinates": (screen_width / 2, screen_height / 1.8),
                                 "font": base_font_50,
                                 "text": "Loading...",
                                 "color": black_col})

        pygame.display.update()

        network = Network()

        dispatch = {"event": self.default_event,
                    "nickname": self.nickname,
                    "room_number": self.room_number,
                    "password": self.password}

        receive = network.connect(dispatch)
        verdict = receive["verdict"]

        if type(verdict) == int:
            player_number = verdict

            text = Game(player_number, network).main()

            bg = table_img

        elif type(verdict) == str:
            text = verdict
            bg = menu_bg_img

        else:
            text = "Connection to server failed."
            bg = menu_bg_img

        ObjectsDrawManager.image({"img": bg,
                                  "coordinates": (screen_width / 2, screen_height / 2),
                                  "transform": (screen_width, screen_height)})
        ObjectsDrawManager.text({"coordinates": (screen_width / 2, screen_height / 1.8),
                                 "font": base_font_50,
                                 "text": text,
                                 "color": black_col})

        pygame.display.update()
        time.sleep(2)

        self.event = "menu"


Menu("menu").main()
