class Tarefa:
    def __init__(self, descricao, prioridade):
        self.descricao = descricao
        self.prioridade = prioridade

    def __repr__(self):
        return f"{self.descricao} (Prioridade: {self.prioridade})"

class GerenciadorTarefas:
    def __init__(self):
        self.tarefas = []

    def adicionar_tarefa(self, descricao, prioridade):
        tarefa = Tarefa(descricao, prioridade)
        self.tarefas.append(tarefa)
        self.ordenar_tarefas()

    def remover_tarefa(self, descricao):
        self.tarefas = [tarefa for tarefa in self.tarefas if tarefa.descricao != descricao]
        print(f"Tarefa '{descricao}' removida com sucesso!")

    def listar_tarefas(self):
        if not self.tarefas:
            print("Nenhuma tarefa adicionada.")
        else:
            print("Tarefas ordenadas por prioridade:")
            for tarefa in self.tarefas:
                print(tarefa)

    def ordenar_tarefas(self):
        prioridades = {'alta': 1, 'media': 2, 'baixa': 3}
        self.tarefas.sort(key=lambda t: prioridades[t.prioridade])

# Interface interativa
gerenciador = GerenciadorTarefas()

def exibir_menu():
    print("\n--- Gerenciador de Tarefas ---")
    print("1. Adicionar Tarefa")
    print("2. Remover Tarefa")
    print("3. Listar Tarefas")
    print("4. Sair")

while True:
    exibir_menu()
    escolha = input("Escolha uma opção: ")

    if escolha == '1':
        descricao = input("Digite a descrição da tarefa: ")
        prioridade = input("Digite a prioridade (alta/media/baixa): ").lower()
        if prioridade in ['alta', 'media', 'baixa']:
            gerenciador.adicionar_tarefa(descricao, prioridade)
            print(f"Tarefa '{descricao}' com prioridade {prioridade} adicionada.")
        else:
            print("Prioridade inválida! Use 'alta', 'media' ou 'baixa'.")
    elif escolha == '2':
        descricao = input("Digite a descrição da tarefa a ser removida: ")
        gerenciador.remover_tarefa(descricao)
    elif escolha == '3':
        gerenciador.listar_tarefas()
    elif escolha == '4':
        print("Saindo do gerenciador de tarefas...")
        break
    else:
        print("Opção inválida! Tente novamente.")
