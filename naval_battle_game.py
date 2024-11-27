import json
import random
from colorama import Fore, init

init(autoreset=True)

class NavyBattleGame:
    def __init__(self, game_state_json=None):
        self.board_size = 10
        self.player_board = [["~"] * self.board_size for _ in range(self.board_size)]
        self.opponent_board = [["~"] * self.board_size for _ in range(self.board_size)]
        self.player_ships = []
        self.opponent_ships = {}
        self.game_over = False
        self.is_player_turn = None

        if game_state_json:
            self.load_game_from_json(game_state_json)
        else:
            self.place_player_ships()

    def load_game_from_json(self, game_state_json):
        """Carrega o estado do jogo a partir de um JSON."""
        game_state = json.loads(game_state_json)
        self.player_board = game_state["player_board"]
        self.opponent_board = game_state["opponent_board"]
        self.player_ships = game_state["player_ships"]
        self.opponent_ships = game_state["opponent_ships"]
        self.is_player_turn = game_state["is_player_turn"]

    def place_player_ships(self):
        """Posiciona automaticamente os navios do jogador."""
        ship_sizes = {
            "porta-avioes": 5,
            "encouracado": 4,
            "cruzador": 3,
            "destroier": 2
        }
        for ship_type, size in ship_sizes.items():
            count = 2 if ship_type in ["cruzador", "destroier"] else 1
            for _ in range(count):
                while True:
                    orientation = random.choice(["horizontal", "vertical"])
                    x = random.randint(0, self.board_size - (size if orientation == "vertical" else 1))
                    y = random.randint(0, self.board_size - (size if orientation == "horizontal" else 1))

                    positions = [
                        (x + i, y) if orientation == "vertical" else (x, y + i)
                        for i in range(size)
                    ]
                    if all(self.player_board[pos[0]][pos[1]] == "~" for pos in positions):
                        for pos in positions:
                            self.player_board[pos[0]][pos[1]] = "S"
                        self.player_ships.append(positions)
                        break

    def receive_opponent_ships(self, ships_json):
        """Recebe e configura os navios do oponente a partir de JSON."""
        ships = json.loads(ships_json)
        for index, ship in enumerate(ships):
            positions = [tuple(pos) for pos in ship["posicoes"]]
            self.opponent_ships[f'Navio #{index} {ship["tipo"]}'] = positions

    def export_player_ships_to_json(self):
        """Exporta os navios do jogador para JSON."""
        ships_data = []
        ship_types = ["porta-avioes", "encouracado", "cruzador", "cruzador", "destroier", "destroier"]
        for ship_type, positions in zip(ship_types, self.player_ships):
            ships_data.append({"tipo": ship_type, "posicoes": positions})
        return json.dumps(ships_data)

    def process_attack(self, coordinates):
        """Processa um ataque recebido."""
        x, y = coordinates
        hit = False
        for ship in self.player_ships:
            if (x, y) in ship:
                ship.remove((x, y))
                self.player_board[x][y] = "X"
                hit = True
                if not ship:
                    self.player_ships.remove(ship)
                break
        if not hit:
            self.player_board[x][y] = "O"
        return hit

    def attack_opponent(self, coordinates):
        """Registra o ataque no tabuleiro do oponente."""
        x, y = coordinates
        if self.opponent_board[x][y] not in ["~"]:  # Ignorar células já atacadas
            return False
        for ship_key, positions in self.opponent_ships.items():
            if (x, y) in positions:
                self.opponent_board[x][y] = "X"  # Marca como acerto
                positions.remove((x, y))
                if not positions:
                    print(Fore.GREEN + f"Você derrubou o {ship_key} do oponente!")
                    del self.opponent_ships[ship_key]  # Remove o navio se afundado
                return True
        self.opponent_board[x][y] = "O"  # Marca como erro
        return False


    def print_boards(self):
        """Imprime os tabuleiros do jogador e do oponente lado a lado, com espaçamento adequado."""
        # Espaçamento entre os tabuleiros
        spacing = " " * 10

        # Cabeçalho dos tabuleiros
        header = f"{'Seu Tabuleiro':^{self.board_size * 2}}{spacing}{'Tabuleiro do Oponente':^{self.board_size * 2}}"
        print(header)
        print("-" * len(header))  # Linha separadora

        for row_player, row_opponent in zip(self.player_board, self.opponent_board):
            # Constrói as linhas do jogador e do oponente
            player_row = " ".join(self.format_cell(cell, is_player=True) for cell in row_player)
            opponent_row = " ".join(self.format_cell(cell, is_player=False) for cell in row_opponent)
            # Imprime as linhas com o espaçamento definido
            print(f"{player_row:<{self.board_size * 2}}{spacing}{opponent_row:<{self.board_size * 2}}")
        print()


    def format_cell(self, cell, is_player):
        """Formata a célula com cores apropriadas."""
        if cell == "S":
            return Fore.GREEN + cell if is_player else "~"  # O oponente nunca vê navios
        elif cell == "X":
            return Fore.RED + cell  # Acerto
        elif cell == "O":
            return Fore.YELLOW + cell  # Erro
        else:
            return Fore.CYAN + cell  # Água (~)

    def save_game(self, file_name="navy_battle_save.json"):
        """
        Salva o estado atual do jogo em um arquivo JSON.
        """
        game_state = {
            "player_board": self.player_board,
            "opponent_board": self.opponent_board,
            "player_ships": self.player_ships,
            "opponent_ships": self.opponent_ships,
            "is_player_turn": self.is_player_turn
        }
        with open(file_name, "w") as save_file:
            json.dump(game_state, save_file, indent=4)
        print(f"Jogo salvo no arquivo: {file_name}")

    def load_game(self, file_name="navy_battle_save.json"):
        """
        Carrega o estado do jogo de um arquivo JSON.
        """
        try:
            with open(file_name, "r") as save_file:
                game_state = json.load(save_file)
                self.player_board = game_state["player_board"]
                self.opponent_board = game_state["opponent_board"]
                self.player_ships = game_state["player_ships"]
                self.opponent_ships = game_state["opponent_ships"]
                self.is_player_turn = game_state["is_player_turn"]
            print(f"Jogo carregado do arquivo: {file_name}")
        except FileNotFoundError:
            print("Nenhum arquivo de salvamento encontrado. Começando um novo jogo.")

    def print_shot_result(self, result):
        """Imprime o resultado de um ataque."""
        if result:
            print(Fore.GREEN + "Você acertou!")
        else:
            print(Fore.RED + "Você errou!")

    def print_game_result(self, result):
        """Imprime o resultado de um ataque."""
        if result:
            print(Fore.GREEN + "Todos os navios do oponente foram destruídos! Você venceu!")
        else:
            print(Fore.RED + "Todos os seus navios foram destruídos! Você perdeu!")