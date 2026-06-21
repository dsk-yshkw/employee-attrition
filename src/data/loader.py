import os
import pandas as pd
from src.config import MISSING_VALUES, SURVEY_NUMBERS


class DataLoader:
    def __init__(self, data_dir: str, language: str = "japanese"):
        self.data_dir = data_dir
        self.language = language

    def load_wave(self, survey_number: int) -> pd.DataFrame:
        csv_path = self._find_csv(survey_number)
        df = pd.read_csv(csv_path, encoding="utf-8-sig", low_memory=False)
        df = self._replace_missing(df)
        df["wave"] = survey_number
        return df

    def load_all_waves(self) -> dict[int, pd.DataFrame]:
        waves = {}
        for num in SURVEY_NUMBERS:
            wave_dir = os.path.join(self.data_dir, str(num))
            if os.path.isdir(wave_dir):
                waves[num] = self.load_wave(num)
        return waves

    def _find_csv(self, survey_number: int) -> str:
        base = os.path.join(self.data_dir, str(survey_number), self.language)
        for fname in os.listdir(base):
            if fname.endswith(".csv"):
                return os.path.join(base, fname)
        raise FileNotFoundError(f"No CSV found for survey {survey_number} in {base}")

    def _replace_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        for col, sentinel in MISSING_VALUES.items():
            if col in df.columns:
                df[col] = df[col].replace(sentinel, pd.NA)
        return df
