import random
import string

def gerar_senha(tamanho):
    caracteres = string.ascii_letters + string.digits + string.punctuation
    senha = ''.join(random.choice(caracteres) for i in range(tamanho))
    return senha

comprimento = int(input("Digite o comprimento da senha: "))
print("Senha gerada:", gerar_senha(comprimento))
