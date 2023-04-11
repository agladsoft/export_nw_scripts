import os
import sys
import json
import numpy as np
import pandas as pd
from pandas import DataFrame

headers_eng: dict = {
    "Год": "year",
    "Месяц": "month",
    "Период": "period",
    "Линия": "line",
    "Судно": "ship_name",
    "Рейс": "voyage",
    "Порт": "tracking_seaport",
    "Отправитель": "shipper_name",
    "Получатель": "consignee_name",
    "Экспедитор": "expeditor",
    "Груз": "goods_name",
    "Тип контейнера": "container_type",
    "Размер контейнера": "container_size",
    "Кол-во контейнеров, шт.": "container_count",
    "Терминал": "terminal",
    "TEU": "teu",
    "Номер контейнера": "container_number",
    "Номер декларации гтд": "gtd_number",
    "КОД ТНВЭД": "tnved",
    "Группа груза по ТНВЭД": "tnved_group_id",
    "Наименование Группы": "tnved_group_name",
    "ИНН": "shipper_inn",
    "УНИ-компания": "shipper_name_unified",
    "Страна КОМПАНИИ": "shipper_country",
    "Направление": "direction",
    "Коносамент": "booking",
    "Порожний": "is_empty",
    "Вес нетто (кг)": "goods_weight_netto"
}


class ExportNW(object):
    def __init__(self, input_file_path: str, output_folder: str):
        self.input_file_path: str = input_file_path
        self.output_folder: str = output_folder

    @staticmethod
    def trim_all_columns(df) -> DataFrame:
        """
        Delete the empty lines at the beginning and at the end of the lines.
        """
        return df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    @staticmethod
    def change_type_and_values(df) -> None:
        """
        Change data types or changing values.
        """
        df[['ship_name', 'voyage']] = df[['ship_name', 'voyage']].apply(lambda x: x.fillna('Нет данных'))

    def write_to_json(self, parsed_data) -> None:
        """
        Write data to json.
        """
        basename: str = os.path.basename(self.input_file_path)
        output_file_path: str = os.path.join(self.output_folder, f'{basename}.json')
        with open(f"{output_file_path}", 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=4)

    def main(self) -> None:
        """
        The main function where we read the Excel file and write the file to json.
        """
        df: DataFrame = pd.read_excel(self.input_file_path)
        df = df.replace({np.nan: None})
        df = df.dropna(axis=0, how='all')
        df = df.rename(columns=headers_eng)
        df = df.loc[:, ~df.columns.isin(['direction', 'tnved_group_name', 'shipper_inn', 'shipper_name_unified',
                                         'destination_country'])]
        df = self.trim_all_columns(df)
        self.change_type_and_values(df)
        self.write_to_json(df.to_dict('records'))


export_nw: ExportNW = ExportNW(os.path.abspath(sys.argv[1]), sys.argv[2])
export_nw.main()