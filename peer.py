import socket
import threading
import json
from naval_battle_game import NavyBattleGame

PORT = 8080
exit_event = threading.Event()

def send_message(sock, message):
    """Envia uma mensagem ao peer."""
    sock.sendall(message.encode())

def receive_message(sock):
    """Recebe uma mensagem do peer."""
    return sock.recv(1024).decode()

def start_game(sock, is_server):
    """Lógica principal do jogo."""
    game = NavyBattleGame()
    if is_server:
        print("Aguardando navios do oponente...")
        ships_json = receive_message(sock)
        game.receive_opponent_ships(ships_json)
        send_message(sock, game.export_player_ships_to_json())
    else:
        send_message(sock, game.export_player_ships_to_json())
        ships_json = receive_message(sock)
        game.receive_opponent_ships(ships_json)

    print("Tabuleiros configurados! Que comece o jogo!")
    game.print_boards()

    turn = is_server
    while not game.game_over:
        if turn:
            print("Seu turno!")
            while True:
                try:
                    coordinates = input("Digite as coordenadas (ex: 23 para linha 2 e coluna 3): ")
                    if len(coordinates) != 2 or not coordinates.isdigit():
                        raise ValueError("Entrada inválida. Certifique-se de digitar exatamente dois dígitos.")
                    x, y = int(coordinates[0]), int(coordinates[1])
                    if game.opponent_board[x][y] in ["X", "O"]:
                        raise ValueError("Você já atacou aqui! Tente novamente.")
                    send_message(sock, f'{x}{y}')
                    result = game.attack_opponent((x, y))
                    if result:
                        print("Você acertou!")
                    else:
                        print("Você errou!")
                    game.print_boards()  # Atualiza os tabuleiros após a jogada do jogador
                    break
                except ValueError as e:
                    print(e)
            turn = False
        else:
            print("Aguardando jogada do oponente...")
            coordinates = receive_message(sock)
            coordinates = (int(coordinates[0]), int(coordinates[1]))
            hit = game.process_attack(coordinates)
            if not game.player_ships:
                print("Todos os seus navios foram destruídos! Você perdeu!")
                game.game_over = True
            game.print_boards()  # Atualiza os tabuleiros após a jogada do oponente
            turn = True

def start_server():
    """Inicia o servidor."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip_address = socket.gethostbyname(socket.gethostname())
    server_socket.bind((ip_address, PORT))
    server_socket.listen(1)
    print(f"Aguardando conexão em {ip_address}:{PORT}...")
    conn, addr = server_socket.accept()
    print(f"Conexão estabelecida com {addr}")
    start_game(conn, is_server=True)

def start_client(ip):
    """Inicia o cliente."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, PORT))
    print(f"Conectado ao servidor {ip}:{PORT}")
    start_game(client_socket, is_server=False)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Batalha naval P2P.")
    parser.add_argument("--ip", type=str, help="Endereço IP do servidor (opcional para cliente).")
    args = parser.parse_args()

    if args.ip:
        start_client(args.ip)
    else:
        start_server()