import socket

UDP_IP = "0.0.0.0" 
UDP_PORT = 12345

print("[DEBUG] Criando socket...")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    print(f"[DEBUG] Fazendo bind em {UDP_IP}:{UDP_PORT}...")
    sock.bind((UDP_IP, UDP_PORT))
except Exception as e:
    print(f"[ERRO] Falha ao fazer bind: {e}")
    exit(1)

print("[DEBUG] Socket pronto. Criando arquivo...")

try:
    with open("dados_recebidos.raw", "wb") as f:
        print("[DEBUG] Arquivo aberto. Aguardando pacotes UDP... (Ctrl+C para parar)")
        while True:
            data, addr = sock.recvfrom(4096)
            f.write(data)
except Exception as e:
    print(f"[ERRO] Durante a execução: {e}")
