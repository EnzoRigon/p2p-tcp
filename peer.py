import socket
import threading
import argparse
import sys

# Evento para sinalizar para ambos os *threads* encerrarem
exit_event = threading.Event()

def receive_messages(peer_socket):
    """Função para tratar mensagens recebidas."""
    try:
        while not exit_event.is_set():
            message = peer_socket.recv(1024).decode()
            if message:
                if message.lower() == "exit":
                    print("\nPeer desconectou. Encerrando chat.")
                    exit_event.set()
                    break
                print("\nPeer:", message)
            else:
                print("\nPeer desconectou.")
                exit_event.set()
                break
    except Exception as e:
        if not exit_event.is_set():  # Só exibir erro se não estiver saindo
            print("\nErro ao receber mensagem:", str(e))
    finally:
        peer_socket.close()

def send_messages(peer_socket):
    """Função para tratar envio de mensagens."""
    try:
        while not exit_event.is_set():
            message = input("Você: ")
            if message.lower() == "exit":
                peer_socket.sendall(message.encode())
                print("Saindo do chat.")
                exit_event.set()
                break
            peer_socket.sendall(message.encode())
    except Exception as e:
        if not exit_event.is_set():  # Só exibir erro se não estiver saindo
            print("\nErro ao enviar mensagem:", str(e))
    finally:
        peer_socket.close()

def handle_connection(server_socket):
    """Função para aceitar conexões de entrada."""
    while not exit_event.is_set():
        try:
            peer_socket, addr = server_socket.accept()
            print(f"\nConexão aceita de {addr}")
            
            # Inicia threads para enviar e receber mensagens com o novo peer
            threading.Thread(target=receive_messages, args=(peer_socket,), daemon=True).start()
            threading.Thread(target=send_messages, args=(peer_socket,), daemon=True).start()
        except Exception as e:
            if not exit_event.is_set():
                print("\nErro ao aceitar conexão:", str(e))
            break

def connect_to_peer(port):
    """Solicita o IP do peer e tenta estabelecer uma conexão."""
    while not exit_event.is_set():
        try:
            target_ip = input("\nDigite o IP do peer para conectar (ou 'exit' para sair): ")
            if target_ip.lower() == "exit":
                print("Encerrando chat.")
                exit_event.set()
                break

            # Conecta ao peer especificado
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((target_ip, port))
            print(f"Conectado ao peer em {target_ip}:{port}")

            # Inicia threads para enviar e receber mensagens
            threading.Thread(target=receive_messages, args=(peer_socket,), daemon=True).start()
            threading.Thread(target=send_messages, args=(peer_socket,), daemon=True).start()
            break
        except Exception as e:
            print(f"Erro ao conectar ao peer: {e}")
            continue

def start_peer(ip):
    """Função para iniciar o peer no modo servidor e cliente simultaneamente."""
    port = 8080

    # Inicia o servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((ip, port))
    server_socket.listen(1)
    print(f"Escutando por conexões em {ip}:{port}...")

    # Inicia a thread para aceitar conexões de entrada
    threading.Thread(target=handle_connection, args=(server_socket,), daemon=True).start()

    # Solicita o IP do peer para conectar
    connect_to_peer(port)

    # Espera que a aplicação seja encerrada
    while not exit_event.is_set():
        pass

    server_socket.close()
    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aplicativo de chat P2P.")
    parser.add_argument("--ip", type=str, required=True, help="Endereço IP para escutar conexões")

    args = parser.parse_args()

    start_peer(args.ip)
