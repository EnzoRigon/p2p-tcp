import socket
import threading
from naval_battle_game import NavyBattleGame
import sys
import netifaces

PORT = 8080
exit_event = threading.Event()

def send_message(sock, message):
    """Envia uma mensagem ao peer."""
    sock.sendall(message.encode())

def receive_message(sock):
    """Recebe uma mensagem do peer."""
    return sock.recv(1024).decode()

def start_game(sock, is_server, game_state_json=None):
    """Lógica principal do jogo."""
    if game_state_json:
        game = NavyBattleGame(game_state_json)
    else:
        game = NavyBattleGame()

    try:
        if not game_state_json:
            if is_server:
                send_message(sock, game.export_player_ships_to_json())
                print("Aguardando navios do oponente...")
                ships_json = receive_message(sock)
                game.receive_opponent_ships(ships_json)
                game.is_player_turn = True
            else:
                print('Agurdando navios do oponente...')
                ships_json = receive_message(sock)
                game.receive_opponent_ships(ships_json)
                send_message(sock, game.export_player_ships_to_json())
                game.is_player_turn = False

        print("Tabuleiros configurados! Que comece o jogo!")
        game.print_boards()
    except Exception as e:
        print(f"Erro durante a configuração inicial: {e}")
        game.save_game()
        sys.exit(1)

    while not game.game_over:
        try:
            if game.is_player_turn:
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
                        game.print_shot_result(result)
                        if not game.opponent_ships:
                            game.print_game_result(True)
                            game.game_over = True
                        game.print_boards()
                        break
                    except ValueError as e:
                        print(e)
                game.is_player_turn = False
            else:
                print("Aguardando jogada do oponente...")
                coordinates = receive_message(sock)
                coordinates = (int(coordinates[0]), int(coordinates[1]))
                hit = game.process_attack(coordinates)
                if not game.player_ships:
                    game.print_game_result(False)
                    game.game_over = True
                game.print_boards()  
                game.is_player_turn = True

        except (socket.error, KeyboardInterrupt) as e:
            print(f"Jogo interrompido: {e}")
            game.save_game()  
            print("Estado do jogo salvo.")
            try:
                sock.close()
                print("Conexão TCP encerrada.")
            except Exception as e:
                print(f"Erro ao encerrar a conexão: {e}")
            return

    if game.game_over:
        print("Jogo concluído! Obrigado por jogar.")
        
        try:
            import os
            os.remove("navy_battle_save.json")
            print("Arquivo de salvamento removido.")
        except FileNotFoundError:
            pass
        try:
            sock.close()
            print("Conexão TCP encerrada.")
        except Exception as e:
            print(f"Erro ao encerrar a conexão: {e}")

def get_first_interface_ip():
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            for addr in addresses[netifaces.AF_INET]:
                ip = addr['addr']
                if not ip.startswith("127."):
                    return ip
    return None

def start_server(game_state_json=None):
    """Inicia o servidor."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip_address = get_first_interface_ip()
    if not ip_address:
        print("Não foi possível obter o endereço IP da primeira interface.")
        return
    server_socket.bind((ip_address, PORT))
    server_socket.listen(1)
    print(f"Aguardando conexão em {ip_address}:{PORT}...")
    conn, addr = server_socket.accept()
    print(f"Conexão estabelecida com {addr}")
    start_game(conn, is_server=True, game_state_json=game_state_json)

def start_client(ip, game_state_json=None):
    """Inicia o cliente."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, PORT))
    print(f"Conectado ao servidor {ip}:{PORT}")
    start_game(client_socket, is_server=False, game_state_json=game_state_json)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Batalha naval P2P.")
    parser.add_argument("--ip", type=str, help="Endereço IP do servidor (opcional para cliente).")
    parser.add_argument("--game-state", type=str, help="JSON contendo o estado do jogo (opcional).")
    args = parser.parse_args()

    game_state_json = None
    if args.game_state:
        with open(args.game_state, 'r') as f:
            game_state_json = f.read()

    if args.ip:
        start_client(args.ip, game_state_json=game_state_json)
    else:
        start_server(game_state_json=game_state_json)