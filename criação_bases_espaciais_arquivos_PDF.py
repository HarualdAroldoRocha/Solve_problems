# Importando bibliotecas  - 2
import os
import pandas as pd
import numpy as np
import pdfplumber
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import re

#arcpy.env.addOutputsToMap = True

# Função para converter coordenadas grau, minuto, segundo em graus decimais
def convert(cord):

    cord_spl = list(re.split(r"\°|\'|\"", cord))

    grau = (float(cord_spl[0]) * -1)
    min = float(cord_spl[1])
    seg = float(cord_spl[2])

    dd = ((((seg / 60) + min) / 60) + grau) * -1

    return dd

# Armazena o arquivo PDF a ser trabalhado, parametrizado no ToolBox
filename = arcpy.GetParameterAsText(0)

# Lendo os arquivos PDF
pdf = pdfplumber.open(filename)
#pdf = pdfplumber.open(r"D:/DADOS/Python/trabalhos/E_comerce/CEP_Ecomerce_GIS/DRL_pdf/DRL_teste_tabelas.pdf")

# Identifica a quantidade de paginas do PDF
totalpaginas = len(pdf.pages)

# Extrai e agrupa as tabelas do PDF
tot_tabelas = []
for i in range(0, totalpaginas):
    # extrai a tabela da página para uma lista
    tab_pagina = pdf.pages[i].extract_tables(table_settings={})
    # agrupa as tabelas extraidas em uma lista só
    tot_tabelas = tot_tabelas + tab_pagina
flat_list = [item for l in tot_tabelas for item in l]  # desaninha a lista com o resultado da junção de tabelas

# Cria o dataframe selecionando somente as colunas que interessam
tab_final = pd.DataFrame(flat_list[4:], columns = ['Código', 'Longitude', 'Latitude',
                                                   'Altitude (m)', 'Código', 'Azimute', 'Dist. (m)'])

# Subistitui vírgula por ponto nas colunas de valor numérico
tab_final['Longitude'] = tab_final['Longitude'].str.replace(',', '.')
tab_final['Latitude'] = tab_final['Latitude'].str.replace(',', '.')
tab_final['Dist. (m)'] = tab_final['Dist. (m)'].str.replace(',', '.')

# Converte as coordenadas para graus decimais
tab_final['Latitude_dd'] = tab_final['Latitude'].apply(convert)
tab_final['Longitude_dd'] = tab_final['Longitude'].apply(convert)

# converte Pandas dataframe to Spatial Data Frame
sdf = pd.DataFrame.spatial.from_xy(tab_final, x_column='Longitude_dd', y_column='Latitude_dd', sr=4326)

# Define o nome da feature class de saída com base no arquivo de entrada
#filename_out =''.join(list(re.split(r"\/|\.", filename))[-2:-1]).replace(" ", "")
filename_out = os.path.splitext(os.path.basename(filename))[0]

# Converte Spatial Data Frame em Shapefile
out = sdf.spatial.to_featureclass(location=r"D:\DADOS\GIS\Cursos\Palestra_Geoinformação\MyProject1\MyProject1.gdb/" + filename_out, overwrite=True)

# Limpando os Locks
arcpy.Compact_management("D:\DADOS\GIS\Cursos\Palestra_Geoinformação\MyProject1\MyProject1.gdb")

# Adiciona o featureclass ao mapa ativo
arcpy.SetParameterAsText(1, out)
