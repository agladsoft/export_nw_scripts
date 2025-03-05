import os
import json
import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.scripts.flat_export_nw import ExportNW, headers_eng
from src.scripts.parsed import ParsedDf


@pytest.fixture
def sample_dataframe():
    data = {
        "Год": [2023],
        "Месяц": ["Январь"],
        "Судно": ["  Ship A  "],
        "Рейс": ["  Voyage  "],
        "Номер контейнера": [" CSYTVS134948 "],
        "Направление": ["импорт"],
    }
    return pd.DataFrame(data)



@pytest.fixture
def temp_excel_file(tmp_path, sample_dataframe):
    file_path = tmp_path / "test.xlsx"
    sample_dataframe.to_excel(file_path, index=False)
    return file_path



@pytest.fixture
def temp_output_folder(tmp_path):
    folder = tmp_path / "output"
    folder.mkdir()
    return folder



@pytest.fixture
def export_nw(temp_excel_file, temp_output_folder):
    return ExportNW(str(temp_excel_file), str(temp_output_folder))



def test_read_file(export_nw):
    df = pd.read_excel(export_nw.input_file_path, dtype={"ИНН": str})
    assert not df.empty
    assert "Год" in df.columns
    assert "Месяц" in df.columns



def test_transformation_df(export_nw, sample_dataframe):
    df = sample_dataframe.copy()
    df = df.rename(columns=headers_eng)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    assert "year" in df.columns
    assert "month" in df.columns
    assert "ship_name" in df.columns
    assert df["ship_name"].iloc[0] == "Ship A"



def test_add_new_columns(export_nw, sample_dataframe):
    df = sample_dataframe.copy()
    export_nw.add_new_columns(df)
    assert "original_file_name" in df.columns
    assert "original_file_parsed_on" in df.columns
    assert df["original_file_name"].iloc[0] == os.path.basename(export_nw.input_file_path)
    try:
        datetime.strptime(df["original_file_parsed_on"].iloc[0], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        pytest.fail("Неверный формат даты в столбце original_file_parsed_on")



def test_change_type_and_values(sample_dataframe):
    df = sample_dataframe.copy()

    df["ship_name"] = [None]
    df["voyage"] = [None]
    ExportNW.change_type_and_values(df)
    assert df["ship_name"].iloc[0] == "Нет данных"
    assert df["voyage"].iloc[0] == "Нет данных"



def test_write_to_json(export_nw, sample_dataframe, temp_output_folder):
    df = sample_dataframe.copy()
    df = df.rename(columns=headers_eng)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    export_nw.add_new_columns(df)
    ExportNW.change_type_and_values(df)
    df = df.replace({np.nan: None, "NaT": None})
    df["direction"] = df["direction"].replace({"импорт": "import", "экспорт": "export", "каботаж": "cabotage"})
    parsed_data = df.to_dict("records")
    export_nw.write_to_json(parsed_data)

    output_file = temp_output_folder / (os.path.basename(export_nw.input_file_path) + ".json")
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["year"] == 2023
    assert data[0]["direction"] == "import"



def test_main(export_nw):
    export_nw.main()
    output_file = os.path.join(export_nw.output_folder, os.path.basename(export_nw.input_file_path) + ".json")
    assert os.path.exists(output_file)
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Ожидается, что JSON содержит список с одной записью
    assert isinstance(data, list)
    assert len(data) == 1

    expected_keys = set(list(headers_eng.values()) + ["original_file_name", "original_file_parsed_on"])
    assert expected_keys.issubset(set(data[0].keys()))

    assert data[0]["direction"] == "import"
