"""
MetalTech Soluções Industriais S.A.
Módulo de Inspeção de Qualidade Óptica e Geométrica via Visão Computacional (OpenCV)
Atende aos requisitos da Etapa 3 do Projeto Integrador Fábrica Inteligente.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import cv2
import numpy as np


@dataclass
class ResultadoInspecao:
    arquivo: str
    status: str  # "APROVADO" ou "REPROVADO"
    motivo: str
    num_contornos_externos: int
    area_principal: float
    circularidade: float
    anomalias_detectadas: List[str]


class InspetorQualidadeVisual:
    """
    Inspetor óptico baseado em processamento digital de imagem:
    1. Conversão em escala de cinza
    2. Suavização Gaussiana (filtro passa-baixas 5x5)
    3. Detecção de Bordas Canny (histerese 50/150)
    4. Análise Geométrica de Contornos (Área nominal e Circularidade ISO)
    5. Análise Espectral HSV para Detecção de Oxidação / Corrosão
    """

    def __init__(
        self,
        area_esperada_min: float = 28000.0,
        area_esperada_max: float = 34000.0,
        circularidade_min: float = 0.85,
        limiar_canny_baixo: int = 50,
        limiar_canny_alto: int = 150,
    ):
        self.area_min = area_esperada_min
        self.area_max = area_esperada_max
        self.circularidade_min = circularidade_min
        self.canny_baixo = limiar_canny_baixo
        self.canny_alto = limiar_canny_alto

    def inspecionar(self, caminho_imagem: str | Path) -> Tuple[ResultadoInspecao, np.ndarray]:
        caminho = Path(caminho_imagem)
        if not caminho.exists():
            raise FileNotFoundError(f"Arquivo não localizado: {caminho.resolve()}")

        imagem_bgr = cv2.imread(str(caminho))
        if imagem_bgr is None:
            raise ValueError(f"Formato de imagem inválido ou ilegível: {caminho}")

        # 1. Pré-processamento
        imagem_cinza = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2GRAY)
        imagem_blur = cv2.GaussianBlur(imagem_cinza, (5, 5), 0)

        # 2. Detecção de bordas via Canny
        bordas = cv2.Canny(imagem_blur, self.canny_baixo, self.canny_alto)

        # 3. Análise de Contornos Externos
        contornos_ext, _ = cv2.findContours(
            bordas.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        anomalias: List[str] = []
        imagem_anotada = imagem_bgr.copy()

        # Filtrar contornos significativos
        contornos_relevantes = [c for c in contornos_ext if cv2.contourArea(c) >= 50]

        if not contornos_relevantes:
            return ResultadoInspecao(
                arquivo=caminho.name,
                status="REPROVADO",
                motivo="Nenhum contorno de peça localizado.",
                num_contornos_externos=0,
                area_principal=0.0,
                circularidade=0.0,
                anomalias_detectadas=["Geometria não detectada"],
            ), imagem_anotada

        # Maior contorno (corpo principal da peça)
        contorno_principal = max(contornos_relevantes, key=cv2.contourArea)
        area = cv2.contourArea(contorno_principal)
        perimetro = cv2.arcLength(contorno_principal, True)

        # Circularidade: 4 * pi * Area / (Perimetro^2) -> 1.0 para círculo perfeito
        circularidade = (4 * np.pi * area) / (perimetro**2) if perimetro > 0 else 0.0

        # Verificação 1: Quebra de integridade de perímetro externo / trincas
        if len(contornos_relevantes) > 2 or area < self.area_min:
            anomalias.append(
                f"Trinca ou fratura estrutural detectada (perímetro rompido em {len(contornos_relevantes)} seções, área útil {area:.0f} px²)"
            )
        elif area > self.area_max:
            anomalias.append(f"Dimensões acima da tolerância nominal ({area:.0f} px²)")

        # Verificação 2: Circularidade
        if circularidade < self.circularidade_min:
            anomalias.append(
                f"Distorção geométrica/ovalização ({circularidade:.2f} < {self.circularidade_min:.2f})"
            )

        # Verificação 3: Análise de corrosão / oxidação (espaço de cores HSV)
        imagem_hsv = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2HSV)
        mascara_ferrugem = cv2.inRange(
            imagem_hsv, np.array([5, 40, 40]), np.array([25, 255, 200])
        )
        pixels_corrosao = int(cv2.countNonZero(mascara_ferrugem))
        if pixels_corrosao > 100:
            anomalias.append(
                f"Oxidação superficial severa/ferrugem ({pixels_corrosao} pixels afetados)"
            )

        # Classificação
        aprovado = len(anomalias) == 0
        status = "APROVADO" if aprovado else "REPROVADO"
        motivo = (
            "Geometria nominal e superfície íntegra dentro das tolerâncias."
            if aprovado
            else "; ".join(anomalias)
        )

        cor_status = (0, 180, 0) if aprovado else (0, 0, 220)
        cv2.drawContours(imagem_anotada, contornos_relevantes, -1, cor_status, 2)
        cv2.putText(
            imagem_anotada,
            f"{status} | Area:{int(area)} px",
            (15, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            cor_status,
            2,
        )

        return ResultadoInspecao(
            arquivo=caminho.name,
            status=status,
            motivo=motivo,
            num_contornos_externos=len(contornos_relevantes),
            area_principal=round(area, 2),
            circularidade=round(circularidade, 3),
            anomalias_detectadas=anomalias,
        ), imagem_anotada


if __name__ == "__main__":
    inspetor = InspetorQualidadeVisual()
    pasta_imagens = Path("images")
    pasta_saida = Path("images/inspecoes")
    pasta_saida.mkdir(exist_ok=True, parents=True)

    print("=" * 70)
    print("METALTECH INDUSTRIAL S.A. - SISTEMA DE INSPEÇÃO COMPUTACIONAL")
    print("=" * 70)

    for img_path in sorted(pasta_imagens.glob("*.jpg")):
        if "inspecoes" in str(img_path):
            continue
        resultado, img_anotada = inspetor.inspecionar(img_path)
        cv2.imwrite(str(pasta_saida / f"resultado_{img_path.name}"), img_anotada)
        print(f"\n[PEÇA]: {resultado.arquivo}")
        print(f" -> STATUS FINAL: {resultado.status}")
        print(f" -> Área Contorno Principal: {resultado.area_principal} px²")
        print(f" -> Circularidade: {resultado.circularidade}")
        print(f" -> Diagnóstico: {resultado.motivo}")
