# Citizen Assist AI

## Integrantes
- Felipe Mitsuo Takahashi Stephano — RM570692
- Letícia Araújo Espindola — RM569308
- Milena de Aguiar Lopes Cardoso — RM570599

## Público e problema
O projeto atende jovens que estão procurando o primeiro emprego. O objetivo é facilitar a consulta de informações sobre documentos, oportunidades de trabalho e direitos trabalhistas, usando orientações obtidas em fontes oficiais.

**ODS relacionados:** ODS 8 (Trabalho Decente e Crescimento Econômico) e ODS 16 (Paz, Justiça e Instituições Eficazes).

## Como executar
1. Instale o Python 3 e abra a pasta `citizen-assist-ai` no VS Code.
2. Abra o terminal na pasta do projeto.
3. Execute:

```bash
python main.py
```

Não são necessárias bibliotecas externas. O programa apresenta as opções de pergunta, consulta por categoria, indicadores, exportação CSV e saída.

## Base e funcionamento
A base está em `data/base_conhecimento.csv` e contém 11 orientações de três categorias: Documentação, Primeiro emprego e Direitos trabalhistas. Cada registro possui identificação, categoria, título, palavras-chave, resposta, documentos, local de atendimento, fonte oficial e data de verificação.

As classes são `Orientacao` (dados e exibição), `BaseConhecimento` (leitura, categorias e busca) e `Assistente` (atendimento, histórico, indicadores e exportação). O arquivo `main.py` inicia o programa.

## Regra de busca
A pergunta, as palavras-chave e o título são convertidos para minúsculas, sem acentos e sem pontuação. A pontuação é:

- +3 por palavra-chave ou expressão encontrada na pergunta.
- +1 por palavra da pergunta com pelo menos quatro letras que também apareça no título.
- 6 pontos ou mais: confiança ALTA.
- 3 a 5 pontos: confiança MÉDIA.
- Menos de 3 pontos: orientação não encontrada.

Os resultados são organizados em uma lista de tuplas `(pontos, orientacao)`, em ordem decrescente. São apresentadas a melhor resposta e, quando existirem, até duas alternativas com no mínimo 3 pontos.

Não foram feitas integrações com outras disciplinas.

## Fontes consultadas
As páginas abaixo foram consultadas em 08/11/2026. O endereço correspondente a cada orientação também está registrado no CSV.

- Receita Federal — https://www.gov.br/pt-br/servicos/inscrever-no-cpf
- Governo Digital — https://www.gov.br/governodigital/pt-br/identidade/cin/perguntas-frequentes-sobre-a-cin/onde-os-brasileiros-e-brasileiras
- Ministério do Trabalho — https://www.gov.br/trabalho-e-emprego/pt-br/servicos/trabalhador/carteira-de-trabalho/perguntas-frequentes-carteira-de-trabalho-digital
- TSE — https://www.tse.jus.br/servicos-eleitorais/titulo-eleitoral/autoatendimento-eleitoral/autoatendimento-eleitoral-titulo-net
- SINE — https://www.gov.br/pt-br/servicos/buscar-emprego-no-sistema-nacional-de-emprego-sine
- Aprendizagem — https://www.gov.br/trabalho-e-emprego/pt-br/noticias-e-conteudo/2026/julho/aprendizagem-profissional-regras-direitos-e-funcionamento-do-contrato-de-aprendizagem
- Estágio e direitos trabalhistas — https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/acoes-e-programas/programas-projetos-acoes-obras-e-atividades/proteja/duvidas-frequentes/duvidas-frequentes
- FGTS — https://www.caixa.gov.br/beneficios-trabalhador/fgts/perguntas-frequentes/Paginas/default.aspx
- Férias — https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/perguntas-frequentes

## Testes com usuários

- Data dos testes: 09/11/2026
- Quantidade de pessoas que testaram: 3
- Total de atendimentos: 13
- Respostas encontradas: 84.6%
- Taxa de acerto (respostas que ajudaram): 84.6%
- Tempo médio para encontrar: 46 segundos
- Tentativas por atendimento: 1
- Facilidade de uso: 4/5
- Dúvidas sem solução: Como consertar um foguete? / Onde eu faço um novo RG?
- Melhoria realizada após os testes: Foi adicionada a palavra-chave "novo rg" à orientação Carteira de Identidade Nacional. Antes da alteração, a pergunta "Onde eu faço um novo RG?" não era reconhecida. Após a correção, a mesma pergunta retornou a orientação correta, com confiança MÉDIA (3 pontos).

## Limitações
A busca funciona com regras e palavras-chave, não com um modelo de IA generativa. Perguntas formuladas com termos diferentes dos cadastrados podem não ter resposta. O conteúdo depende da atualização manual do CSV e não substitui atendimento oficial. Perguntas com `@` ou oito ou mais dígitos são recusadas e não são registradas. A nota de facilidade é calculada na execução atual e não é armazenada entre execuções.

## Vídeo técnico
Link: [inserir URL do vídeo não listado no YouTube]