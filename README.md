# Documentação do Projeto CSV

## Visão Geral
Este projeto é uma aplicação web desenvolvida em Python utilizando o framework Flask. Ele permite o upload de arquivos CSV, processamento de dados, geração de gráficos e download de resultados processados. A aplicação foi projetada para ser simples e intuitiva, com funcionalidades adicionais para filtragem e visualização de dados.

## Funcionalidades
1. **Upload de Arquivos CSV**: Permite o envio de arquivos CSV para processamento.
2. **Processamento de Dados**: Agrupa os dados por colunas específicas (`department`, `title`, `access`) e gera um arquivo CSV processado.
3. **Download de Resultados**: O arquivo processado pode ser baixado diretamente pela interface.
4. **Geração de Gráficos**: Cria gráficos de pizza baseados nos dados processados, com opções de filtragem por `department`, `title` e `access`.
5. **Filtros Dinâmicos**: Os filtros são atualizados dinamicamente com base nos dados disponíveis.
6. **Interface Intuitiva**: Botões para navegação e interação, incluindo um botão para acessar a página de gráficos.

## Requisitos
- Python 3.8 ou superior
- Bibliotecas Python: Flask, pandas, matplotlib
- Navegador web moderno

## Configuração e Execução

### Passo 1: Clonar o Repositório
Clone o repositório para sua máquina local:
```bash
$ git clone <URL_DO_REPOSITORIO>
$ cd Projeto_CSV
```

### Passo 2: Instalar Dependências
Instale as dependências necessárias utilizando o `pip`:
```bash
$ pip install -r requirements.txt
```

### Passo 3: Executar a Aplicação
Inicie o servidor Flask:
```bash
$ python app.py
```
A aplicação estará disponível em `http://127.0.0.1:5000/`.

## Utilização

### Tela Inicial
1. **Upload de Arquivo**: Clique no botão "Escolher arquivo" e selecione um arquivo CSV.
2. **Download de Resultados**: Após o upload, clique no botão "Download result" para baixar o arquivo processado.
3. **Ir para o Gráfico**: Clique no botão "Ir para o Gráfico" para acessar a página de visualização de gráficos.

### Página de Gráficos
1. **Filtros**: Utilize os menus suspensos para filtrar os dados por `department`, `title` e `access`.
2. **Visualização do Gráfico**: O gráfico de pizza será atualizado automaticamente com base nos filtros aplicados.
3. **Download do Gráfico**: O gráfico gerado é exibido no centro da página e pode ser salvo manualmente como imagem.

## Sugestões de Telas

### Tela Inicial
- Mostre o botão de upload, o botão de download e o botão "Ir para o Gráfico".

### Página de Gráficos
- Capture a tela com os filtros preenchidos e o gráfico de pizza exibido no centro.

## Estrutura do Projeto
```
Projeto_CSV/
├── app.py
├── main.py
├── generate_pdf.py
├── grouped_output.csv
├── input.csv
├── README.md
├── static/
│   └── chart.png
├── templates/
│   ├── chart.html
│   └── upload.html
└── Documentacao_Projeto_CSV.pdf
```

## Observações
- Certifique-se de que o arquivo `input.csv` esteja no formato correto antes de fazer o upload.
- Caso encontre erros, verifique os logs no terminal para mais detalhes.