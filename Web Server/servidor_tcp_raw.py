import socket
import time

HOST = "0.0.0.0"
TCP_PORT = 8001
TAMANHO_BLOCO = 4088

NOME_ARQUIVO = "sinal_recebido.raw"

def receber_tcp_raw():
    total_bytes = 0
    total_blocos = 0
    sobra = b""

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, TCP_PORT))
    servidor.listen(1)

    print(f"Servidor TCP RAW aguardando conexão com porta {TCP_PORT}... ")

    conexao, endereco = servidor.accept()
    print(f"ESP32 conectado: {endereco}")

    inicio = time.time()

    with open(NOME_ARQUIVO, "wb") as arquivo:
        while True:
            dados = conexao.recv(16384)

            if not dados:
                break

            sobra += dados

            while len(sobra) >= TAMANHO_BLOCO:
                bloco = sobra[:TAMANHO_BLOCO]
                sobra = sobra[TAMANHO_BLOCO:]

                arquivo.write(bloco)
                total_bytes += len(bloco)
                total_blocos += 1

    fim = time.time()

    conexao.close()
    servidor.close()

    print("\nCaptura finalizada")
    print(f"Arquivo salvo: {NOME_ARQUIVO}")
    print(f"Blocos completos salvos: {total_blocos}")
    print(f"Bytes salvos: {total_bytes}")
    print(f"Sobra incompleta descartada: {len(sobra)} bytes")
    print(f"Tempo de recepção: {fim - inicio:.3f} s")

    if total_bytes == total_blocos * TAMANHO_BLOCO:
        print("Tamanho do arquivo OK")
    else:
        print("Erro no tamanho do arquivo")
    

if __name__ == "__main__":
    receber_tcp_raw()
