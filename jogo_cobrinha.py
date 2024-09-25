import pygame
import time
import random

# Inicializa o Pygame
pygame.init()

# Cores
branco = (255, 255, 255)
preto = (0, 0, 0)
vermelho = (255, 0, 0)
verde = (0, 255, 0)

# Configurações da tela
largura = 600
altura = 400
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Jogo da Cobrinha")

# Tamanho da cobra e velocidade
tamanho_cobra = 10
velocidade = 15

# Fonte
fonte = pygame.font.SysFont("arial", 25)

def mostrar_pontuacao(pontuacao):
    texto = fonte.render("Pontos: " + str(pontuacao), True, preto)
    tela.blit(texto, [0, 0])

def jogo():
    game_over = False
    game_close = False

    x1 = largura / 2
    y1 = altura / 2

    x1_mudou = 0
    y1_mudou = 0

    cobra = []
    comprimento_cobra = 1

    comida_x = round(random.randrange(0, largura - tamanho_cobra) / 10.0) * 10.0
    comida_y = round(random.randrange(0, altura - tamanho_cobra) / 10.0) * 10.0

    while not game_over:

        while game_close == True:
            tela.fill(branco)
            mensagem = fonte.render("Game Over! Pressione C para jogar novamente ou Q para sair.", True, vermelho)
            tela.blit(mensagem, [largura / 6, altura / 3])
            mostrar_pontuacao(comprimento_cobra - 1)
            pygame.display.update()

            for evento in pygame.event.get():
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if evento.key == pygame.K_c:
                        jogo()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                game_over = True
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT:
                    x1_mudou = -tamanho_cobra
                    y1_mudou = 0
                elif evento.key == pygame.K_RIGHT:
                    x1_mudou = tamanho_cobra
                    y1_mudou = 0
                elif evento.key == pygame.K_UP:
                    y1_mudou = -tamanho_cobra
                    x1_mudou = 0
                elif evento.key == pygame.K_DOWN:
                    y1_mudou = tamanho_cobra
                    x1_mudou = 0

        if x1 >= largura or x1 < 0 or y1 >= altura or y1 < 0:
            game_close = True

        x1 += x1_mudou
        y1 += y1_mudou
        tela.fill(branco)
        pygame.draw.rect(tela, verde, [comida_x, comida_y, tamanho_cobra, tamanho_cobra])
        cobra_cabeca = []
        cobra_cabeca.append(x1)
        cobra_cabeca.append(y1)
        cobra.append(cobra_cabeca)
        if len(cobra) > comprimento_cobra:
            del cobra[0]

        for segmento in cobra[:-1]:
            if segmento == cobra_cabeca:
                game_close = True

        for segmento in cobra:
            pygame.draw.rect(tela, preto, [segmento[0], segmento[1], tamanho_cobra, tamanho_cobra])

        mostrar_pontuacao(comprimento_cobra - 1)

        pygame.display.update()

        if x1 == comida_x and y1 == comida_y:
            comida_x = round(random.randrange(0, largura - tamanho_cobra) / 10.0) * 10.0
            comida_y = round(random.randrange(0, altura - tamanho_cobra) / 10.0) * 10.0
            comprimento_cobra += 1

        pygame.time.Clock().tick(velocidade)

    pygame.quit()
    quit()

if __name__ == "__main__":
    jogo()
