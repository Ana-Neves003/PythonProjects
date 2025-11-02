from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import json
import numpy as np
from scipy.fft import fft
import time

HOST = "0.0.0.0"
PORT = 8000
buffer_dados = b""
freq_atual = []
mag_atual = []


HTTPServer.last_fft = ([], [])

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
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
            global freq_atual, mag_atual
            freq = np.array(freq_atual)
            spec = np.array(mag_atual)
            print(f"[DEBUG] Chamado /dados_fft - freq_atual: {None if freq_atual is None else len(freq_atual)}, mag_atual: {None if mag_atual is None else len(mag_atual)}")

            # --- Retorna FFT atual ---
            #if freq_atual is None or mag_atual is None:
            #    data = {"freq": [], "spec": []}
            #else:
            #    freq = np.array(freq_atual)
            #    spec = np.array(mag_atual)
            #    print(f"[DEBUG] Chamado /dados_fft - freq_atual: {len(freq)}, mag_atual: {len(spec)}")

            #    data = {
            #        "freq": freq.tolist(),
            #        "spec": spec.tolist(),
            #    }


            data = {
                "freq": freq.tolist(),
                "spec": spec.tolist(),
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")            
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())

        else:
            self.send_error(404, "Caminho nao encontrado")

    def do_POST(self):
        global buffer_dados, freq_atual, mag_atual

        if self.path == "/upload":
            MIN_AMOSTRAS = 131072 # 65536 mínimo para FFT
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            #print(f"Recebido {len(data)} bytes de dados.")

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

                    # FFT
                    Nfft = len(sinal_pdm)
                    fs = 5_000_000  # Hz (ajuste conforme sua taxa real)
                    #spec = fft(sinal_pdm)
                    #spec = spec[:Nfft // 2 + 1]

                    # Aplica janela Hann para equivalência ao MATLAB
                    janela = np.hanning(Nfft)
                    sinal_janelado = sinal_pdm * janela

                    #spec = np.fft.rfft(sinal_pdm)

                    # FFT unilateral
                    spec = np.fft.rfft(sinal_janelado)
                    
                    #spec = np.abs(spec[:N // 2])  # metade positiva
                    #psd_spec = (np.abs(spec) ** 2) * (fs * Nfft)
                    psd_spec = (np.abs(spec) ** 2) * (1 / (fs * Nfft))
                    psd_spec[1:-1] *= 2
                    freq = np.linspace(0, fs / 2, len(psd_spec))
                    mag_dB = 10 * np.log10(psd_spec + 1e-20)# em dB

                    # Atualiza as variáveis globais para o /dados
                    freq_atual = freq
                    #mag_atual = psd_spec
                    #mag_atual = 20 * np.log10(psd_spec + 1e-12)  
                    mag_atual = mag_dB  

                    # Limpa buffer após processar (ou use janela deslizante)
                    buffer_dados = b""

                    print(f"FFT atualizada com {Nfft} amostras")

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
