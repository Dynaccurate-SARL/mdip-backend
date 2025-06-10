from typing import Dict

from src.application.dto.drug_catalog_dto import CountryCode as ParserType
from src.infrastructure.services.pandas_parser.drug.contract import PandasParser
from src.infrastructure.services.pandas_parser.drug.impl.iat import AT_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ica import CA_Parser
from src.infrastructure.services.pandas_parser.drug.impl.ica_pillcheck import (
    CA_PillcheckParser,
)
from src.infrastructure.services.pandas_parser.drug.impl.icy import CY_Parser
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


def drug_parser_factory(parser_type: ParserType) -> PandasParser:
    parsers: Dict[ParserType, PandasParser] = {
        "EU": EU_Parser,
        "XX": CA_PillcheckParser,
    } | {
        "AT": AT_Parser,
        "BE": BE_Parser,
        "CA": CA_Parser,
        "CY": CY_Parser,
        "CZ": CZ_Parser,
        "DK": DK_Parser,
        "EE": EE_Parser,
        "ES": ES_Parser,
        "FI": FI_Parser,
        "FR": FR_Parser,
        "GR": GR_Parser,
        "HR": HR_Parser,
        "HU": HU_Parser,
        "IE": IE_Parser,
        "LU": LU_Parser,
        "LV": LV_Parser,
        "MT": MT_Parser,
        "NL": NL_Parser,
        "PL": PL_Parser,
        "PT": PT_Parser,
        "RO": RO_Parser,
        "SE": SE_Parser,
        "SK": SK_Parser,
        "UK": UK_Parser,
        "US": US_Parser,
    }
    try:
        return parsers[parser_type]
    except KeyError:
        raise ValueError(f"Unsupported parser type: {parser_type}")
