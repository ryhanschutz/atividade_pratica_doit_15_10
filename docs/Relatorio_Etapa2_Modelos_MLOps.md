# METALTECH SOLUÇÕES INDUSTRIAIS S.A.
# RELATÓRIO COMPARATIVO DE MODELOS E PLANO DE MLOps (ETAPA 2)
**Projeto:** Fábrica Inteligente: Preditiva e Visão Computacional  
**Documento:** RM-PREDITIVA-002  
**Autor:** Engenharia de Machine Learning & MLOps  
**Status:** Validado e Aprovado  

---

## 1. Preparação para Treinamento de Modelos
- **Conjuntos:** Separação estrita de Variáveis Previsoras ($X$: `temperatura_c`, `vibracao_mm_s`, `pressao_bar`) e Alvo ($y$: `falha_motor`).
- **Divisão Treino/Teste:** 70% para treinamento (7.000 amostras) e 30% para teste e homologação cega (3.000 amostras), com estratificação de classe para preservar a taxa real de falhas.
- **Pipeline de Pré-processamento:** Padronização estatística via `StandardScaler` ($\mu = 0, \sigma = 1$) integrada diretamente ao fluxo de inferência para evitar vazamento de dados.

## 2. Comparativo de Algoritmos de Classificação
Foram treinados e comparados dois modelos de classificação supervisionada sob métricas industriais:

| Algoritmo | Acurácia | Precisão | Recall (Sensibilidade) | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **Regressão Logística** | 99.77% | 95.54% | **100.00%** | 97.72% |
| **Random Forest (Campeão)** | **99.97%** | **99.34%** | **100.00%** | **99.67%** |

### Discussão Crítica das Métricas:
- **Prioridade Estratégica do Recall:** Na manufatura e manutenção preditiva contínua, o **Recall é a métrica mais crítica**. Um falso negativo (deixar uma falha real passar despercebida) implica na destruição catastrófica de eixos de transmissão, queima de estator e paralisação imprevista de toda a linha com prejuízos estimados em centenas de milhares de reais. Ambos os modelos alcançaram 100% de Recall no conjunto de teste.
- **Superioridade do Random Forest:** O classificador Random Forest superou a Regressão Logística na Precisão (99.34% vs 95.54%), reduzindo drasticamente os falsos positivos (falsos alarmes que interromperiam desnecessariamente a produção). O modelo foi exportado e serializado em `models/modelo_random_forest.joblib`.

## 3. Aprendizado Não Supervisionado (Clusterização K-Means)
Aplicou-se o algoritmo **K-Means ($k=2$)** sobre os dados normalizados de sensores sem os rótulos de falha:
- **Capacidade de Separação:** O modelo K-Means agrupou espontaneamente 98.6% das falhas críticas em um cluster isolado, demonstrando que a assinatura física da falha mecânica forma um agrupamento denso e geometricamente distante do envelope operacional padrão no espaço tridimensional $(\text{Temperatura}, \text{Vibração}, \text{Pressão})$.

---

## 4. Plano Simples de MLOps: Monitoramento da Degradação em 6 Meses
Como garantia de estabilidade e confiabilidade contínua do modelo preditivo em produção, a equipe de MLOps executará a seguinte rotina semestral:

```
[ Sensores IoT / CLPs ] ---> [ Ingestão Telemetria ] ---> [ FastAPI /predict ]
                                     |                           |
                                     v                           v
                           [ Banco TimeSeries ]        [ Previsões Registradas ]
                                     \                          /
                                      v                        v
                            [ Monitoramento MLOps: Data Drift & Recall ]
                                           |
                                [ Gatilho de Retreino ]
```

1. **Monitoramento de Data Drift (Deriva de Dados - Teste KS / PSI):**
   - **Frequência:** Semanal.
   - **Métrica:** Population Stability Index (PSI) e teste Kolmogorov-Smirnov comparando a distribuição estatística de entrada das medições dos últimos 7 dias com o baseline de treinamento.
   - **Gatilho de Alerta:** $PSI > 0.1$ aciona investigação de calibração de sensores físicos; $PSI > 0.25$ força retreino supervisionado.

2. **Monitoramento de Concept Drift (Deriva de Conceito):**
   - **Frequência:** Mensal.
   - **Ação:** Cruzamento do log de predições da API com os relatórios reais de ordens de serviço (OS) de manutenção corretiva e preventiva abertas no sistema ERP/CMMS (SAP PM).
   - **Gatilho de Degradação:** Se o Recall industrial cair abaixo de 98.5% ou a taxa de falsos positivos subir acima de 2%, uma nova versão candidata do modelo é gerada.

3. **Ciclo de Retreino Automatizado e Shadow Deployment (Canary):**
   - **Janela de Retreino:** A cada 90 dias com janela deslizante de 12 meses de dados históricos.
   - **Deploy Seguro:** Novos modelos rodam em modo *Shadow Mode* por 15 dias na API, registrando predições em paralelo sem atuar nos atuadores até comprovação de superioridade estocástica.

4. **Auditoria de Integridade de Artefatos:**
   - Armazenamento em versionador de modelos (MLflow Model Registry) com cálculo automático de hash SHA-256 e validação de compatibilidade com as versões de bibliotecas (`scikit-learn`, `joblib`).
