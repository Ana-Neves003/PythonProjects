from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import json
import numpy as np
from scipy.fft import fft
import time
from filtro_pdm import processar_pdm

HOST = "0.0.0.0"
PORT = 8000
buffer_dados = b""
freq_bruto = mag_bruto = freq_filtrado = mag_filtrado = None


# CONTADOR DE PACOTES
pacotes_recebidos = 0
bytes_recebidos = 0
sinal_bruto_acumulado = []
sinal_filtrado_acumulado = []

HTTPServer.last_fft = ([], [])

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
            #freq = np.array(freq_atual)
            #spec = np.array(mag_atual)
            #print(f"[DEBUG] Chamado /dados_fft - freq_atual: {None if freq_atual is None else len(freq_atual)}, mag_atual: {None if mag_atual is None else len(mag_atual)}")

            # Verifica se há dados
            if freq_bruto is None or mag_bruto is None or freq_filtrado is None or mag_filtrado is None:
                data = {
                    "freq_bruto": [],
                    "spec_bruto": [],
                    "freq_filtrado": [],
                    "spec_filtrado": []
                }  
            # --- Retorna FFT atual ---
            #if freq_atual is None or mag_atual is None:
            #    data = {"freq": [], "spec": []}
            #else:
            #    freq = np.array(freq_atual)
            #    spec = np.array(mag_atual)

            else: 
                data = {
                #"freq": freq.tolist(),
                #"spec": spec.tolist(),
                    "freq_bruto": np.array(freq_bruto).tolist(),
                    "spec_bruto": np.array(mag_bruto).tolist(),
                    "freq_filtrado": np.array(freq_filtrado).tolist(),
                    "spec_filtrado": np.array(mag_filtrado).tolist(),
                }

            # Retorno HTTP
            self.send_response(200)
            self.send_header("Content-type", "application/json")            
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())

        #ENDEPOINT PARA DOWNLOAD DO SINAL BRUTO
        elif self.path == "/dados_brutos":
            try:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()

                if "ultimo_sinal_bruto" in globals():
                    #self.wfile.write(json.dumps({"amostras": ultimo_sinal_bruto.tolist()}).encode())
                    self.wfile.write(json.dumps({"amostras": sinal_bruto_acumulado}).encode())
                else:
                    self.wfile.write(json.dumps({"amostras": []}).encode())
                    
            except Exception as e:
                self.send_error(500, f"Erro ao retornar sinal bruto: {e}")
            
        # ENDEPOINT PARA DOWNLOAD DO SINAL FILTRADO
        elif self.path == "/dados_filtrados":
            try:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()

                if "ultimo_sinal_filtrado" in globals():
                    #self.wfile.write(json.dumps({"amostras": ultimo_sinal_filtrado.tolist()}).encode())
                    self.wfile.write(json.dumps({"amostras": sinal_filtrado_acumulado}).encode())
                else:
                    self.wfile.write(json.dumps({"amostras": []}).encode())

            except Exception as e:
                self.send_error(500, f"Erro ao retornar sinal filtrado: {e}")

        else:
            self.send_error(404, "Caminho nao encontrado")

    def do_POST(self):
        global buffer_dados, freq_atual, mag_atual, sinal_bruto
        global pacotes_recebidos, bytes_recebidos
        global sinal_bruto_acumulado, sinal_filtrado_acumulado
        global capturando

        if self.path == "/upload":            
            #MIN_AMOSTRAS = 131072 
            MIN_AMOSTRAS = 4096 * 4 
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            #print(f"Recebido {len(data)} bytes de dados.")

            # CONTADOR DE PACOTE
            pacotes_recebidos += 1
            bytes_recebidos += len(data)
            print(f"[{pacotes_recebidos}] Pacote recebido com {len(data)} bytes (Total: {bytes_recebidos} bytes)")

            # --- Acumula os dados recebidos ---
            buffer_dados += data

            # --- Evita processar pacotes muito pequenos ---
            if len(buffer_dados) < 128:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
                return

            # Limita tamanho do buffer (mantém últimas amostras)
            MAX_BUFFER = MIN_AMOSTRAS * 2  # ajuste conforme a RAM do PC
            if len(buffer_dados) > MAX_BUFFER:
                buffer_dados = buffer_dados[-MAX_BUFFER:]

            # Confirma recebimento pro ESP32
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

            # --- Só processa FFT quando tiver amostras suficientes ---  
            if len(buffer_dados) >= MIN_AMOSTRAS:

                # Evita fazer FFT em cada pacote (aguarda 0.5 s)
                #import time
                #if time.time() - getattr(self, "ultimo_fft", 0) < 0.5:
                #    return
                #self.ultimo_fft = time.time()

                try:

                    janela = buffer_dados[-MIN_AMOSTRAS:]
                    # Converte bytes para uint32 (mesmo formato do seu PDM)
                    #data_uint32 = np.frombuffer(buffer_dados, dtype=np.uint32)
                    data_uint32 = np.frombuffer(janela, dtype=np.uint32)

                    # Expande cada uint32 em bits (MSB primeiro)
                    bits = np.unpackbits(data_uint32.byteswap().view(np.uint8))

                    # Converte para bipolar (-1/+1)
                    sinal_pdm = 2 * bits.astype(np.int8) - 1 
                    sinal_bruto = sinal_pdm.copy()    # sinal do gráfico 1 - sinal bruto
                    sinal_filtrado = processar_pdm(sinal_pdm)

                    #ultimo_sinal_bruto = sinal_pdm.copy()
                    #ultimo_sinal_filtrado = sinal_filtrado.copy()

                    #globals()["ultimo_sinal_bruto"] = ultimo_sinal_bruto
                    #globals()["ultimo_sinal_filtrado"] = ultimo_sinal_filtrado

                    globals()["ultimo_sinal_bruto"] = sinal_pdm.copy()
                    globals()["ultimo_sinal_filtrado"] = sinal_filtrado.copy()

                    sinal_bruto_acumulado.extend(sinal_pdm.astype(np.float32).tolist())
                    sinal_filtrado_acumulado.extend(sinal_filtrado.astype(np.float32).tolist())

                    
                    #sinal_pdm = sinal_filtrado # Sinal do gráfico 2 - sinal filtrado

                    #--- Função auxiliar para FFT ---
                    def calcular_fft(signal, fs):
                        Nfft = len(signal)
                        janela = np.hanning(Nfft)
                        sinal_janelado = signal * janela
                        spec = np.fft.rfft(sinal_janelado)
                        psd_spec = (np.abs(spec) ** 2) * (1 / (fs * Nfft))
                        psd_spec[1:-1] *= 2
                        freq = np.linspace(0, fs / 2, len(psd_spec))
                        mag_dB = 10 * np.log10(psd_spec + 1e-20)
                        return freq, mag_dB 
                      
                    # --- FFT do sinal bruto e do filtrado ---
                    fs = 5_000_000
                    freq_bruto, mag_bruto = calcular_fft(sinal_bruto, fs)
                    freq_filtrado, mag_filtrado = calcular_fft(sinal_filtrado, fs / 16)

                    # Atualiza variáveis globais para o /dados_fft
                    #globals()["freq_bruto"] = freq_bruto
                    #globals()["mag_bruto"] = mag_bruto
                    #globals()["freq_filtrado"] = freq_filtrado
                    #globals()["mag_filtrado"] = mag_filtrado

                    # Acumula FFT no servidor usando máximo, igual ao HTML
                    if globals()["mag_bruto"] is None:
                        globals()["freq_bruto"] = freq_bruto
                        globals()["mag_bruto"] = mag_bruto
                    else:
                        globals()["mag_bruto"] = np.maximum(globals()["mag_bruto"], mag_bruto)

                    if globals()["mag_filtrado"] is None:
                        globals()["freq_filtrado"] = freq_filtrado
                        globals()["mag_filtrado"] = mag_filtrado
                    else:
                        globals()["mag_filtrado"] = np.maximum(globals()["mag_filtrado"], mag_filtrado)

                    # Limpa buffer após processar (ou use janela deslizante)
                    buffer_dados = b""

                    print(f"FFT atualizada com {len(sinal_pdm)} amostras")

                except Exception as e:
                    print(f"Erro ao processar FFT: {e}")

            #try:
            #    raw = np.frombuffer(data, dtype=np.uint32)
            #    bits = np.unpackbits(raw.view(np.uint8))
            
            #    bipolar = 2 * bits.astype(np.int8) - 1

            #    Nfft = len(bipolar)
            #    fs = 5_000_000
            #    spec = fft(bipolar)
            #    spec = np.abs(spec[:Nfft // 2])
            #    freq = np.linspace(0, fs / 2, len(spec))

            #    self.server.last_fft = (freq, spec)
            #    print("FFT calculada com sucesso.")
            #except Exception as e:
            #    print("Erro na FFT:", e)


            #self.send_response(200)
            #self.end_headers()
            #self.wfile.write(b"OK")
        else:
            self.send_error(404, "Caminho nao encontrado")

def run_server():
    server = HTTPServer((HOST, PORT), MyHandler)
    print(f"Servidor HTTP rodando em http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando servidor.")
        server.server_close()

if __name__ == "__main__":
    run_server()
