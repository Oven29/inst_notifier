import logging
import os
import pathlib

import dotenv


ROOT_DIR = pathlib.Path(__file__).parents[1]
dotenv.load_dotenv(
    dotenv_path=os.path.join(ROOT_DIR, '.env'),
    override=True,
    encoding='utf-8',
)

LOGS_DIR = os.path.join(ROOT_DIR, 'logs')
DATA_DIR = os.path.join(ROOT_DIR, 'data')

BOT_TOKEN = os.getenv('BOT_TOKEN')
PROXY = os.getenv('PROXY') or None

LOGGING_LEVEL = logging.INFO
