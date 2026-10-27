# Contribuindo com a MetalTech

Agradecemos o interesse em contribuir com a Central de Manutenção Preditiva e Visão Computacional da MetalTech!

## Padrões de Desenvolvimento

### 1. Branches
- `main`: sempre estável e pronta para produção.
- Branches curtas criadas a partir de `main`:
  - `feat/nome-da-funcionalidade`
  - `fix/nome-da-correcao`
  - `docs/nome-da-documentacao`

### 2. Commits (Conventional Commits em pt-br)
Utilizamos mensagens no modo imperativo com tipos bem definidos:
- `feat(escopo)`: nova funcionalidade.
- `fix(escopo)`: correção de bug.
- `docs(escopo)`: alteração em documentações.
- `refactor(escopo)`: refatoração de código sem alteração funcional.
- `test(escopo)`: adição ou ajuste de testes.
- `chore(escopo)`: tarefas de build, dependências ou infraestrutura.
- `ci(escopo)`: ajustes de integração contínua / pipelines.

> Limite de 72 caracteres na primeira linha, sem ponto final.  
> Exemplo: `feat(predicao): adiciona calculo de severidade para falha de motor`

### 3. Convenções de Código
- Código em **Python**: padrão PEP 8 / `snake_case`.
- Arquivos e pastas do repositório: **kebab-case**, sem acentuação, espaços ou caracteres especiais.
- Todos os identificadores no código devem manter um idioma consistente (`pt-br`).

### 4. Fluxo de Pull Request (PR)
1. Crie sua branch a partir de `main`.
2. Realize alterações atômicas com testes locais.
3. Abra um Pull Request detalhando a motivação e os testes efetuados.
