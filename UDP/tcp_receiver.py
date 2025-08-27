import socket
import sys
import signal

# CONFIGURAÇÕES
TCP_IP = "0.0.0.0" 
TCP_PORT = 12345
ARQUIVO_RAW = "dados_recebidos_TCP.raw"
BUFFER_SIZE = 4096

#CRIAR SOCKET TCP
print("[DEBUG] Criando socket TCP...")
#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)



try:
    server_socket.bind((TCP_IP, TCP_PORT))
    server_socket.listen(1)
    print(f"[DEBUG] Servidor aguardando conexão em {TCP_IP}:{TCP_PORT}...")
except Exception as e:
    print(f"[ERRO] Falha ao fazer bind: {e}")
    exit(1)

# ==== ACEITA CONEXÃO ====
conn, addr = server_socket.accept()
print(f"[DEBUG] Conexão estabelecida com {addr}")

bytes_recebidos = 0

def finalizar(sig, frame):
    print(f"\n[DEBUG] Encerrando. {bytes_recebidos} bytes recebidos.")
    conn.close()
    server_socket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, finalizar)

# ==== RECEBE DADOS ====
with open(ARQUIVO_RAW, "wb") as f:
    try:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            f.write(data)
            bytes_recebidos += len(data)

            # Log a cada 100 KB recebidos
            if bytes_recebidos % 100000 < BUFFER_SIZE:
                print(f"[DEBUG] {bytes_recebidos} bytes recebidos")
    except Exception as e:
        print(f"[ERRO] Falha durante a recepção: {e}")

print(f"[DEBUG] Aquisição finalizada. {bytes_recebidos} bytes salvos.")
conn.close()
server_socket.close()
