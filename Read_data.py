import pandas as pd
from pathlib import Path
from Handy_func import timer

@timer # хочу
def get_MSK_data():
    # Получаем директорию текущего скрипта
    current_dir = Path.cwd()
    MSK_dir = Path.joinpath(Path.cwd(), 'MSK')

    files_read_cfg_MSK = {
        'DDY.xlsx': {
            'params': {'skiprows': 1, 'dtype': str, 'usecols': ['Адрес объекта в ЕИСЖС', 'Застройщик']},
            'address_col': 'Адрес объекта в ЕИСЖС',
            'developer_col': 'Застройщик',
            'name_value': 'ДДУ',
            'level_value':'ДДУ',
        },
        'FedNadzor.xlsx': {
            'params': {'skiprows': 4, 'dtype': str, 'usecols': [
                'Наименование объекта капитального строительства',
                'Адрес объекта',
                'Полное наименование юридического лица, Ф.И.О. индивидуального предпринимателя - Застройщика'
            ]},
            'address_col': 'Адрес объекта',
            'developer_col': 'Полное наименование юридического лица, Ф.И.О. индивидуального предпринимателя - Застройщика',
            'name_col': 'Наименование объекта капитального строительства',
            'level_value': 'Федназдор',
        },
        'RegNadzor.xlsx': {
            'params': {'skiprows': 1, 'dtype': str, 'usecols': [
                'Наименование объекта капитального строительства',
                'Адрес объекта',
                'Полное наименование юридического лица, Ф.И.О. индивидуального предпринимателя - Застройщика'
            ]},
            'address_col': 'Адрес объекта',
            'developer_col': 'Полное наименование юридического лица, Ф.И.О. индивидуального предпринимателя - Застройщика',
            'name_col': 'Наименование объекта капитального строительства',
            'level_value': 'Регнадзор',
        },
    }

    ### --- Считаем

    dfs = []

    for filename, config in files_read_cfg_MSK.items():
        #
        params = config['params']
        file_dir = Path.joinpath(MSK_dir, filename)
        df = pd.read_excel(file_dir, **params)

        # переименовываем колонки
        df = df.rename(columns={
            config['address_col']: 'address',
            config['developer_col']: 'developer',
        })

        # не везде есть названия объектов
        if 'name_col' in config:
            df = df.rename(columns={config['name_col']: 'name'})
        elif 'name_value' in config:
            df['name'] = config['name_value']

        df['source'] = filename.split('.')[0]
        df['level'] = config['level_value']

        # select
        df = df[['source', 'address', 'developer', 'name', 'level']]
        dfs.append(df)

    # Объединяем все датафреймы
    df_data = pd.concat(dfs, ignore_index=True)
    df_data.reset_index(inplace= True, drop= True)

    return df_data




