# METALTECH SOLUÇÕES INDUSTRIAIS S.A.
# RELATÓRIO EXECUTIVO DE DIAGNÓSTICO E TRATAMENTO DE DADOS (ETAPA 1)
**Projeto:** Fábrica Inteligente: Preditiva e Visão Computacional  
**Documento:** RE-DADOS-001  
**Autor:** Engenharia de Dados & Automação  
**Status:** Concluído e Aprovado  

---

## 1. Contexto e Importância Industrial
A MetalTech S.A. instrumentou suas linhas produtivas com sensores de telemetria IoT capturando grandezas termodinâmicas e cinemáticas em alta cadência temporal. Entretanto, devido ao ambiente agressivo de chão de fábrica, com campos eletromagnéticos provenientes de motores elétricos e inversores de frequência (ruído EMI), as séries temporais brutas exportadas (`dados_sensores_metaltech.csv`, 10.000 registros) apresentaram perdas de pacotes (dados nulos) e anomalias de hardware (outliers físicos).

## 2. Inspeção Inicial do Dataset
A análise exploratória inicial do dataset de telemetria revelou a seguinte composição:
- **Volume Total:** 10.000 medições temporais distribuídas entre 5 centros de usinagem e motobombas distintas (`M01` a `M05`).
- **Variáveis Monitoradas:** `timestamp`, `id_maquina`, `temperatura_c`, `vibracao_mm_s`, `pressao_bar` e a variável de resposta `falha_motor` (binária).
- **Valores Ausentes:** 
  - `temperatura_c`: 296 medições nulas (~2.96%)
  - `vibracao_mm_s`: 299 medições nulas (~2.99%)
  - `pressao_bar`: 300 medições nulas (~3.00%)
- **Duplicatas de Linha:** 0 registros duplicados.

## 3. Metodologia de Limpeza de Dados (Data Cleaning)
Para garantir integridade física e reprodutibilidade analítica, foram adotadas as seguintes técnicas especializadas:

1. **Ordenação Temporal por Ativo:** O conjunto de dados foi indexado temporalmente e ordenado por `(id_maquina, timestamp)`, garantindo a preservação da cronologia estocástica da série.
2. **Interpolação de Séries Temporais:** Os valores nulos pontuais foram tratados através de interpolação linear (`interpolate(method='linear')`), seguida de propagação de borda (`bfill` / `ffill`), técnica recomendada para processos contínuos onde grandezas térmicas e de pressão não sofrem descontinuidades discretas instantâneas.
3. **Tratamento de Outliers Físicos Operacionais:**
   - **Temperaturas de Sensor Saturado (999.9 °C):** Valores resultantes de curto-circuito ou estouro de escala nos termopares foram isolados e substituídos por interpolação física local ou eliminados conforme os limites térmicos operacionais da máquina (máx. seguro de 125 °C).
   - **Vibrações Negativas:** A grandeza de velocidade de vibração global RMS ($\text{mm/s}$) é estritamente positiva por definição matemática da norma ISO 10816. Registros negativos (ruído de offset no conversor A/D) foram tratados.
   - **Z-Score e IQR:** Aplicação combinada de limiares de $Z > 3.0$ para identificação de espúrios nos parâmetros de pressão hidráulica.

## 4. Análise Exploratória e Correlações com a Falha
Após o saneamento, as análises de densidade e correlação de Pearson revelaram:
- **Correlação Vibração $\times$ Falha:** Correlação positiva forte ($r \approx 0.76$). Picos contínuos de vibração acima de $7.5\text{ mm/s}$ indicam desbalanceamento grave ou folga nos mancais de rolamento momentos antes do desligamento.
- **Correlação Temperatura $\times$ Falha:** Correlação positiva expressiva ($r \approx 0.71$). O atrito decorrente da perda de viscosidade da lubrificação culmina em aquecimento severo ($> 90^\circ\text{C}$).
- **Pressão Hidráulica:** Correlação negativa com a falha ($r \approx -0.42$), demonstrando que a perda de pressão no circuito de lubrificação é com frequência o evento precursor da elevação de temperatura e vibração.

## 5. Conclusão da Etapa
O dataset resultante (`data/dados_sensores_metaltech_tratados.csv`) foi sanitizado com 100% de preenchimento válido, viabilizando o pipeline de treinamento de modelos supervisionados e não-supervisionados com garantia contra contaminação de dados (data leakage).
