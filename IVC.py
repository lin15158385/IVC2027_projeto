
import cv2
import numpy as np


def processar_imagem(frame):
    """
    Segmenta um objecto azul e calcula a sua posição vertical.

    Retorna:
        centro_y: posição vertical do objecto, ou None
                  se não for detectado.
        imagem_resultado: imagem com a visualização da detecção.
    """

    # Converter a imagem de BGR para HSV.
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Intervalo inicial para detectar a cor azul.
    azul_inferior = np.array([90, 80, 50])
    azul_superior = np.array([135, 255, 255])

    # Criar uma máscara: branco = azul detectado.
    mascara = cv2.inRange(
        hsv,
        azul_inferior,
        azul_superior
    )

    # Reduzir pequenos ruídos na máscara.
    kernel = np.ones((5, 5), np.uint8)

    mascara = cv2.morphologyEx(
        mascara,
        cv2.MORPH_OPEN,
        kernel
    )

    mascara = cv2.morphologyEx(
        mascara,
        cv2.MORPH_CLOSE,
        kernel
    )

    # Encontrar os contornos dos objectos detectados.
    contornos, _ = cv2.findContours(
        mascara,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    centro_y = None

    # Criar uma cópia para visualizar os resultados.
    resultado = frame.copy()

    if contornos:
        # Escolher o maior contorno.
        maior_contorno = max(
            contornos,
            key=cv2.contourArea
        )

        area = cv2.contourArea(maior_contorno)

        # Ignorar pequenos objectos e ruído.
        if area > 300:
            x, y, w, h = cv2.boundingRect(maior_contorno)

            # Centro vertical do objecto.
            centro_y = y + h // 2

            # Desenhar o contorno e o centro detectado.
            cv2.rectangle(
                resultado,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            cv2.circle(
                resultado,
                (x + w // 2, centro_y),
                6,
                (0, 0, 255),
                -1
            )

            cv2.putText(
                resultado,
                f"Centro Y: {centro_y}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

    # Mostrar também a máscara de segmentação.
    cv2.imshow("Mascara - Segmentacao Azul", mascara)
    cv2.imshow("IVC - Deteccao", resultado)

    return centro_y
