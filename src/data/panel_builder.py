import pandas as pd
from src.data.loader import DataLoader
from src.config import PKEY


class PanelBuilder:
    def __init__(self, loader: DataLoader):
        self.loader = loader

    def build(self) -> pd.DataFrame:
        waves = self.loader.load_all_waves()
        frames = list(waves.values())
        panel = pd.concat(frames, ignore_index=True)
        panel = panel.sort_values([PKEY, "wave"]).reset_index(drop=True)
        return panel

    def build_transitions(self, panel: pd.DataFrame) -> pd.DataFrame:
        """Add next-wave attrition label: 1 if the respondent quit in the next wave."""
        panel = panel.copy()
        panel["wave_rank"] = panel.groupby(PKEY)["wave"].rank(method="first").astype(int)
        next_wave = (
            panel[[PKEY, "wave_rank", "Q46_1"]]
            .assign(wave_rank=lambda d: d["wave_rank"] - 1)
            .rename(columns={"Q46_1": "attrition_next_wave"})
        )
        panel = panel.merge(next_wave, on=[PKEY, "wave_rank"], how="left")
        return panel
