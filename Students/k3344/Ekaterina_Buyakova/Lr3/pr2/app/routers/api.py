import socket

from core import settings
from fastapi import Depends, APIRouter

router = APIRouter()


def get_socket() -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        sock.connect((settings.PARSER_HOST, settings.PARSER_PORT))
        return sock
    except socket.error as err:
        sock.close()
        raise err


@router.get("/")
def parse_url(url: str = "", sock: socket.socket = Depends(get_socket)):
    result = {}
    url += "\n"
    try:
        print(url.encode())
        sock.sendall(url.encode("utf-8"))
        recv_data = sock.recv(1024)
        result = {"url": url, "data": recv_data}
    except socket.timeout:
        result = {"message": "timeout"}
    except socket.error as e:
        result = {"message": f"error: {e}"}
    finally:
        sock.close()
    return result
