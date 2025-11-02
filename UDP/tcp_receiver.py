import socket
import sys
import signal

# CONFIGURAÇÕES
TCP_IP = "0.0.0.0" 
TCP_PORT = 12345
ARQUIVO_RAW = "dados_recebidos_TCP.raw"
#ARQUIVO_RAW = "dados_recebidos_TCP_FILT.raw"
#BUFFER_SIZE = 4096
BUFFER_SIZE = 65536
FLUSH_LIMIT = 1 * 1024 * 1024   # 1 MB acumulado antes de gravar no disco

#CRIAR SOCKET TCP
print("[DEBUG] Criando socket TCP...")
#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP
#server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
#server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 262144)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1048576)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)



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
buffer_mem = bytearray()

def finalizar(sig, frame):
    global buffer_mem
    print(f"\n[DEBUG] Encerrando. {bytes_recebidos} bytes recebidos.")
    # grava o que restar no buffer
    if buffer_mem:
        with open(ARQUIVO_RAW, "ab") as f:
            f.write(buffer_mem)
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
            buffer_mem.extend(data)
            bytes_recebidos += len(data)

            # Grava no disco a cada 1 MB acumulado
            if len(buffer_mem) >= FLUSH_LIMIT:
                f.write(buffer_mem)
                buffer_mem.clear()
                f.flush()   # garante que está no disco

            # Log a cada 100 KB
            if bytes_recebidos % 100000 < BUFFER_SIZE:
                print(f"[DEBUG] {bytes_recebidos} bytes recebidos")
                sys.stdout.flush()
    except Exception as e:
        print(f"[ERRO] Falha durante a recepção: {e}")

# grava qualquer sobra
if buffer_mem:
    with open(ARQUIVO_RAW, "ab") as f:
        f.write(buffer_mem)

print(f"[DEBUG] Aquisição finalizada. {bytes_recebidos} bytes salvos.")
conn.close()
server_socket.close()