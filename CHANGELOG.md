# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato baseia-se em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/)
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2026-10-27

### Adicionado
- Pipeline de diagnóstico e tratamento estatístico de dados de sensores (`01_diagnostico_dados.ipynb`).
- Modelagem de manutenção preditiva com Random Forest e K-Means (`models/modelo_random_forest.joblib`).
- Módulo de visão computacional em OpenCV para inspeção geométrica e detecção de oxidação (`visao_computacional.py`).
- API RESTful em FastAPI com endpoints `/predict`, `/health` e documentação interativa Swagger/OpenAPI (`app.py`).
- Painel interativo de supervisão industrial para operadores e engenharia (`index.html`).
- Gerador executivo de Parecer Técnico e Regulatório em PDF (`gerar_parecer_tecnico.py`).
- Containerização da aplicação com `Dockerfile`, `docker-compose.yml` e `requirements.txt`.
