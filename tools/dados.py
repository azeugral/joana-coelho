# -*- coding: utf-8 -*-
"""Pecas do portfolio. arq = numero do post em _ref/ig; cat = filtro; leg = legenda (palavras dela quando existem)."""
CATS = [('todas', 'Todas'), ('botanico', 'Botânico'), ('ornamental', 'Ornamental'), ('animais', 'Animais'), ('retratos', 'Retratos'), ('escrita', 'Escrita'), ('projetos', 'Projetos')]
P = [
    (201, 'ornamental', 'Coluna ornamental com lótus e lua'),
    (81, 'botanico', 'Lírios sobre cicatrizes, borboleta sobre a pele'),
    (335, 'animais', 'Girafa em linha fina'),
    (64, 'retratos', 'O rosto da fé gravado na pele'),
    (320, 'ornamental', 'Borboleta e símbolos ao longo da coluna'),
    (40, 'projetos', 'A primeira sleeve do Carlos, cicatrizada há cerca de 3 anos'),
    (353, 'botanico', 'Rosas com folhas, em traço fino'),
    (12, 'animais', 'O Floco, um gatinho especial do Luxemburgo'),
    (61, 'escrita', 'Lettering em toda a perna'),
    (219, 'ornamental', 'Rosas e mandala no ombro'),
    (403, 'animais', 'Com a dor vem a força'),
    (72, 'projetos', 'Braço fechado com arquitetura e figuras'),
    (299, 'botanico', 'Girassol, folhas e borboleta'),
    (130, 'retratos', 'Retrato em linha'),
    (7, 'animais', 'Fénix'),
    (11, 'ornamental', 'Cada detalhe, desenhado ao pormenor'),
    (207, 'escrita', 'Desde sempre… para sempre'),
    (135, 'projetos', 'Projeto de braço com símbolos'),
    (50, 'botanico', 'Lírios nas costas'),
    (29, 'retratos', 'Entre arte e anatomia: razão e emoção'),
    (314, 'animais', 'Tartaruga'),
    (110, 'ornamental', 'As fases da lua ao longo do tronco'),
    (304, 'projetos', 'Família: um braço cheio de histórias'),
    (151, 'botanico', 'Cada um tem o seu tempo de florescer'),
    (52, 'animais', 'Até nos reencontrarmos'),
    (221, 'retratos', 'Retrato feminino com flores'),
    (310, 'escrita', 'Frase com tigre'),
    (9, 'projetos', 'Antebraço com olho e natureza'),
    (203, 'botanico', 'Ramo floral nas costas'),
    (143, 'animais', 'Pantera ao longo da coluna'),
    (430, 'retratos', 'Família em traço contínuo'),
    (125, 'botanico', 'Flores no antebraço'),
    (439, 'animais', 'Libélula'),
    (360, 'botanico', 'Braço floral'),
    (445, 'animais', 'Pena'),
    (371, 'projetos', 'Braço floral completo'),
    (323, 'animais', 'Borboleta e folhas no peito'),
    (348, 'animais', 'Lobo em linha fina'),
]

# fotos com cor real que ficam melhores em P&B na grade
SEMPRE_PB = set()

# ritmo da grade: cor e P&B em xadrez, a partir das fotos que tem cor real
COR = {81, 64, 40, 12, 61, 11, 130, 50, 110, 52, 9, 143, 430, 439}
_c = [p for p in P if p[0] in COR]; _m = [p for p in P if p[0] not in COR]; P = []
while _c or _m:
    i = len(P); quer_cor = (i % 4 + i // 4) % 2 == 0
    P.append((_c if (quer_cor and _c) or not _m else _m).pop(0))
