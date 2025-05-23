import io
from typing import Dict

from src.application.dto.drug_catalog_dto import CountryCode as ParserType
from src.infrastructure.services.pandas_parser.drug.contract import PandasParser
from src.infrastructure.services.pandas_parser.drug.impl.iat import AT_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ica import HR_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ica_pillcheck import (
    CA_PillcheckParser,
)
from src.infrastructure.services.pandas_parser.drug.impl.icy import GR_Parser
from src.infrastructure.services.pandas_parser.drug.impl.icz import CZ_Parser
from src.infrastructure.services.pandas_parser.drug.impl.idk import DK_Parser
from src.infrastructure.services.pandas_parser.drug.impl.iee import EE_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ieu import EU_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ibe import BE_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ies import ES_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ifi import FI_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ifr import FR_Parser
from src.infrastructure.services.pandas_parser.drug.impl.igr import GR_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ihr import HR_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ihu import HU_Parser
from src.infrastructure.services.pandas_parser.drug.impl.iie import IE_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ilu import LU_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ilv import LV_Parser
from src.infrastructure.services.pandas_parser.drug.impl.imt import MT_Parser
from src.infrastructure.services.pandas_parser.drug.impl.inl import NL_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ipl import PL_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ipt import PT_Parser
from src.infrastructure.services.pandas_parser.drug.impl.iro import RO_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ise import SE_Parser
from src.infrastructure.services.pandas_parser.drug.impl.isk import SK_Parser
from src.infrastructure.services.pandas_parser.drug.impl.iuk import UK_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ius import US_Parser


def drug_parser_factory(parser_type: ParserType, file: io.BytesIO) -> PandasParser:
    parsers: Dict[ParserType, PandasParser] = {
        "EU": EU_Parser(file),
        "CENTRAL": CA_PillcheckParser(file),
    } | {
        "AT": AT_Parser(file),
        "BE": BE_Parser(file),
        "CA": HR_Parser(file),
        "CY": HR_Parser(file),
        "CZ": HR_Parser(file),
        "DK": HR_Parser(file),
        "EE": HR_Parser(file),
        "ES": HR_Parser(file),
        "FI": HR_Parser(file),
        "FR": HR_Parser(file),
        "GR": HR_Parser(file),
        "HR": HR_Parser(file),
        "HU": HU_Parser(file),
        "IE": IE_Parser(file),
        "LU": LU_Parser(file),
        "LV": LV_Parser(file),
        "MT": MT_Parser(file),
        "NL": NL_Parser(file),
        "PL": PL_Parser(file),
        "PT": PT_Parser(file),
        "RO": RO_Parser(file),
        "SE": SE_Parser(file),
        "SK": SK_Parser(file),
        "UK": UK_Parser(file),
        "US": US_Parser(file),
    }
    try:
        return parsers[parser_type]
    except KeyError:
        raise ValueError(f"Unsupported parser type: {parser_type}")
