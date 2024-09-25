contatos = {}

def adicionar_contato(nome, telefone):
    contatos[nome] = telefone
    print(f"Contato {nome} adicionado com sucesso!")

def visualizar_contato(nome):
    if nome in contatos:
        print(f"Nome: {nome}, Telefone: {contatos[nome]}")
    else:
        print("Contato não encontrado.")

def atualizar_contato(nome, novo_telefone):
    if nome in contatos:
        contatos[nome] = novo_telefone
        print(f"Contato {nome} atualizado com sucesso!")
    else:
        print("Contato não encontrado.")

def remover_contato(nome):
    if nome in contatos:
        del contatos[nome]
        print(f"Contato {nome} removido com sucesso!")
    else:
        print("Contato não encontrado.")

while True:
    print("\nAgenda de Contatos")
    print("1. Adicionar contato")
    print("2. Visualizar contato")
    print("3. Atualizar contato")
    print("4. Remover contato")
    print("5. Sair")
    
    escolha = input("Escolha uma opção: ")

    if escolha == '1':
        nome = input("Digite o nome: ")
        telefone = input("Digite o telefone: ")
        adicionar_contato(nome, telefone)
    elif escolha == '2':
        nome = input("Digite o nome para visualizar: ")
        visualizar_contato(nome)
    elif escolha == '3':
        nome = input("Digite o nome para atualizar: ")
        novo_telefone = input("Digite o novo telefone: ")
        atualizar_contato(nome, novo_telefone)
    elif escolha == '4':
        nome = input("Digite o nome para remover: ")
        remover_contato(nome)
    elif escolha == '5':
        break
    else:
        print("Opção inválida!")
