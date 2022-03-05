from node.node import Node
from sys import argv, exit


if __name__ == "__main__":
    if len(argv) == 2:
        host, port = argv[1].split(":")
        node = Node(host, port)
        node.start_p2p()
        node.start_api()
    else:
        print(f"Usage: {argv[0]} [host:port]")
        exit(2)
