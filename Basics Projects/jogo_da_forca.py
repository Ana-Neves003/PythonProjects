import random

def escolher_palavra():
    palavras = ['python', 'desenvolvimento', 'programacao', 'tecnologia', 'computador']
    return random.choice(palavras)

def exibir_palavra(palavra, letras_corretas):
    return ' '.join([letra if letra in letras_corretas else '_' for letra in palavra])

palavra = escolher_palavra()
letras_corretas = []
tentativas = 6

print("Bem-vindo ao Jogo da Forca!")
print(exibir_palavra(palavra, letras_corretas))

while tentativas > 0 and set(letras_corretas) != set(palavra):
    palpite = input("\nDigite uma letra: ").lower()

    if palpite in palavra:
        letras_corretas.append(palpite)
    else:
        tentativas -= 1
        print(f"Letra incorreta! Você tem {tentativas} tentativas restantes.")

    print(exibir_palavra(palavra, letras_corretas))

if set(letras_corretas) == set(palavra):
    print("Parabéns, você ganhou!")
else:
    print(f"Você perdeu! A palavra era '{palavra}'.")
