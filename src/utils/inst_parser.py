import os.path

from src import config
from src.inst.parser import InterfaceInstParser, InstParser


inst_parser: InterfaceInstParser = InstParser()
inst_parser.set_proxy(config.PROXY)
inst_parser.login_from_file(os.path.join(config.DATA_DIR, 'inst.json'))
