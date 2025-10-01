'''
Прочитаем что есть и сохраним в эксельку для визуализации
'''

# basic
import pandas as pd
import numpy as np
from tqdm import tqdm
from pathlib import Path
import re

# clusters
from sklearn.cluster import AgglomerativeClustering
from rapidfuzz import fuzz

# project
from Read_data import get_MSK_data
from Handy_func import timer
from Get_coord import get_coordinates_yandex

fallback_path = Path.joinpath(Path.cwd() , 'save.xlsx') # чтобы лишний раз не тратить апишку
out_path = Path.joinpath(Path.cwd() , 'total.xlsx')

@timer
def create_data():
    #---
    df_data = get_MSK_data()  # А кроме МСК ничего и нет
    df_data['address'] = 'г. Москва,' + df_data['address'] # улучшит точность

    # -- get coord
    df_data['coord'] = [get_coordinates_yandex(x) for x in tqdm(df_data['address'])]
    df_data.to_excel(fallback_path, index = False)
    print(f"bad is {df_data['coord'].isna().sum() / df_data.shape[0]:.3}% ")

def clean_data():
    # -- clean garbage
    df_data = pd.read_excel(fallback_path).copy()
    df_data = df_data[df_data['coord'].notna()] # пустые точно не нужно - судьба
    # пустот уже не будет
    def geo_fltr(coord): # примерно в квадрате Москвы
        long, att = coord.strip('[]').split(', ')
        long = pd.to_numeric(long)
        att  = pd.to_numeric(att)
        if ~(37 < att < 38.6) | ~ (55 < long < 57): # примерно ориентиры МСК
            return False
        else:
            return True # в границах

    df_data = df_data[[geo_fltr(x) for x in df_data['coord']]]
    df_data.to_excel(out_path, index= False)

@timer
def Try_2_cluster():
    df = pd.read_excel(out_path)
    developers = df['developer'].dropna().unique().tolist()
    print(f"Всего уникальных застройщиков: {len(developers)}")

    # почистим символы тк смысла в названиях немного
    def preprocess_dev_name(name):
        name = name.lower()
        # организационно-правовые формы
        opf_pattern = r"\b(ооо|ао|зао|пао|ип|фгбоу|фгбу|гу|гуп|фгаоу|фгуп|оао|оо|а|закрытое акционерное общество|публичное акционерное общество)\b"
        name = re.sub(opf_pattern, "", name)
        # специализированный застройщик
        sz_pattern = r"\b(специализированный застройщик|с\.?\s*з\.?|сз)\b"
        name = re.sub(sz_pattern, "", name)
        # общество с ограниченной ответственностью
        long_opf_pattern = r"\b(общество с ограниченной ответственностью)\b"
        name = re.sub(long_opf_pattern, "", name)
        # унитарное предприятие
        long_opf_pattern = r"\b(государственное унитарное предприятие)\b"
        name = re.sub(long_opf_pattern, "", name)
        # мусор
        name = re.sub(r"[^a-zа-яё0-9\s]", " ", name)
        # лишние пробелы
        name = re.sub(r'\s+', ' ', name).strip()

        return name

    processed_devs = [preprocess_dev_name(d) for d in developers]

    # матрица схожести
    n = len(processed_devs)
    similarity_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            score = fuzz.token_set_ratio(processed_devs[i], processed_devs[j])
            similarity_matrix[i][j] = score
            similarity_matrix[j][i] = score

    distance_matrix = 100 - similarity_matrix  # в расстояние

    # кластеризация
    clustering = AgglomerativeClustering(
        n_clusters=None,
        linkage='average',
        distance_threshold=10,  # меньше - строже
        metric='precomputed'
    )
    clusters = clustering.fit_predict(distance_matrix)

    # соберу в словарь
    dev_2_clusters = {}
    for idx, cluster_id in enumerate(clusters):
        dev_2_clusters[developers[idx]] = cluster_id

    # lj,fdk. d lfyyst
    df['cluster_id'] = df['developer'].map(dev_2_clusters)

    # не должно быть такого, но пусть будет
    df['cluster_id'] = df['cluster_id'].fillna(-1).astype(int)

    df.to_excel(out_path, index=False)









