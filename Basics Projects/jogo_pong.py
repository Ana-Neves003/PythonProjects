import pygame
import sys

# Inicializa o Pygame
pygame.init()

# Configurações da tela
largura = 800
altura = 600
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Pong")

# Cores
branco = (255, 255, 255)
preto = (0, 0, 0)

# Configuração da raquete
raquete_largura = 10
raquete_altura = 100
raquete1_pos = [50, (altura / 2) - (raquete_altura / 2)]
raquete2_pos = [largura - 50 - raquete_largura, (altura / 2) - (raquete_altura / 2)]
raquete_velocidade = 10

# Configuração da bola
bola_pos = [largura / 2, altura / 2]
bola_velocidade = [5, 5]
bola_diametro = 20

# Função para desenhar objetos na tela
def desenhar():
    tela.fill(preto)
    pygame.draw.rect(tela, branco, (raquete1_pos[0], raquete1_pos[1], raquete_largura, raquete_altura))
    pygame.draw.rect(tela, branco, (raquete2_pos[0], raquete2_pos[1], raquete_largura, raquete_altura))
    pygame.draw.ellipse(tela, branco, (bola_pos[0], bola_pos[1], bola_diametro, bola_diametro))
    pygame.display.flip()

# Loop principal do jogo
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Movimentação das raquetes
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and raquete1_pos[1] > 0:
        raquete1_pos[1] -= raquete_velocidade
    if keys[pygame.K_s] and raquete1_pos[1] < altura - raquete_altura:
        raquete1_pos[1] += raquete_velocidade
    if keys[pygame.K_UP] and raquete2_pos[1] > 0:
        raquete2_pos[1] -= raquete_velocidade
    if keys[pygame.K_DOWN] and raquete2_pos[1] < altura - raquete_altura:
        raquete2_pos[1] += raquete_velocidade

    # Movimentação da bola
    bola_pos[0] += bola_velocidade[0]
    bola_pos[1] += bola_velocidade[1]

    # Colisão com as paredes
    if bola_pos[1] <= 0 or bola_pos[1] >= altura - bola_diametro:
        bola_velocidade[1] = -bola_velocidade[1]

    # Colisão com as raquetes
    if (bola_pos[0] <= raquete1_pos[0] + raquete_largura and raquete1_pos[1] <= bola_pos[1] <= raquete1_pos[1] + raquete_altura) or \
       (bola_pos[0] >= raquete2_pos[0] - bola_diametro and raquete2_pos[1] <= bola_pos[1] <= raquete2_pos[1] + raquete_altura):
        bola_velocidade[0] = -bola_velocidade[0]

    # Reinicia a bola se passar pelas raquetes
    if bola_pos[0] < 0 or bola_pos[0] > largura:
        bola_pos = [largura / 2, altura / 2]
        bola_velocidade = [5, 5]

    # Desenha tudo
    desenhar()
    pygame.time.delay(30)
