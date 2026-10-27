# MetalTech - Fábrica Inteligente: Preditiva e Visão Computacional
> Solução integrada para diagnóstico preditivo de motores industriais e controle de qualidade visual de peças metálicas.

## Sobre
O sistema **MetalTech** integra telemetria de sensores industriais (temperatura, vibração e pressão) com modelos de Inteligência Artificial para antecipar falhas eletromecânicas em redutores e motobombas. Em paralelo, implementa uma esteira óptica com visão computacional para detecção de anomalias superficiais (oxidação) e defeitos dimensionais ou fraturas estruturais (trincas) em peças usinadas.

## Requisitos
- **Python:** 3.10 ou superior
- **Docker & Docker Compose** (opcional, para execução isolada em container)
- Bibliotecas principais: `fastapi`, `uvicorn`, `scikit-learn`, `joblib`, `opencv-python`, `pandas`

## Instalação
Clone o repositório e configure o ambiente virtual:

```bash
# 1. Clonar o repositório
git clone https://github.com/metaltech/fabrica-inteligente.git
cd fabrica-inteligente

# 2. Criar e ativar o ambiente virtual
python -m venv .venv
# No Windows:
.venv\Scripts\activate
# No Linux/macOS:
source .venv/bin/activate

# 3. Instalar as dependências do projeto
pip install -r requirements.txt
```

## Uso
### 1. Iniciar a API e o Painel Web (FastAPI)
Execute a partir do diretório raiz:

```bash
python -m uvicorn app:app --reload --port 8000
```

Acesse:
- **Painel de Operações:** [http://localhost:8000](http://localhost:8000)
- **Documentação Interativa Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Exemplo Mínimo de Inferência Preditiva (cURL)
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"temperatura_c": 92.5, "vibracao_mm_s": 7.4, "pressao_bar": 22.0}'
```

Resposta:
```json
{
  "falha_prevista": 1,
  "risco_de_falha": "Sim",
  "probabilidade_falha_percentual": 78.0,
  "severidade_alerta": "CRÍTICO_INTERVENÇÃO",
  "recomendacao_operacional": "Interromper operação imediatamente e despachar equipe técnica de emergência para o mancal."
}
```

### 3. Execução via Docker Compose
```bash
docker compose up --build
```

## Estrutura do Projeto
```text
.
├── .editorconfig              # Padronização de estilo e indentação
├── .gitignore                 # Arquivos e pastas ignorados no versionamento
├── CHANGELOG.md               # Histórico de alterações do projeto
├── CONTRIBUINDO.md            # Guia de contribuição e convenções de commit
├── LICENSE                    # Licença de uso de software (MIT)
├── README.md                  # Apresentação e instruções da solução
├── Dockerfile                 # Especificação do container de produção
├── docker-compose.yml         # Orquestração do serviço da API
├── requirements.txt           # Dependências Python fixadas
├── app.py                     # API RESTful FastAPI e rotas de inferência
├── visao_computacional.py     # Pipeline de inspeção por visão computacional
├── index.html                 # Interface web / dashboard supervisório
├── gerar_parecer_tecnico.py   # Gerador do parecer técnico executivo em PDF
├── dados_sensores_metaltech.csv # Base histórica de telemetria
├── docs/                      # Relatórios técnicos e pareceres regulatórios
├── images/                    # Imagens padrão e amostras de inspeção
└── models/                    # Artefato serializado do modelo (Random Forest)
```

## Testes
Para validar os componentes analíticos e o classificador:

```bash
# Validar pipeline de visão computacional em amostras reais
python visao_computacional.py

# Validar teste do modelo preditivo
python -c "import joblib; m = joblib.load('models/modelo_random_forest.joblib'); print('Modelo carregado com sucesso:', m)"
```

## Contribuindo
Consulte as orientações completas em [CONTRIBUINDO.md](CONTRIBUINDO.md) para conventions de commit, fluxo de branches e padrões de código.

## Licença
Distribuído sob a Licença MIT. Consulte [LICENSE](LICENSE) para mais detalhes.
