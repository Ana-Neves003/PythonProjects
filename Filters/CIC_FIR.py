import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf

# LER O ARQUIVO DE ÁUDIO PDM (.WAV)
filename = 'REC_5kHz_4.WAV'

try:
    # Lê os dados e a taxa de amostragem usando soundfile
    data, fs = sf.read(filename, dtype='int32')
    print(f"Arquivo {filename} lido com sucesso!")
    print(f"Taxa de amostragem: {fs} Hz, Formato dos dados: {data.dtype}, Tamanho: {data.shape}")
except Exception as e:
    print(f"Erro ao processar o arquivo WAV: {e}")
    exit()

# PROCESSAR O SINAL LIDO
Nfft = len(data)
data = data[Nfft // 2:]  # Usa metade dos dados
binary_data = np.unpackbits(data.view(np.uint8))  # Converte para binário
binary_data = binary_data[:len(binary_data) // 32 * 32]  # Ajustar tamanho
binary_data = binary_data.reshape(-1, 32)[:, ::-1].flatten()  # Rearranjar bits
reorganized_data = 2 * binary_data - 1
Nfft = len(reorganized_data)

# PARÂMETROS DO FILTRO CIC E FIR
fs = 5e6  # Frequência de amostragem
fc = 110e3  # Frequência de corte do FIR
order = 64  # Ordem do FIR
N = 4  # Número de estágios do CIC
R = 16  # Taxa de decimação do CIC
M = 1  # Atraso diferencial do CIC

# FILTRO CIC
def cic_filter(x, R, N):
    # Garantir precisão usando float64 durante cálculos
    integrator = x.astype(np.float64)
    for _ in range(N):  # Etapas de integração
        for i in range(1, len(integrator)):
            integrator[i] = integrator[i - 1] + integrator[i]
    decimated = integrator[::R]  # Decimação
    y = decimated
    for _ in range(N):  # Etapas de diferenciação
        comb = np.zeros_like(y)
        for i in range(R, len(y)):
            comb[i] = y[i] - y[i - R]
        y = comb
    return y.astype(np.int64)  # Retornar para formato inteiro no final

cic_processed = cic_filter(reorganized_data, R, N)
fs_cic = fs / R

# FILTRO FIR
coeficientes_fir = [  # Mesmos coeficientes fornecidos no código original
    0.000792054770933056, -0.000442986869603646, -0.000346715840607441, 
    0.00105672404464702, -0.00102725323675075, -3.97609216037946e-05, 
    0.00157304669437729, -0.00223131365400529, 0.000913291906289769, 
    0.00194681182232756, -0.00410916320834437, 0.00307212378248671, 
    0.00143941527024877, -0.00629432948118691, 0.00682235964803528, 
    -0.000929276275685085, -0.00791664441517844, 0.0121861344621779, 
    -0.00625357547552810, -0.00757308458012768, 0.0187253171630382, 
    -0.0157626522477365, -0.00317130531504444, 0.0255797271575543, 
    -0.0314843244086080, 0.00912596811664657, 0.0316404965881606, 
    -0.0600365491481145, 0.0419241430420708, 0.0358143540096918, 
    -0.151082412771185, 0.254374980329710, 0.703428798081828, 
    0.254374980329710, -0.151082412771185, 0.0358143540096918, 
    0.0419241430420708, -0.0600365491481145, 0.0316404965881606, 
    0.00912596811664657, -0.0314843244086080, 0.0255797271575543, 
    -0.00317130531504444, -0.0157626522477365, 0.0187253171630382, 
    -0.00757308458012768, -0.00625357547552810, 0.0121861344621779, 
    -0.00791664441517844, -0.000929276275685085, 0.00682235964803528, 
    -0.00629432948118691, 0.00143941527024877, 0.00307212378248671, 
    -0.00410916320834437, 0.00194681182232756, 0.000913291906289769, 
    -0.00223131365400529, 0.00157304669437729, -3.97609216037946e-05, 
    -0.00102725323675075, 0.00105672404464702, -0.000346715840607441, 
    -0.000442986869603646, 0.000792054770933056]

def my_filter_FIR(b, x):
    y = np.zeros_like(x, dtype=np.float64)
    for n in range(len(x)):
        for k in range(len(b)):
            if n - k >= 0:
                y[n] += b[k] * x[n - k]
    return y

fir_processed = my_filter_FIR(coeficientes_fir, cic_processed)

# Espectros
Nfft_filter = len(cic_processed)
freq = np.linspace(0, fs / 2, Nfft // 2 + 1)
freq_filter = np.linspace(0, fs_cic / 2, Nfft_filter // 2 + 1)

spec = np.fft.fft(reorganized_data, Nfft)[:Nfft // 2 + 1]
psd_spec = np.abs(spec) ** 2 / (fs * Nfft)

spec_cic = np.fft.fft(cic_processed, Nfft_filter)[:Nfft_filter // 2 + 1]
psd_cic = np.abs(spec_cic) ** 2 / (fs_cic * Nfft_filter)

spec_fir = np.fft.fft(fir_processed, Nfft_filter)[:Nfft_filter // 2 + 1]
psd_fir = np.abs(spec_fir) ** 2 / (fs_cic * Nfft_filter)

# VISUALIZAÇÃO
plt.figure(figsize=(12, 8))
plt.subplot(2, 2, 1)
plt.semilogx(freq, 10 * np.log10(psd_spec))
plt.grid(True)
plt.title('Espectro do Sinal Original')
plt.xlabel('Frequência (Hz)')
plt.ylabel('Potência (dB/Hz)')

plt.subplot(2, 2, 2)
plt.semilogx(freq_filter, 10 * np.log10(psd_cic))
plt.grid(True)
plt.title('Espectro após o Filtro CIC')
plt.xlabel('Frequência (Hz)')
plt.ylabel('Potência (dB/Hz)')

plt.subplot(2, 2, 3)
plt.semilogx(freq_filter, 10 * np.log10(psd_fir))
plt.grid(True)
plt.title('Espectro do Filtro CIC + FIR')
plt.xlabel('Frequência (Hz)')
plt.ylabel('Potência (dB/Hz)')

plt.tight_layout()
plt.show()
