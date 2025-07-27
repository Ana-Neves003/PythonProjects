import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft

filename = 'sinais/dados_recebidos_sinais.RAW'

# Lê os dados como uint32
with open(filename, 'rb') as f:
    data = np.fromfile(f, dtype=np.uint32)

# Converte cada uint32 para uma string binária de 32 bits, MSB-first
bit_strs = [f"{val:032b}" for val in data]  # lista de strings '010101...'
bit_array = np.array([int(b) for bits in bit_strs for b in bits], dtype=np.int8)

# Converte para PDM bipolar (-1 e 1)
reorganized_data = 2 * bit_array - 1
Nfft = len(reorganized_data)

# FFT
fs = 5_000_000  # Hz
spec = fft(reorganized_data)
spec = spec[:Nfft // 2 + 1]
freq = np.linspace(0, fs / 2, len(spec))

# PSD
psd_spec = (np.abs(spec) ** 2) * (1 / (fs * Nfft))
psd_spec[1:-1] *= 2

# Plot
plt.figure(figsize=(10, 5))
plt.semilogx(freq, 10 * np.log10(psd_spec), 'r')
plt.grid(True)
plt.title("Espectro do Sinal PDM")
plt.xlabel("Frequência (Hz)")
plt.ylabel("Magnitude (dB/Hz)")
plt.tight_layout()
plt.show()
