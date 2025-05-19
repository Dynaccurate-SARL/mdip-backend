import io
from typing import Literal

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser
from src.infrastructure.services.pandas_parser.drug.impl.ica_pillcheck import CA_PillcheckParser
from src.infrastructure.services.pandas_parser.drug.impl.ieu import EU_Parser

from src.infrastructure.services.pandas_parser.drug.impl.ibe import BE_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ies import ES_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ifr import FR_Parser
from src.infrastructure.services.pandas_parser.drug.impl.iie import IE_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ilv import LV_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ipl import PL_Parser
from src.infrastructure.services.pandas_parser.drug.impl.iro import RO_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ise import SE_Parser
from src.infrastructure.services.pandas_parser.drug.impl.iuk import UK_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ius import US_Parser


ParserType = Literal['CENTRAL', 'EU', 'CA', 'FR', 'US', 'UK', 'SE',
                     'RO', 'PL', 'LV', 'IE', 'ES', 'BE']


def drug_parser_factory(parser_type: ParserType,
                        file: io.BytesIO) -> PandasParser:
    match(parser_type):
        case 'CENTRAL':
            return CA_PillcheckParser(file)
        case 'EU':
            return EU_Parser(file)
        # -------------------------------------------------------
        case 'FR':
            return FR_Parser(file)
        case 'US':
            return US_Parser(file)
        case 'UK':
            return UK_Parser(file)
        case 'SE':
            return SE_Parser(file)
        case 'RO':
            return RO_Parser(file)
        case 'PL':
            return PL_Parser(file)
        case 'LV':
            return LV_Parser(file)
        case 'IE':
            return IE_Parser(file)
        case 'ES':
            return ES_Parser(file)
        case 'BE':
            return BE_Parser(file)
        case _:
            raise ValueError("Unsupported parser type")
