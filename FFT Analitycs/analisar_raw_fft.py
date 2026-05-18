import numpy as np
import matplotlib.pyplot as plt


ARQUIVO_BRUTO = "Sinal\sinal_bruto_5k.raw"
ARQUIVO_FILTRADO = "Sinal\sinal_filtrado_5k.raw"

FS_BRUTO = 5_000_000
R = 16
FS_FILTRADO = FS_BRUTO / R


def calcular_fft(arquivo, fs):
    x = np.fromfile(arquivo, dtype=np.float32)

    print("\nArquivo:", arquivo)
    print("Amostras:", len(x))
    print("Min:", np.min(x))
    print("Max:", np.max(x))

    x = x - np.mean(x)

    fft = np.fft.rfft(x)
    freq = np.fft.rfftfreq(len(x), d=1 / fs)

    mag = np.abs(fft)
    mag = mag / np.max(mag)
    mag_db = 20 * np.log10(mag + 1e-12)

    return freq, mag_db


freq_bruto, mag_bruto = calcular_fft(ARQUIVO_BRUTO, FS_BRUTO)
freq_filtrado, mag_filtrado = calcular_fft(ARQUIVO_FILTRADO, FS_FILTRADO)


fig, axs = plt.subplots(1, 2, figsize=(10, 4))

axs[0].semilogx(freq_bruto[1:], mag_bruto[1:])
axs[0].set_title("FFT do sinal bruto")
axs[0].set_xlabel("Frequência (Hz)")
axs[0].set_ylabel("Magnitude (dB)")
axs[0].grid(True, which="both")
axs[0].set_xlim(10, FS_BRUTO / 2)
axs[0].set_ylim(-160, 0)

axs[1].semilogx(freq_filtrado[1:], mag_filtrado[1:], color="red")
axs[1].set_title("FFT do sinal filtrado")
axs[1].set_xlabel("Frequência (Hz)")
axs[1].set_ylabel("Magnitude (dB)")
axs[1].grid(True, which="both")
axs[1].set_xlim(10, FS_FILTRADO / 2)
axs[1].set_ylim(-120, 40)

plt.tight_layout()
plt.show()