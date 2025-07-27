import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft

# === PARÂMETROS DO CIC ===
fs = 5_000_000    # Frequência de amostragem original (Hz)
N = 4             # Número de estágios do CIC
R = 16            # Fator de decimação
M = 1             # Atraso do comb

# === Função CIC corrigida ===
def cic_filter(signal, R, N, M=1):
    # Converter para int64 para evitar overflow
    signal = signal.astype(np.int64)
    
    # Integradores
    for _ in range(N):
        integrated = np.zeros_like(signal)
        integrated[0] = signal[0]
        for i in range(1, len(signal)):
            integrated[i] = integrated[i-1] + signal[i]
        signal = integrated

    # Decimação
    decimated = signal[::R]

    # Combs    
    for _ in range(N):
        combed = np.zeros_like(decimated)
        combed[M:] = decimated[M:] - decimated[:-M]
        decimated = combed

    return decimated[M:]

# === Leitura e conversão do sinal PDM ===
filename = 'sinais/dados_recebidos_sinais.RAW'
with open(filename, 'rb') as f:
    data = np.fromfile(f, dtype=np.uint32)

# Converte para bits (MSB primeiro, como no MATLAB)
bit_strs = [f"{val:032b}" for val in data]
bit_array = np.array([int(b) for bits in bit_strs for b in bits], dtype=np.int8)
pdm_signal = 2 * bit_array - 1  # PDM bipolar

# === FFT do sinal original (PDM) ===
Nfft_pdm = len(pdm_signal)
freq_pdm = np.linspace(0, fs / 2, Nfft_pdm // 2 + 1)
spec_pdm = fft(pdm_signal)
psd_pdm = (np.abs(spec_pdm[:len(freq_pdm)])**2) * (1 / (fs * Nfft_pdm))
psd_pdm[1:-1] *= 2

# === Aplicar CIC ===
cic_output = cic_filter(pdm_signal, R, N, M)
fs_cic = fs / R

# === FFT após CIC ===
Nfft_cic = len(cic_output)
freq_cic = np.linspace(0, fs_cic / 2, Nfft_cic // 2 + 1)
spec_cic = fft(cic_output)
psd_cic = (np.abs(spec_cic[:len(freq_cic)])**2) * (1 / (fs_cic * Nfft_cic))
psd_cic[1:-1] *= 2

psd_cic[psd_cic == 0] = 1e-20

# === Plots lado a lado ===
plt.figure(figsize=(12, 6))

# PDM original
plt.subplot(1, 2, 1)
plt.semilogx(freq_pdm, 10 * np.log10(psd_pdm), 'b')
plt.title('FFT do Sinal PDM Original')
plt.xlabel('Frequência (Hz)')
plt.ylabel('Magnitude (dB/Hz)')
plt.grid(True)

# Após CIC
plt.subplot(1, 2, 2)
plt.semilogx(freq_cic, 10 * np.log10(psd_cic), 'b')
plt.title('FFT após Filtro CIC')
plt.xlabel('Frequência (Hz)')
plt.ylabel('Magnitude (dB/Hz)')
plt.grid(True)

plt.tight_layout()
plt.show()
