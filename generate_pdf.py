from fpdf import FPDF  # Ensure this is from fpdf2
import sys
from fpdf.enums import XPos, YPos
import os

class PDFUnicode(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Documentação do Projeto CSV', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(5)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)  # Changed to bold font
        self.cell(0, 10, title, 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_image(self, image_path, x, y, w, h):
        if os.path.exists(image_path):
            self.ln(1)  # Add spacing before placing the image
            self.set_y(self.get_y() + 1)  # Move the cursor to a new line before adding the image
            self.image(image_path, x=x, y=self.get_y(), w=w, h=h)
            self.ln(h + 1)  # Add spacing after the image to avoid overlap with subsequent text
        else:
            self.set_xy(x, y)  # Ensure the placeholder text is also positioned correctly
            self.set_font('Arial', '', 10)
            self.cell(0, 10, f'Imagem não encontrada: {image_path}', 0, 1, 'C')

# Criar o PDF
pdf = PDFUnicode()
pdf.add_font('Arial', '', 'arial.ttf')  # Add regular Arial font
pdf.add_font('Arial', 'B', 'arialbd.ttf')  # Add bold Arial font
pdf.add_page()

# Adicionar conteúdo
pdf.chapter_title('Visão Geral')
pdf.chapter_body('Este projeto é uma aplicação web desenvolvida em Python utilizando o framework Flask. Ele permite o upload de arquivos CSV, processamento de dados, geração de gráficos e download de resultados processados. A aplicação foi projetada para ser simples e intuitiva, com funcionalidades adicionais para filtragem e visualização de dados.')

pdf.chapter_title('Funcionalidades')
pdf.chapter_body('1. Upload de Arquivos CSV: Permite o envio de arquivos CSV para processamento.\n2. Processamento de Dados: Agrupa os dados por colunas específicas (department, title, access) e gera um arquivo CSV processado.\n3. Download de Resultados: O arquivo processado pode ser baixado diretamente pela interface.\n4. Geração de Gráficos: Cria gráficos de pizza baseados nos dados processados, com opções de filtragem por department, title e access.\n5. Filtros Dinâmicos: Os filtros são atualizados dinamicamente com base nos dados disponíveis.\n6. Interface Intuitiva: Botões para navegação e interação, incluindo um botão para acessar a página de gráficos.')

pdf.chapter_title('Configuração e Execução')
pdf.chapter_body('1. Clonar o Repositório: Clone o repositório para sua máquina local.\n2. Instalar Dependências: Instale as dependências necessárias utilizando o pip.\n3. Executar a Aplicação: Inicie o servidor Flask e acesse a aplicação no navegador.')

pdf.chapter_title('Utilização')
pdf.chapter_body('Tela Inicial:\n- Upload de Arquivo: Clique no botão "Escolher arquivo" e selecione um arquivo CSV.\n- Download de Resultados: Após o upload, clique no botão "Download result" para baixar o arquivo processado.\n- Ir para o Gráfico: Clique no botão "Ir para o Gráfico" para acessar a página de visualização de gráficos.\n\nPágina de Gráficos:\n- Filtros: Utilize os menus suspensos para filtrar os dados por department, title e access.\n- Visualização do Gráfico: O gráfico de pizza será atualizado automaticamente com base nos filtros aplicados.\n- Download do Gráfico: O gráfico gerado é exibido no centro da página e pode ser salvo manualmente como imagem.')

pdf.chapter_title('Estrutura do Projeto')
pdf.chapter_body('Projeto_CSV/\n├── app.py\n├── main.py\n├── generate_pdf.py\n├── grouped_output.csv\n├── input.csv\n├── README.md\n├── static/\n│   └── chart.png\n├── templates/\n│   ├── chart.html\n│   └── upload.html\n└── Documentacao_Projeto_CSV.pdf')

# Adicionar nomes para cada passo e tela
pdf.chapter_title('Tela Inicial')
pdf.chapter_body('Na tela inicial você vai enviar o arquivo desejado pelo botão "Escolher arquivo". Após o upload, clique no botão "Download result" para baixar o arquivo processado.')

# Tire uma captura de tela da página inicial da aplicação, mostrando os botões de upload, download e o botão "Ir para o Gráfico".
pdf.add_image('upload_screen.png', x=10, y=pdf.get_y(), w=100, h=50)  # Dynamically position the image based on the current cursor

# Tire uma captura de tela da página inicial da aplicação, mostrando o download concluído.
pdf.add_image('result_screen.png', x=10, y=pdf.get_y(), w=100, h=50)  # Dynamically position the image based on the current cursor

pdf.chapter_title('Utilização do Gráfico')
pdf.chapter_body('Para acessar a página de gráficos, clique no botão "Ir para o Gráfico" na página inicial. Na página de gráficos, você pode utilizar os filtros disponíveis para refinar os dados exibidos no gráfico de pizza.\n\nFiltros disponíveis:\n- **Departamento (department):** Selecione um departamento específico para visualizar os dados relacionados.\n- **Título (title):** Escolha um título para filtrar os dados.\n- **Acesso (access):** Filtre os dados com base no tipo de acesso.\n\nApós selecionar os filtros desejados, o gráfico será atualizado automaticamente para refletir os dados filtrados. Você também pode salvar o gráfico gerado manualmente como uma imagem.')

pdf.chapter_title('Tela de Gráficos')
# pdf.chapter_body('Tire uma captura de tela da página de gráficos, com os filtros preenchidos e o gráfico de pizza exibido no centro.')
pdf.add_image('grafico.png', x=10, y=pdf.get_y(), w=120, h=80)  # Adiciona a imagem grafico.png


# Salvar o PDF
pdf.output('Documentacao_Projeto_CSV.pdf')