"""
MetalTech Soluções Industriais S.A.
API RESTful de Alta Disponibilidade para Manutenção Preditiva Industrial.
Em conformidade com a Etapa 3 do Projeto Integrador e diretrizes de integração com CLPs.
"""

from pathlib import Path
from typing import Literal
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Localização e carregamento com fallback defensivo do modelo treinado
DIRETORIO_RAIZ = Path(__file__).parent
CAMINHO_MODELO = DIRETORIO_RAIZ / "models" / "modelo_random_forest.joblib"

if not CAMINHO_MODELO.exists():
    raise FileNotFoundError(f"Arquivo do modelo não encontrado: {CAMINHO_MODELO.resolve()}")

modelo = joblib.load(CAMINHO_MODELO)

# Inicialização da aplicação FastAPI
app = FastAPI(
    title="MetalTech - API de Manutenção Preditiva Industrial",
    description=(
        "Microserviço RESTful para inferência em tempo real de risco de falhas mecânicas "
        "em motobombas e redutores a partir de telemetria IoT (temperatura, vibração e pressão)."
    ),
    version="1.1.0",
    contact={
        "name": "Engenharia de Automação & Governança MetalTech",
        "email": "automacao@metaltech.ind.br",
    },
)

# Habilitar CORS para integração com dashboards industriais e SCADA Web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montagem de diretórios estáticos para visualização no dashboard
if (DIRETORIO_RAIZ / "images").exists():
    app.mount("/images", StaticFiles(directory=str(DIRETORIO_RAIZ / "images")), name="images")

if (DIRETORIO_RAIZ / "docs").exists():
    app.mount("/docs-files", StaticFiles(directory=str(DIRETORIO_RAIZ / "docs")), name="docs-files")


class DadosSensores(BaseModel):
    """
    Schema dos dados transmitidos por sensores IoT / CLPs industriais.
    Contém limites físicos de segurança operacional para validação estrita.
    """

    temperatura_c: float = Field(
        ...,
        ge=-40.0,
        le=250.0,
        description="Temperatura de mancal/carcaça em graus Celsius (-40°C a 250°C)",
        example=74.5,
    )
    vibracao_mm_s: float = Field(
        ...,
        ge=0.0,
        le=50.0,
        description="Velocidade de vibração global RMS em mm/s (0.0 a 50.0)",
        example=4.2,
    )
    pressao_bar: float = Field(
        ...,
        ge=0.0,
        le=150.0,
        description="Pressão hidráulica da linha de lubrificação em bar (0.0 a 150.0)",
        example=41.8,
    )


class RespostaPrevisao(BaseModel):
    """Schema de resposta unificada conforme especificado no Edital."""

    falha_prevista: int = Field(
        ..., description="0 para operação normal, 1 para anomalia crítica"
    )
    risco_de_falha: Literal["Sim", "Não"] = Field(
        ..., description="Resposta direta para os CLPs industriais: Sim ou Não"
    )
    probabilidade_falha_percentual: float = Field(
        ..., description="Probabilidade calculada de avaria mecânica (0 a 100%)"
    )
    severidade_alerta: Literal["NORMAL", "ALERTA_PREVENTIVO", "CRÍTICO_INTERVENÇÃO"] = Field(
        ..., description="Classificação para automação de alarmes em IHM/SCADA"
    )
    recomendacao_operacional: str = Field(
        ..., description="Ação prescritiva recomendada à equipe de manutenção"
    )


@app.get("/", tags=["Dashboard & Interface Web"])
def pagina_inicial():
    """Retorna o painel interativo da fábrica se existir, ou informações da API."""
    index_path = DIRETORIO_RAIZ / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {
        "sistema": "MetalTech Industrial IoT Gateway",
        "status": "ONLINE",
        "versao": "1.1.0",
        "modelo_ativo": "RandomForest_Classifier_v1.0",
        "endpoints": {
            "predicao": "/predict [POST]",
            "documentacao_swagger": "/docs",
            "documentacao_redoc": "/redoc",
        },
    }


@app.get("/health", tags=["Diagnóstico"])
def healthcheck():
    """Health check para orquestradores (Kubernetes, Docker Swarm ou Supervisórios)."""
    return {
        "status": "healthy",
        "modelo_carregado": modelo is not None,
        "n_classes": len(modelo.classes_) if hasattr(modelo, "classes_") else 0,
    }


@app.post(
    "/predict",
    response_model=RespostaPrevisao,
    status_code=status.HTTP_200_OK,
    tags=["Predição Industrial"],
    summary="Predição de Falha em Motores Industriais",
)
def prever_falha(dados: DadosSensores):
    """
    Processa os parâmetros de sensores IoT de uma máquina e retorna o diagnóstico preditivo.
    - Atende estritamente à especificação da Etapa 3: 'Risco de Falha: Sim/Não'.
    - Fornece suporte a CLPs (Sim/Não e 0/1) e sistemas supervisórios de gestão de ativos.
    """
    try:
        entrada = pd.DataFrame(
            [
                {
                    "temperatura_c": dados.temperatura_c,
                    "vibracao_mm_s": dados.vibracao_mm_s,
                    "pressao_bar": dados.pressao_bar,
                }
            ]
        )

        previsao = int(modelo.predict(entrada)[0])
        probabilidades = modelo.predict_proba(entrada)[0]
        indice_falha = list(modelo.classes_).index(1)
        probabilidade_falha = float(probabilidades[indice_falha])
        percentual = round(probabilidade_falha * 100, 2)

        risco_rotulo: Literal["Sim", "Não"] = "Sim" if previsao == 1 else "Não"

        if percentual >= 75.0:
            severidade = "CRÍTICO_INTERVENÇÃO"
            recomendacao = "Interromper operação imediatamente e despachar equipe técnica de emergência para o mancal."
        elif percentual >= 40.0:
            severidade = "ALERTA_PREVENTIVO"
            recomendacao = "Agendar inspeção e lubrificação preventiva na próxima janela operacional de 4 horas."
        else:
            severidade = "NORMAL"
            recomendacao = "Equipamento em parâmetros nominais de trabalho. Nenhuma ação requerida."

        return RespostaPrevisao(
            falha_prevista=previsao,
            risco_de_falha=risco_rotulo,
            probabilidade_falha_percentual=percentual,
            severidade_alerta=severidade,
            recomendacao_operacional=recomendacao,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno no processamento do modelo preditivo: {str(e)}",
        )
