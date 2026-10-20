
import cv2
import pygame
import random

from IVC import processar_imagem


# --------------------------------------------------
# 1. Inicializacao do jogo
# --------------------------------------------------

pygame.init()

LARGURA = 800
ALTURA = 500
FPS = 60

ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pong - Projeto IVC")

relogio = pygame.time.Clock()

# Cores RGB
PRETO = (15, 15, 20)
BRANCO = (240, 240, 240)
AZUL = (50, 150, 255)
CINZENTO = (100, 100, 110)

fonte = pygame.font.SysFont("Arial", 32)
fonte_pequena = pygame.font.SysFont("Arial", 18)


# --------------------------------------------------
# 2. Configuracao das raquetes
# --------------------------------------------------

LARGURA_RAQUETE = 12
ALTURA_RAQUETE = 90
VELOCIDADE_RAQUETE = 7

raquete_jogador = pygame.Rect(
    30,
    ALTURA // 2 - ALTURA_RAQUETE // 2,
    LARGURA_RAQUETE,
    ALTURA_RAQUETE
)

raquete_computador = pygame.Rect(
    LARGURA - 30 - LARGURA_RAQUETE,
    ALTURA // 2 - ALTURA_RAQUETE // 2,
    LARGURA_RAQUETE,
    ALTURA_RAQUETE
)


# --------------------------------------------------
# 3. Configuracao da bola
# --------------------------------------------------

TAMANHO_BOLA = 14
VELOCIDADE_BOLA_X = 5
VELOCIDADE_BOLA_Y = 4

bola = pygame.Rect(
    LARGURA // 2 - TAMANHO_BOLA // 2,
    ALTURA // 2 - TAMANHO_BOLA // 2,
    TAMANHO_BOLA,
    TAMANHO_BOLA
)

velocidade_x = random.choice([-VELOCIDADE_BOLA_X,
                               VELOCIDADE_BOLA_X])
velocidade_y = random.choice([-VELOCIDADE_BOLA_Y,
                               VELOCIDADE_BOLA_Y])


def reiniciar_bola(direcao):
    """Coloca a bola no centro e define uma nova direcao."""

    global velocidade_x, velocidade_y

    bola.center = (LARGURA // 2, ALTURA // 2)

    velocidade_x = VELOCIDADE_BOLA_X * direcao
    velocidade_y = random.choice([-4, -3, 3, 4])


# --------------------------------------------------
# 4. Pontuacao
# --------------------------------------------------

pontos_jogador = 0
pontos_computador = 0


# --------------------------------------------------
# 5. Inicializacao da camara
# --------------------------------------------------

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERRO: Nao foi possivel abrir a camara.")
    print("Verifica se a camara esta ligada e disponivel.")
    pygame.quit()
    raise SystemExit


# --------------------------------------------------
# 6. Ciclo principal
# --------------------------------------------------

a_correr = True

try:
    while a_correr:

        relogio.tick(FPS)

        # ------------------------------------------
        # Eventos
        # ------------------------------------------

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                a_correr = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    a_correr = False

        # ------------------------------------------
        # FASE 1: Segmentacao por cor
        # ------------------------------------------

        sucesso, frame = camera.read()

        centro_y = None

        if sucesso:
            # Espelhar a imagem para tornar os movimentos
            # mais naturais para o jogador.
            frame = cv2.flip(frame, 1)

            centro_y = processar_imagem(frame)

        # ------------------------------------------
        # Controlo da raquete do jogador
        # ------------------------------------------

        teclas = pygame.key.get_pressed()

        if centro_y is not None and sucesso:
            # Converter a coordenada vertical da camara
            # para a coordenada vertical do jogo.
            altura_imagem = frame.shape[0]

            posicao_y = int(
                centro_y * ALTURA / altura_imagem
            )

            raquete_jogador.centery = posicao_y

        else:
            # Controlo alternativo pelo teclado.
            if teclas[pygame.K_UP]:
                raquete_jogador.y -= VELOCIDADE_RAQUETE

            if teclas[pygame.K_DOWN]:
                raquete_jogador.y += VELOCIDADE_RAQUETE

        # Impedir que a raquete saia do ecra.
        if raquete_jogador.top < 0:
            raquete_jogador.top = 0

        if raquete_jogador.bottom > ALTURA:
            raquete_jogador.bottom = ALTURA

        # ------------------------------------------
        # Controlo automatico do computador
        # ------------------------------------------

        if raquete_computador.centery < bola.centery - 10:
            raquete_computador.y += 5

        elif raquete_computador.centery > bola.centery + 10:
            raquete_computador.y -= 5

        if raquete_computador.top < 0:
            raquete_computador.top = 0

        if raquete_computador.bottom > ALTURA:
            raquete_computador.bottom = ALTURA

        # ------------------------------------------
        # Movimento da bola
        # ------------------------------------------

        bola.x += velocidade_x
        bola.y += velocidade_y

        # Colisao com as paredes superior e inferior.
        if bola.top <= 0:
            bola.top = 0
            velocidade_y = abs(velocidade_y)

        elif bola.bottom >= ALTURA:
            bola.bottom = ALTURA
            velocidade_y = -abs(velocidade_y)

        # ------------------------------------------
        # Colisao com as raquetes
        # ------------------------------------------

        if bola.colliderect(raquete_jogador) and velocidade_x < 0:
            bola.left = raquete_jogador.right
            velocidade_x = abs(velocidade_x)

            # A posicao do impacto altera o angulo.
            desvio = (
                bola.centery - raquete_jogador.centery
            ) / (ALTURA_RAQUETE / 2)

            velocidade_y = int(desvio * 5)

            if velocidade_y == 0:
                velocidade_y = random.choice([-2, 2])

        if bola.colliderect(raquete_computador) and velocidade_x > 0:
            bola.right = raquete_computador.left
            velocidade_x = -abs(velocidade_x)

            desvio = (
                bola.centery - raquete_computador.centery
            ) / (ALTURA_RAQUETE / 2)

            velocidade_y = int(desvio * 5)

            if velocidade_y == 0:
                velocidade_y = random.choice([-2, 2])

        # ------------------------------------------
        # Pontuacao
        # ------------------------------------------

        if bola.right < 0:
            pontos_computador += 1
            reiniciar_bola(1)

        elif bola.left > LARGURA:
            pontos_jogador += 1
            reiniciar_bola(-1)

        # ------------------------------------------
        # Desenhar o jogo
        # ------------------------------------------

        ecra.fill(PRETO)

        # Linha central.
        for y in range(0, ALTURA, 25):
            pygame.draw.rect(
                ecra,
                CINZENTO,
                (LARGURA // 2 - 1, y, 2, 12)
            )

        # Raquetes e bola.
        pygame.draw.rect(
            ecra, AZUL, raquete_jogador
        )

        pygame.draw.rect(
            ecra, BRANCO, raquete_computador
        )

        pygame.draw.ellipse(
            ecra, BRANCO, bola
        )

        # Pontuacao.
        texto_jogador = fonte.render(
            str(pontos_jogador), True, BRANCO
        )

        texto_computador = fonte.render(
            str(pontos_computador), True, BRANCO
        )

        ecra.blit(
            texto_jogador,
            (LARGURA // 2 - 70, 20)
        )

        ecra.blit(
            texto_computador,
            (LARGURA // 2 + 45, 20)
        )

        # Indicacao do metodo de controlo.
        if centro_y is not None:
            estado = "Segmentacao: objecto azul detectado"
            cor_estado = (50, 220, 100)
        else:
            estado = "Sem deteccao: usa as setas CIMA/BAIXO"
            cor_estado = (255, 190, 60)

        texto_estado = fonte_pequena.render(
            estado, True, cor_estado
        )

        ecra.blit(texto_estado, (15, ALTURA - 25))

        pygame.display.flip()

finally:
    # Libertar recursos mesmo que ocorra um erro.
    camera.release()
    cv2.destroyAllWindows()
    pygame.quit()
