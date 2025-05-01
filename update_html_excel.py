import pandas as pd
import json
import re

def excel_para_html(excel_path, html_path):
    # Carregar dados do Excel
    df = pd.read_excel(excel_path)

    # Garantir que latitude e longitude sejam numéricos (float)
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

    # Remover linhas sem coordenadas válidas (opcional, mas recomendado)
    df = df.dropna(subset=['Latitude', 'Longitude'])

    # Converter DataFrame para dicionário (lista de banheiros)
    dados = df.to_dict(orient='records')

    # Serializar JSON com acentos e indentação
    dados_js = json.dumps(dados, ensure_ascii=False, indent=2)

    # Ler HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Substituir conteúdo da variável bathrooms no HTML
    pattern = r'const bathrooms = \[.*?\];'
    nova_const = f'const bathrooms = {dados_js};'
    html_atualizado = re.sub(pattern, nova_const, html, flags=re.DOTALL)

    # Salvar HTML atualizado
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_atualizado)

    print("✅ HTML atualizado com dados do Excel.")

path_excel = r"C:\Users\lucar\OneDrive\Documentos\Projetos\OCRC\Avaliação de Banehiros.xlsx"
path_html = r"C:\Users\lucar\OneDrive\Documentos\Projetos\OCRC\index.html"

# Uso
excel_para_html(path_excel, path_html)

