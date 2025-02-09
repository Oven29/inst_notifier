import os
import pathlib

import dotenv


root_dir = pathlib.Path(__file__).parents[1]
dotenv.load_dotenv(
    dotenv_path=os.path.join(root_dir, '.env'),
    override=True,
    encoding='utf-8',
)

BOT_TOKEN = os.getenv('BOT_TOKEN')
PROXY = os.getenv('PROXY') or None
