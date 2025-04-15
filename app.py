from flask import Flask, request, send_file, render_template, make_response, send_from_directory
import os
import subprocess
import logging
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import time
from matplotlib import rcParams, font_manager
rcParams['font.family'] = 'DejaVu Sans'
rcParams['font.sans-serif'] = ['DejaVu Sans']
matplotlib.font_manager.findSystemFonts(fontpaths=['.'])  # Restrict font search to the current directory
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)  # Suppress font manager debug logs
matplotlib.use('Agg')

# Configuração de logging para depuração
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.before_request
def clear_cache():
    # Evita que o navegador use uma versão em cache do formulário
    if request.endpoint == 'upload_file':
        response = make_response(render_template('upload.html'))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        return response

@app.before_request
def log_request_start():
    request.start_time = time.time()
    logging.debug(f"Starting request to {request.path} with method {request.method}")
    if request.args:
        logging.debug(f"Request args: {request.args}")
    if request.form:
        logging.debug(f"Request form data: {request.form}")

@app.after_request
def log_request_end(response):
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        logging.debug(f"Request to {request.path} completed in {duration:.2f} seconds with status {response.status_code}")
    return response

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/upload', methods=['POST'])
def handle_upload():
    logging.debug('Recebendo requisição POST para /upload')

    # Verifica se a requisição contém dados de arquivo
    if 'file' not in request.files:
        logging.error('Nenhum arquivo encontrado na requisição')
        return 'Nenhum arquivo foi enviado', 400

    file = request.files['file']

    # Verifica se o arquivo foi selecionado
    if not file or file.filename == '':
        logging.error('Nenhum arquivo foi selecionado para upload')
        return 'Nenhum arquivo foi selecionado', 400

    try:
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input.csv')
        file.save(input_path)
        logging.debug(f'Arquivo salvo com sucesso em {input_path}')

        # Executa o script Python
        subprocess.run(['python', 'main.py'], cwd=app.config['UPLOAD_FOLDER'], check=True, shell=True)
        logging.debug('Script main.py executado com sucesso')

        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'grouped_output.csv')
        if os.path.exists(output_path):
            logging.debug(f'Arquivo de saída encontrado em {output_path}')
            response = make_response(send_file(output_path, as_attachment=True))
            response.headers['Content-Type'] = 'text/csv'
            return response
        else:
            logging.error('Arquivo de saída não encontrado após a execução do script')
            return 'Erro interno: Arquivo de saída não encontrado', 500

    except Exception as e:
        logging.error(f'Erro ao processar o upload: {e}')
        return f'Erro interno: {str(e)}', 500

@app.route('/check-file', methods=['GET'])
def check_file():
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'grouped_output.csv')
    logging.debug(f'Verificando existência do arquivo em: {output_path}')
    if os.path.exists(output_path):
        logging.debug('Arquivo encontrado. Iniciando envio para o cliente.')
        response = send_file(output_path, as_attachment=True, mimetype='text/csv')
        response.headers['Content-Disposition'] = f'attachment; filename="grouped_output.csv"'
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        logging.debug('Arquivo enviado com sucesso.')
        return response
    else:
        logging.error('Arquivo não encontrado no servidor.')
        return 'Arquivo não encontrado', 404

@app.route('/chart', methods=['GET', 'POST'])
def chart():
    logging.debug("Entered /chart route")
    start_time = time.time()
    try:
        logging.debug("Reading grouped_output.csv")
        df = pd.read_csv('grouped_output.csv', delimiter=',')
        logging.debug(f"CSV loaded with {len(df)} rows")

        # Verificar se as colunas necessárias existem
        if 'department' not in df.columns or 'title' not in df.columns or 'count' not in df.columns:
            logging.error("Missing required columns in CSV")
            return "Erro: O arquivo CSV não contém as colunas necessárias (department, title, count)."

        # Filtros
        department_filter = request.args.get('department')
        title_filter = request.args.get('title')
        access_filter = request.args.get('access')

        if department_filter:
            logging.debug(f"Applying department filter: {department_filter}")
            df = df[df['department'] == department_filter]
        if title_filter:
            logging.debug(f"Applying title filter: {title_filter}")
            df = df[df['title'] == title_filter]
        if access_filter:
            logging.debug(f"Applying access filter: {access_filter}")
            df = df[df['access'] == access_filter]

        logging.debug(f"Dataframe filtered to {len(df)} rows")

        # Atualizar os valores únicos para o filtro de 'access'
        unique_access = df['access'].unique()

        # Sanitize data to remove unsupported characters
        def sanitize_text(text):
            return ''.join(c if ord(c) > 31 and ord(c) != 129 else '?' for c in text)

        df['access'] = df['access'].apply(sanitize_text)
        df['department'] = df['department'].apply(sanitize_text)
        df['title'] = df['title'].apply(sanitize_text)

        # Verificar se o DataFrame resultante está vazio após os filtros
        if df.empty:
            logging.warning("No data found after applying filters")
            return render_template('chart.html', chart_path=None, departments=df['department'].unique(), titles=df['title'].unique(), message="Nenhum dado encontrado para os filtros aplicados.")

        # Agrupamento para o gráfico
        logging.debug("Grouping data for chart")
        grouped = df.groupby(['department', 'title', 'access']).sum().reset_index()

        # Garantir que o diretório 'static' existe
        os.makedirs('static', exist_ok=True)

        # Configurar o caminho do gráfico
        chart_path = os.path.join('static', 'chart.png')

        # Criar gráfico de pizza apenas se houver dados válidos
        if not grouped.empty:
            try:
                logging.debug("Generating pie chart")
                plt.figure(figsize=(20, 8))
                plt.pie(grouped['count'], labels=grouped['access'], autopct=lambda p: f'{int(p * sum(grouped["count"]) / 100)}')
                plt.savefig(chart_path)
                plt.close()
                logging.debug("Pie chart saved successfully")
            except Exception as e:
                logging.error(f"Error generating chart: {e}")
                return render_template('chart.html', chart_path=None, departments=df['department'].unique(), titles=df['title'].unique(), message="Erro ao gerar o gráfico.")
        else:
            logging.warning("No valid data for chart after grouping")
            return render_template('chart.html', chart_path=None, departments=df['department'].unique(), titles=df['title'].unique(), message="Nenhum dado encontrado para os filtros aplicados.")

        logging.debug("Finished processing /chart route")
    except Exception as e:
        logging.error(f"Error in /chart route: {e}")
    finally:
        duration = time.time() - start_time
        logging.debug(f"/chart route completed in {duration:.2f} seconds")
    return render_template('chart.html', chart_path=chart_path, departments=df['department'].unique(), titles=df['title'].unique(), accesses=unique_access)

@app.route('/generate-chart', methods=['POST'])
def generate_chart():
    try:
        # Ler o arquivo CSV com o delimitador correto
        df = pd.read_csv('grouped_output.csv', delimiter=',')

        # Normalize column names to lowercase
        df.columns = df.columns.str.lower()

        # Verificar se as colunas necessárias existem
        if 'department' not in df.columns or 'title' not in df.columns or 'count' not in df.columns:
            return {"error": "O arquivo CSV não contém as colunas necessárias (department, title, count)."}, 400

        # Filtros
        department_filter = request.json.get('department')
        title_filter = request.json.get('title')
        access_filter = request.json.get('access')

        if department_filter:
            df = df[df['department'] == department_filter]
        if title_filter:
            df = df[df['title'] == title_filter]
        if access_filter:
            df = df[df['access'] == access_filter]

        # Sanitize data to remove unsupported characters
        def sanitize_text(text):
            return ''.join(c if ord(c) > 31 and ord(c) != 129 else '?' for c in text)

        df['access'] = df['access'].apply(sanitize_text)
        df['department'] = df['department'].apply(sanitize_text)
        df['title'] = df['title'].apply(sanitize_text)

        # Verificar se o DataFrame resultante está vazio após os filtros
        if df.empty:
            return {"error": "Nenhum dado encontrado para os filtros aplicados."}, 404

        # Agrupamento para o gráfico
        grouped = df.groupby(['department', 'title', 'access']).sum().reset_index()

        # Garantir que o diretório 'static' existe
        os.makedirs('static', exist_ok=True)

        # Configurar o caminho do gráfico
        chart_path = os.path.join('static', 'chart.png')

        # Criar gráfico de pizza apenas se houver dados válidos
        plt.figure(figsize=(20, 8))
        plt.pie(grouped['count'], labels=grouped['access'], autopct=lambda p: f'{int(p * sum(grouped["count"]) / 100)}')
        plt.savefig(chart_path)
        plt.close()

        return {"chart_path": chart_path}, 200

    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/scramble', methods=['POST', 'GET'])
def scramble():
    if request.method == 'POST':
        try:
            # Verifica se o arquivo foi enviado
            if 'file' not in request.files:
                return 'Nenhum arquivo foi enviado', 400

            file = request.files['file']

            # Verifica se o arquivo foi selecionado
            if not file or file.filename == '':
                return 'Nenhum arquivo foi selecionado', 400

            # Lê o arquivo CSV
            df = pd.read_csv(file)

            # Normalize column names to lowercase
            df.columns = df.columns.str.lower()

            # Validate required columns
            required_columns = {'name', 'login', 'department', 'title', 'access'}
            missing_columns = required_columns - set(df.columns.str.lower())
            if missing_columns:
                return f'Missing required columns: {missing_columns}', 400

            # Step 1: Scramble Departments
            grouped = df.groupby(['name', 'login'])
            departments = df['department'].unique()
            np.random.shuffle(departments)
            department_mapping = {name: departments[i % len(departments)] for i, name in enumerate(grouped.groups.keys())}

            for (name, login), group in grouped:
                # Assign the same department to all rows for the person
                df.loc[group.index, 'department'] = department_mapping[(name, login)]

            # Step 2: Scramble Titles and Access
            for (name, login), group in grouped:
                titles = group['title'].unique()
                np.random.shuffle(titles)
                title_mapping = {title: titles[i % len(titles)] for i, title in enumerate(titles)}

                for title in group['title'].unique():
                    title_rows = group[group['title'] == title]
                    new_title = title_mapping[title]

                    # Move all rows with the same title and their respective access
                    destination_rows = df[(df['title'] == new_title) & (df['name'] != name)]

                    # Ensure the lengths of source and destination rows match
                    if len(title_rows) == len(destination_rows):
                        df.loc[destination_rows.index, 'access'] = title_rows['access'].values
                        df.loc[destination_rows.index, 'name'] = name
                        df.loc[destination_rows.index, 'login'] = login
                    else:
                        logging.warning(f"Mismatch in row counts for Title '{title}' between source and destination.")
                        continue

                    # Update the title for the source rows
                    df.loc[title_rows.index, 'title'] = new_title

            # Save the scrambled file
            scrambled_path = os.path.join(app.config['UPLOAD_FOLDER'], 'scrambled_output.csv')
            df.to_csv(scrambled_path, index=False)

            return send_file(scrambled_path, as_attachment=True, mimetype='text/csv')

        except Exception as e:
            logging.error(f'Erro ao processar o arquivo: {e}')
            return f'Erro interno: {str(e)}', 500

    return render_template('scramble.html')

@app.route('/scrambled_output.csv', methods=['GET'])
def download_scrambled():
    scrambled_path = os.path.join(app.config['UPLOAD_FOLDER'], 'scrambled_output.csv')
    if os.path.exists(scrambled_path):
        return send_file(scrambled_path, as_attachment=True, mimetype='text/csv')
    else:
        return 'Arquivo não encontrado', 404

@app.route('/file-format')
def file_format():
    return render_template('file-format.html')

if __name__ == '__main__':
    app.run(debug=True)