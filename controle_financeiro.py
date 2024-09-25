import json
from datetime import datetime

class ControleFinanceiro:
    def __init__(self, arquivo='financas.json'):
        self.arquivo = arquivo
        self.financas = self.carregar_dados()

    def carregar_dados(self):
        try:
            with open(self.arquivo, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"receitas": [], "despesas": []}

    def salvar_dados(self):
        with open(self.arquivo, 'w') as f:
            json.dump(self.financas, f)

    def adicionar_receita(self, valor, descricao):
        self.financas["receitas"].append({"data": str(datetime.now()), "valor": valor, "descricao": descricao})
        self.salvar_dados()

    def adicionar_despesa(self, valor, descricao):
        self.financas["despesas"].append({"data": str(datetime.now()), "valor": valor, "descricao": descricao})
        self.salvar_dados()

    def calcular_saldo(self):
        total_receitas = sum(item['valor'] for item in self.financas['receitas'])
        total_despesas = sum(item['valor'] for item in self.financas['despesas'])
        return total_receitas - total_despesas

    def gerar_relatorio(self):
        print("\n--- Relatório Financeiro ---")
        print(f"Saldo Total: {self.calcular_saldo():.2f}\n")
        print("Receitas:")
        for r in self.financas['receitas']:
            print(f"Data: {r['data']}, Valor: {r['valor']}, Descrição: {r['descricao']}")
        print("\nDespesas:")
        for d in self.financas['despesas']:
            print(f"Data: {d['data']}, Valor: {d['valor']}, Descrição: {d['descricao']}")

# Interface interativa
controle = ControleFinanceiro()

while True:
    print("\n--- Controle Financeiro Pessoal ---")
    print("1. Adicionar Receita")
    print("2. Adicionar Despesa")
    print("3. Gerar Relatório")
    print("4. Sair")

    escolha = input("Escolha uma opção: ")

    if escolha == '1':
        valor = float(input("Digite o valor da receita: "))
        descricao = input("Digite a descrição da receita: ")
        controle.adicionar_receita(valor, descricao)
        print("Receita adicionada com sucesso.")
    elif escolha == '2':
        valor = float(input("Digite o valor da despesa: "))
        descricao = input("Digite a descrição da despesa: ")
        controle.adicionar_despesa(valor, descricao)
        print("Despesa adicionada com sucesso.")
    elif escolha == '3':
        controle.gerar_relatorio()
    elif escolha == '4':
        break
    else:
        print("Opção inválida! Tente novamente.")
