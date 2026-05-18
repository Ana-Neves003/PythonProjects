import numpy as np
import matplotlib.pyplot as plt

# Dados iniciais
valor_casa1 = 120_000  # R$120 mil
valor_casa2 = 230_000  # R$230 mil
entrada = 23_000  # R$23 mil
juros_financiamento = 13 / 100 / 12  # 13% ao ano -> mensal
juros_poupanca = 9 / 100 / 12  # 9% ao ano -> mensal
meses = 120  # 10 anos
deposito_min = 200  # Depósito mensal mínimo
deposito_max = 1500  # Depósito mensal máximo
deposito_medio = (deposito_min + deposito_max) / 2  # Média dos depósitos

# Funções para cálculo
def calcular_parcela(valor, entrada, juros, n):
    valor_financiado = valor - entrada
    parcela = (valor_financiado * juros) / (1 - (1 + juros) ** -n)
    return parcela

def simular_poupanca(saldo_inicial, juros, deposito_mensal, n):
    saldo = saldo_inicial
    historico = []
    for _ in range(n):
        saldo = saldo * (1 + juros) + deposito_mensal
        historico.append(saldo)
    return historico

# Cálculos
parcela_casa1 = calcular_parcela(valor_casa1, entrada, juros_financiamento, meses)
parcela_casa2 = calcular_parcela(valor_casa2, entrada, juros_financiamento, meses)

# Cálculo do valor total pago
valor_final_casa1 = parcela_casa1 * meses
valor_final_casa2 = parcela_casa2 * meses

# Simulação de poupança para depósitos mínimos, médios e máximos
historico_poupanca_min = simular_poupanca(entrada, juros_poupanca, deposito_min, meses)
historico_poupanca_medio = simular_poupanca(entrada, juros_poupanca, deposito_medio, meses)
historico_poupanca_max = simular_poupanca(entrada, juros_poupanca, deposito_max, meses)

# Criação do gráfico
tempo = np.arange(1, meses + 1)

plt.figure(figsize=(10, 6))
plt.plot(tempo, historico_poupanca_min, label="Saldo Poupança (Depósito Mínimo)", color="green")
plt.plot(tempo, historico_poupanca_medio, label="Saldo Poupança (Depósito Médio)", color="orange")
plt.plot(tempo, historico_poupanca_max, label="Saldo Poupança (Depósito Máximo)", color="darkgreen")
plt.axhline(y=valor_casa1, color="blue", linestyle="--", label="Valor Casa 1")
plt.axhline(y=valor_casa2, color="red", linestyle="--", label="Valor Casa 2")
plt.title("Comparação: Poupança x Valores das Casas")
plt.xlabel("Meses")
plt.ylabel("Valor Acumulado (R$)")
plt.legend()
plt.grid()
plt.show()

# Exibição das informações
print(f"Parcela Casa 1: R${parcela_casa1:.2f}/mês")
print(f"Valor final pago pela Casa 1: R${valor_final_casa1:.2f}")
print(f"Parcela Casa 2: R${parcela_casa2:.2f}/mês")
print(f"Valor final pago pela Casa 2: R${valor_final_casa2:.2f}")

# Saldo final da poupança e diferença para os valores das casas
saldo_final_min = historico_poupanca_min[-1]
saldo_final_medio = historico_poupanca_medio[-1]
saldo_final_max = historico_poupanca_max[-1]

falta_casa1_min = max(0, valor_casa1 - saldo_final_min)
falta_casa1_medio = max(0, valor_casa1 - saldo_final_medio)
falta_casa1_max = max(0, valor_casa1 - saldo_final_max)

falta_casa2_min = max(0, valor_casa2 - saldo_final_min)
falta_casa2_medio = max(0, valor_casa2 - saldo_final_medio)
falta_casa2_max = max(0, valor_casa2 - saldo_final_max)

print(f"Saldo final da poupança após 10 anos (depósito mínimo): R${saldo_final_min:.2f}")
print(f"Saldo final da poupança após 10 anos (depósito médio): R${saldo_final_medio:.2f}")
print(f"Saldo final da poupança após 10 anos (depósito máximo): R${saldo_final_max:.2f}")

print(f"Faltando para comprar Casa 1 (depósito mínimo): R${falta_casa1_min:.2f}")
print(f"Faltando para comprar Casa 1 (depósito médio): R${falta_casa1_medio:.2f}")
print(f"Faltando para comprar Casa 1 (depósito máximo): R${falta_casa1_max:.2f}")

print(f"Faltando para comprar Casa 2 (depósito mínimo): R${falta_casa2_min:.2f}")
print(f"Faltando para comprar Casa 2 (depósito médio): R${falta_casa2_medio:.2f}")
print(f"Faltando para comprar Casa 2 (depósito máximo): R${falta_casa2_max:.2f}")

meses_casa1_min = np.argmax(np.array(historico_poupanca_min) >= valor_casa1) + 1 if falta_casa1_min == 0 else None
meses_casa1_medio = np.argmax(np.array(historico_poupanca_medio) >= valor_casa1) + 1 if falta_casa1_medio == 0 else None
meses_casa1_max = np.argmax(np.array(historico_poupanca_max) >= valor_casa1) + 1 if falta_casa1_max == 0 else None

meses_casa2_min = np.argmax(np.array(historico_poupanca_min) >= valor_casa2) + 1 if falta_casa2_min == 0 else None
meses_casa2_medio = np.argmax(np.array(historico_poupanca_medio) >= valor_casa2) + 1 if falta_casa2_medio == 0 else None
meses_casa2_max = np.argmax(np.array(historico_poupanca_max) >= valor_casa2) + 1 if falta_casa2_max == 0 else None

if meses_casa1_min:
    print(f"Casa 1 pode ser comprada em {meses_casa1_min} meses com depósito mínimo.")
if meses_casa1_medio:
    print(f"Casa 1 pode ser comprada em {meses_casa1_medio} meses com depósito médio.")
if meses_casa1_max:
    print(f"Casa 1 pode ser comprada em {meses_casa1_max} meses com depósito máximo.")

if meses_casa2_min:
    print(f"Casa 2 pode ser comprada em {meses_casa2_min} meses com depósito mínimo.")
if meses_casa2_medio:
    print(f"Casa 2 pode ser comprada em {meses_casa2_medio} meses com depósito médio.")
if meses_casa2_max:
    print(f"Casa 2 pode ser comprada em {meses_casa2_max} meses com depósito máximo.")