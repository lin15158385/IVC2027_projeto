import cv2
import numpy as np


def processar_imagem(frame):

    # Converter a imagem de BGR para HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Criar a janela das Trackbars apenas uma vez
    if not hasattr(processar_imagem, "inicializado"):
        cv2.namedWindow("Trackbars - Azul")

        cv2.createTrackbar("H Min", "Trackbars - Azul", 90, 179, lambda x: None)
        cv2.createTrackbar("H Max", "Trackbars - Azul", 135, 179, lambda x: None)

        cv2.createTrackbar("S Min", "Trackbars - Azul", 80, 255, lambda x: None)
        cv2.createTrackbar("S Max", "Trackbars - Azul", 255, 255, lambda x: None)

        cv2.createTrackbar("V Min", "Trackbars - Azul", 50, 255, lambda x: None)
        cv2.createTrackbar("V Max", "Trackbars - Azul", 255, 255, lambda x: None)

        processar_imagem.inicializado = True

    # Ler os valores das Trackbars
    h_min = cv2.getTrackbarPos("H Min", "Trackbars - Azul")
    h_max = cv2.getTrackbarPos("H Max", "Trackbars - Azul")

    s_min = cv2.getTrackbarPos("S Min", "Trackbars - Azul")
    s_max = cv2.getTrackbarPos("S Max", "Trackbars - Azul")

    v_min = cv2.getTrackbarPos("V Min", "Trackbars - Azul")
    v_max = cv2.getTrackbarPos("V Max", "Trackbars - Azul")

    # Definir os limites da cor azul
    azul_inferior = np.array([h_min, s_min, v_min])
    azul_superior = np.array([h_max, s_max, v_max])

    # Criar a máscara de segmentação
    mascara = cv2.inRange( #Ou threshold assim dito
        hsv,
        azul_inferior,
        azul_superior
    )

    # Reduzir o ruído
    kernel = np.ones((5, 5), np.uint8)

    # Ruido fora do obj
    mascara = cv2.morphologyEx(
        mascara,
        cv2.MORPH_OPEN,
        kernel
    )

    # Ruido dentro do obj
    mascara = cv2.morphologyEx(
        mascara,
        cv2.MORPH_CLOSE,
        kernel
    )

    # Encontrar os contornos externos
    contornos, _ = cv2.findContours(
        mascara,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    centro_y = None
    resultado = frame.copy()

    if contornos:

        # Escolher o maior contorno
        maior_contorno = max(
            contornos,
            key=cv2.contourArea
        )

        area = cv2.contourArea(maior_contorno)

        # Ignorar ruído pequeno
        if area > 300:

            # Obter o centro do objeto a partir dos momentos
            momentos = cv2.moments(maior_contorno)

            if momentos["m00"] != 0:

                centro_x = int(
                    momentos["m10"] / momentos["m00"]
                )

                centro_y = int(
                    momentos["m01"] / momentos["m00"]
                )

                # Desenhar o contorno real do objeto, sem retângulo
                cv2.drawContours(
                    resultado,
                    [maior_contorno],
                    -1,
                    (0, 255, 0),
                    2
                )

                # Marcar o centro do objeto
                cv2.circle(
                    resultado,
                    (centro_x, centro_y),
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

    # Mostrar a máscara e o resultado
    cv2.imshow("Mascara - Segmentacao Azul", mascara)
    cv2.imshow("IVC - Deteccao", resultado)

    return centro_y