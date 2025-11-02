import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft

import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

# === PARÂMETROS DO CIC ===
fs = 5_000_000    # Frequência de amostragem original (Hz)
N = 4             # Número de estágios do CIC
R = 16            # Fator de decimação
M = 1             # Atraso do comb

# === PARÂMETROS DO FIR ===
fc = 110e3        # Frequência de corte
fir_coeffs = np.array([
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
    -0.000442986869603646, 0.000792054770933056
])

# === Função CIC ===
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

# === Função FIR ===
def fir_filter(signal, coefficients):
    y = np.zeros_like(signal, dtype=np.float64)
    for n in range(len(signal)):
        for k in range(len(coefficients)):
            if n - k >= 0:
                y[n] += coefficients[k] * signal[n - k]
    return y

# === Leitura e conversão do sinal PDM ===
#filename = 'sinais/dados_recebidos_10s.RAW'
filename = 'sinais/dados_recebidos_TCP.RAW'
with open(filename, 'rb') as f:
    data = np.fromfile(f, dtype=np.uint32)

# Converte para bits (MSB primeiro, como no MATLAB)
bit_strs = [f"{val:032b}" for val in data]
bit_array = np.array([int(b) for bits in bit_strs for b in bits], dtype=np.int8)
pdm_signal = 2 * bit_array - 1  

# === Aplicar CIC ===
cic_output = cic_filter(pdm_signal, R, N, M)
fs_cic = fs / R

# === Aplicar FIR ===
fir_output = fir_filter(cic_output, fir_coeffs)

# === Cálculo das FFTs ===
def compute_psd(signal, fs):
    Nfft = len(signal)
    freq = np.linspace(0, fs/2, Nfft//2 + 1)
    spec = fft(signal)
    psd = (np.abs(spec[:len(freq)])**2) * (1/(fs*Nfft))
    psd[1:-1] *= 2
    psd[psd == 0] = 1e-20
    return freq, 10*np.log10(psd)

freq_pdm, psd_pdm = compute_psd(pdm_signal, fs)
freq_cic, psd_cic = compute_psd(cic_output, fs_cic)
freq_fir, psd_fir = compute_psd(fir_output, fs_cic)

# === Plots lado a lado ===
plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.semilogx(freq_pdm, psd_pdm, 'b')
plt.title('FFT do Sinal PDM Original')
plt.xlabel('Frequência (Hz)')
plt.ylabel('Magnitude (dB/Hz)')
plt.grid(True)

plt.subplot(1, 3, 2)
plt.semilogx(freq_cic, psd_cic, 'b')
plt.title('FFT após Filtro CIC')
plt.xlabel('Frequência (Hz)')
plt.ylabel('Magnitude (dB/Hz)')
plt.grid(True)

plt.subplot(1, 3, 3)
plt.semilogx(freq_fir, psd_fir, 'b')
plt.title('FFT após Filtro FIR')
plt.xlabel('Frequência (Hz)')
plt.ylabel('Magnitude (dB/Hz)')
plt.grid(True)


plt.tight_layout()
plt.show()
