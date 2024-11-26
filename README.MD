# Battleship P2P Game

This project is a peer-to-peer (P2P) implementation of the classic Battleship game. It allows two players to connect over a network and play the game in real-time.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Files](#files)
- [Gameplay](#gameplay) 

## Installation

1. **Clone the repository:**
    ```sh
    https://github.com/EnzoRigon/p2p-tcp.git
    cd p2p-tcp
    ```

2. **Build the Docker image:**
    ```sh
    docker build -t battleship-p2p .
    ```

3. **Run the Docker container:**
    ```sh
    docker run -it --rm battleship-p2p
    ```

## Usage

To start the game, you can either run the server or connect as a client.

### Start as Server

```sh
python3 peer.py
```

### Connect as Client

```sh
python3 peer.py --ip <server-ip-address>
```

## Files

- `Dockerfile`: Contains the instructions to build the Docker image.
- `peer.py`: Main script to start the server or client and handle the game logic.
- `naval_battle_game.py`: Contains the game logic and board management.

## Gameplay

1. **Setup:**
    - The server waits for a client to connect.
    - Both players' ships are placed automatically on their boards.

2. **Turns:**
    - Players take turns to attack each other's ships by entering coordinates.
    - The game continues until all ships of one player are destroyed.

3. **Boards:**
    - The player's board and the opponent's board are displayed side by side.
    - Hits are marked with `X`, misses with `O`, and ships with `S`.