import socket
from _thread import *
import pickle
from game import Game

server = "127.0.0.1"

port = 5556

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print("SOCKET ERROR")
    print(e)

s.listen(5)
print("Server started, waiting for connection")

games = {}


class ThreadedClient:

    def __init__(self, client_socket, game_id, nickname, player_number):

        self.client_socket = client_socket
        self.game_id = game_id
        self.nickname = nickname
        self.player_number = player_number
        self.game = None
        self.main()

    def main(self):

        print(f"Player \"{self.nickname}\", id \"{self.player_number}\", "
              f"room \"{self.game_id}\" - CONNECTED: Connection opened.")

        while True:

            try:

                receive = pickle.loads(self.client_socket.recv(2048))

                if games[self.game_id] is not None:

                    self.game = games[self.game_id]

                    event = receive["event"]
                    card_id = receive.get("card_id")
                    who = receive.get("whose")
                    card_index = receive.get("card_index")

                    if event == "start":
                        start_new_thread(self.game.start_game, ())

                    elif event == "hint":
                        start_new_thread(self.game.event_hint, (self.player_number, card_id, who))

                    elif event == "discard":
                        start_new_thread(self.game.event_discard, (self.player_number, card_id, card_index))

                    elif event == "play":
                        start_new_thread(self.game.event_play, (self.player_number, card_id, card_index))

                    elif event == "superhint":
                        start_new_thread(self.game.event_superhint, (self.player_number, card_id, who))

                    elif event == "recycling":
                        start_new_thread(self.game.event_recycling, (self.player_number, card_id))

                    elif event == "adrenalin":
                        start_new_thread(self.game.event_adrenalin, (self.player_number, card_id))

                    elif event == "quit":
                        print(f"Player \"{self.nickname}\", id \"{self.player_number}\", "
                              f"room \"{self.game_id}\" - PLAYER LEFT: Connection closed.")
                        break

                    self.client_socket.sendall(pickle.dumps(self.game))

            except:
                print(f"Player \"{self.nickname}\", id \"{self.player_number}\", "
                      f"room \"{self.game_id}\" - ERROR OCCURRED: Connection closed.")
                break

        self.game.players.pop(self.player_number)
        self.client_socket.close()

        if len(self.game. players) == 0:
            del games[self.game_id]


while True:

    client_socket, addr = s.accept()
    receive = pickle.loads(client_socket.recv(2048))

    event = receive["event"]
    nickname = receive["nickname"]
    room_number = receive["room_number"]
    password = receive["password"]

    if event == "create":

        index = len(games)

        games[index] = Game(index, password, nickname)

        game_id = index
        player_number = 0

        start_new_thread(ThreadedClient, (client_socket, game_id, nickname, player_number))
        client_socket.sendall(pickle.dumps({"verdict": player_number}))

    elif event == "join":

        try:
            verdict = games[room_number].join(nickname, password)
        except:
            verdict = "Invalid room number."

        if type(verdict) == int:

            game_id = room_number
            player_number = verdict

            start_new_thread(ThreadedClient, (client_socket, game_id, nickname, player_number))

        client_socket.sendall(pickle.dumps({"verdict": verdict}))
