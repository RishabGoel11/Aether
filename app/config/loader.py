from pathlib import Path

import yaml

from app.config.config import Settings


class ConfigLoader:
    def load(self) -> Settings:
        config_path = Path(__file__).parent / "settings.yaml"

        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}"
            )

        with config_path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        if data is None:
            data = {}

        return Settings(**data)