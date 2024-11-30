from pathlib import Path
import os
from dotenv import load_dotenv
import argparse


class Settings:
    def __init__(self) -> None:
        self.api_key: str | None = None
        self.chunk_size: int = 2000
        self.model: str = "gpt-3.5-turbo"
        self._load_settings()

    def _load_settings(self) -> None:
        # 1. First try environment variables
        self.api_key = os.getenv("OPENAI_API_KEY")

        # 2. Then try .env file
        if not self.api_key:
            env_path: Path = Path(".env")
            if env_path.exists():
                load_dotenv()
                self.api_key = os.getenv("OPENAI_API_KEY")

        # 3. Finally, try command line arguments
        parser: argparse.ArgumentParser = argparse.ArgumentParser(
            description="PDF Translator Settings",
        )
        parser.add_argument("--api-key", help="OpenAI API Key")
        parser.add_argument(
            "--chunk-size",
            type=int,
            help="Translation chunk size",
            default=2000,
        )
        parser.add_argument(
            "--model",
            help="OpenAI model to use",
            default="gpt-3.5-turbo",
        )

        args, _ = parser.parse_known_args()

        if args.api_key:
            self.api_key = args.api_key
        if args.chunk_size:
            self.chunk_size = args.chunk_size
        if args.model:
            self.model = args.model

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)


settings = Settings()
