#from http.server import BaseHTTPRequestHandler, HTTPServer
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import json
import numpy as np
from scipy.fft import fft
import time
from filtro_pdm import processar_pdm

import socket
import queue

HOST = "0.0.0.0"
PORT = 8000

TCP_PORT = 8001
TAMANHO_BLOCO = 4088

fila_processamento = queue.Queue()


buffer_dados = b""
freq_bruto = mag_bruto = freq_filtrado = mag_filtrado = None

# CONTADOR DE PACOTES
pacotes_recebidos = 0
bytes_recebidos = 0

sinal_bruto_acumulado = []
sinal_filtrado_acumulado = []

#HTTPServer.last_fft = ([], [])

def processar_bloco_recebido(data):
    global buffer_dados
    global pacotes_recebidos, bytes_recebidos
    global sinal_bruto_acumulado, sinal_filtrado_acumulado
    global freq_bruto, mag_bruto, freq_filtrado, mag_filtrado
    global sinal_bruto

    MIN_AMOSTRAS = 4096 * 4

    pacotes_recebidos += 1
    bytes_recebidos += len(data)

    print(
        f"[{pacotes_recebidos}] Pacote recebido com "
        f"{len(data)} bytes (Total: {bytes_recebidos} bytes)"
    )

    buffer_dados += data

    if len(buffer_dados) < 128:
        return

    MAX_BUFFER = MIN_AMOSTRAS * 2

    if len(buffer_dados) > MAX_BUFFER:
        buffer_dados = buffer_dados[-MAX_BUFFER:]

    if len(buffer_dados) >= MIN_AMOSTRAS:
        try:
            janela = buffer_dados[-MIN_AMOSTRAS:]

            data_uint32 = np.frombuffer(
                janela,
                dtype=np.uint32
            )

            bits = np.unpackbits(
                data_uint32.byteswap().view(np.uint8)
            )

            sinal_pdm = 2 * bits.astype(np.int8) - 1
            sinal_bruto = sinal_pdm.copy()

            sinal_filtrado = processar_pdm(sinal_pdm)

            globals()["ultimo_sinal_bruto"] = sinal_pdm.copy()
            globals()["ultimo_sinal_filtrado"] = sinal_filtrado.copy()

            sinal_bruto_acumulado.extend(
                sinal_pdm.astype(np.float32).tolist()
            )

            sinal_filtrado_acumulado.extend(
                sinal_filtrado.astype(np.float32).tolist()
            )

            def calcular_fft(signal, fs):
                Nfft = len(signal)

                janela_fft = np.hanning(Nfft)
                sinal_janelado = signal * janela_fft

                spec = np.fft.rfft(sinal_janelado)

                psd_spec = (
                    np.abs(spec) ** 2
                ) * (1 / (fs * Nfft))

                psd_spec[1:-1] *= 2

                freq = np.linspace(
                    0,
                    fs / 2,
                    len(psd_spec)
                )

                mag_dB = 10 * np.log10(psd_spec + 1e-20)

                return freq, mag_dB

            fs = 5_000_000

            freq_bruto, mag_bruto_atual = calcular_fft(
                sinal_bruto,
                fs
            )

            freq_filtrado, mag_filtrado_atual = calcular_fft(
                sinal_filtrado,
                fs / 16
            )

            if mag_bruto is None:
                mag_bruto = mag_bruto_atual
            else:
                mag_bruto = np.maximum(
                    mag_bruto,
                    mag_bruto_atual
                )

            if mag_filtrado is None:
                mag_filtrado = mag_filtrado_atual
            else:
                mag_filtrado = np.maximum(
                    mag_filtrado,
                    mag_filtrado_atual
                )

            buffer_dados = b""

            print(
                f"FFT atualizada com "
                f"{len(sinal_pdm)} amostras"
            )

        except Exception as e:
            print(f"Erro ao processar FFT: {e}")

def processar_fila():
    global buffer_dados, freq_bruto, mag_bruto, freq_filtrado, mag_filtrado
    
    # Tamanho necessário para a janela da FFT (16.384 bytes)
    TAMANHO_JANELA_FFT = 16384
    
    while True:
        try:
            bloco = fila_processamento.get()
            if bloco is None:
                break
            
            # Acumula o bloco recebido no buffer local de processamento
            buffer_dados += bloco
            
            # Se o buffer atingiu o tamanho necessário para a FFT, processa imediatamente
            if len(buffer_dados) >= TAMANHO_JANELA_FFT:
                dados_para_fft = buffer_dados[:TAMANHO_JANELA_FFT]
                # Mantém o residual para o próximo bloco
                buffer_dados = buffer_dados[TAMANHO_JANELA_FFT:]
                
                # Executa o desempacotamento PDM e cálculo da FFT
                # (Isso atualiza mag_bruto e mag_filtrado usando np.maximum internamente)
                processar_bloco_recebido(dados_para_fft)
                
            fila_processamento.task_done()
        except Exception as e:
            print(f"Erro na thread de processamento: {e}")

def receber_tcp():
    global buffer_dados

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, TCP_PORT))
    servidor.listen(1)

    print(f"Servidor TCP aguardando conexão na porta {TCP_PORT}...")

    while True:
        conexao, endereco = servidor.accept()
        print(f"ESP32 conectado via TCP: {endereco}")

        # Limpa os buffers de bytes de rede para garantir alinhamento rígido de 32 bits
        buffer_tcp = b""
        buffer_dados = b""
        
        # Esvazia resíduos da fila de blocos
        while not fila_processamento.empty():
            try:
                fila_processamento.get_nowait()
                fila_processamento.task_done()
            except queue.Empty:
                break

        try:
            while True:
                # Leitura direta e ultra rápida do socket TCP (evita travar o ESP32)
                dados = conexao.recv(16384)
                if not dados:
                    break

                buffer_tcp += dados

                # Fatia o fluxo estritamente em blocos de 4.088 bytes
                while len(buffer_tcp) >= TAMANHO_BLOCO:
                    bloco = buffer_tcp[:TAMANHO_BLOCO]
                    buffer_tcp = buffer_tcp[TAMANHO_BLOCO:]
                    fila_processamento.put(bloco)

        except Exception as e:
            print(f"Erro na recepção TCP: {e}")
        finally:
            conexao.close()
            print("Conexão TCP encerrada.")


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        global freq_bruto, mag_bruto, freq_filtrado, mag_filtrado, sinal_bruto
        global ultimo_sinal_bruto, ultimo_sinal_filtrado
        global sinal_bruto_acumulado, sinal_filtrado_acumulado
        global capturando

        if self.path == "/":
            try:
                with open("index.html", "rb") as f:
                    content = f.read()

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content)

            except Exception as e:
                self.send_error(500, f"Erro ao abrir index.html: {e}")

        elif self.path == "/dados_fft":

            if (freq_bruto is None or mag_bruto is None or
                    freq_filtrado is None or mag_filtrado is None):

                data = {
                    "freq_bruto": [],
                    "spec_bruto": [],
                    "freq_filtrado": [],
                    "spec_filtrado": []
                }

            else:
                data = {
                    "freq_bruto": np.array(freq_bruto).tolist(),
                    "spec_bruto": np.array(mag_bruto).tolist(),
                    "freq_filtrado": np.array(freq_filtrado).tolist(),
                    "spec_filtrado": np.array(mag_filtrado).tolist()
                }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())

        elif self.path == "/dados_brutos":
            try:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()

                if "ultimo_sinal_bruto" in globals():
                    self.wfile.write(
                        json.dumps(
                            {"amostras": sinal_bruto_acumulado}
                        ).encode()
                    )
                else:
                    self.wfile.write(
                        json.dumps({"amostras": []}).encode()
                    )

            except Exception as e:
                self.send_error(500, f"Erro ao retornar sinal bruto: {e}")

        elif self.path == "/dados_filtrados":
            try:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()

                if "ultimo_sinal_filtrado" in globals():
                    self.wfile.write(
                        json.dumps(
                            {"amostras": sinal_filtrado_acumulado}
                        ).encode()
                    )
                else:
                    self.wfile.write(
                        json.dumps({"amostras": []}).encode()
                    )

            except Exception as e:
                self.send_error(500, f"Erro ao retornar sinal filtrado: {e}")

        else:
            self.send_error(404, "Caminho nao encontrado")

    def do_POST(self):
        global buffer_dados, freq_atual, mag_atual, sinal_bruto
        global pacotes_recebidos, bytes_recebidos
        global sinal_bruto_acumulado, sinal_filtrado_acumulado
        global capturando
        global freq_bruto, mag_bruto, freq_filtrado, mag_filtrado

        if self.path == "/upload":

            MIN_AMOSTRAS = 4096 * 4

            content_length = int(self.headers["Content-Length"])
            data = self.rfile.read(content_length)

            pacotes_recebidos += 1
            bytes_recebidos += len(data)

            print(
                f"[{pacotes_recebidos}] Pacote recebido com "
                f"{len(data)} bytes (Total: {bytes_recebidos} bytes)"
            )

            buffer_dados += data

            if len(buffer_dados) < 128:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
                return

            MAX_BUFFER = MIN_AMOSTRAS * 2

            if len(buffer_dados) > MAX_BUFFER:
                buffer_dados = buffer_dados[-MAX_BUFFER:]

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

            if len(buffer_dados) >= MIN_AMOSTRAS:
                try:
                    janela = buffer_dados[-MIN_AMOSTRAS:]

                    data_uint32 = np.frombuffer(
                        janela,
                        dtype=np.uint32
                    )

                    bits = np.unpackbits(
                        data_uint32.byteswap().view(np.uint8)
                    )

                    sinal_pdm = 2 * bits.astype(np.int8) - 1
                    sinal_bruto = sinal_pdm.copy()

                    sinal_filtrado = processar_pdm(sinal_pdm)

                    globals()["ultimo_sinal_bruto"] = sinal_pdm.copy()
                    globals()["ultimo_sinal_filtrado"] = sinal_filtrado.copy()

                    sinal_bruto_acumulado.extend(
                        sinal_pdm.astype(np.float32).tolist()
                    )

                    sinal_filtrado_acumulado.extend(
                        sinal_filtrado.astype(np.float32).tolist()
                    )

                    def calcular_fft(signal, fs):
                        Nfft = len(signal)

                        janela_fft = np.hanning(Nfft)
                        sinal_janelado = signal * janela_fft

                        spec = np.fft.rfft(sinal_janelado)

                        psd_spec = (
                            np.abs(spec) ** 2
                        ) * (1 / (fs * Nfft))

                        psd_spec[1:-1] *= 2

                        freq = np.linspace(
                            0,
                            fs / 2,
                            len(psd_spec)
                        )

                        mag_dB = 10 * np.log10(psd_spec + 1e-20)

                        return freq, mag_dB

                    fs = 5_000_000

                    freq_bruto, mag_bruto_atual = calcular_fft(
                        sinal_bruto,
                        fs
                    )

                    freq_filtrado, mag_filtrado_atual = calcular_fft(
                        sinal_filtrado,
                        fs / 16
                    )

                    if mag_bruto is None:
                        mag_bruto = mag_bruto_atual
                    else:
                        mag_bruto = np.maximum(
                            mag_bruto,
                            mag_bruto_atual
                        )

                    if mag_filtrado is None:
                        mag_filtrado = mag_filtrado_atual
                    else:
                        mag_filtrado = np.maximum(
                            mag_filtrado,
                            mag_filtrado_atual
                        )

                    buffer_dados = b""

                    print(
                        f"FFT atualizada com "
                        f"{len(sinal_pdm)} amostras"
                    )

                except Exception as e:
                    print(f"Erro ao processar FFT: {e}")

        else:
            self.send_error(404, "Caminho nao encontrado")


def run_server():

    threading.Thread(target=processar_fila, daemon=True).start()
    threading.Thread(target=receber_tcp, daemon=True).start()

    #server = HTTPServer((HOST, PORT), MyHandler)
    server = ThreadingHTTPServer((HOST, PORT), MyHandler)

    print(f"Servidor HTTP rodando em http://{HOST}:{PORT}")

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nEncerrando servidor.")
        server.server_close()


if __name__ == "__main__":
    run_server()