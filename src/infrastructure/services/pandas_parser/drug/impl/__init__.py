import io
from typing import Literal, Dict

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


_OtherCode = Literal["CENTRAL", "EU"]
_CountryCode = Literal[
    "AT",
    "BE",
    "CA",
    "CY",
    "CZ",
    "DK",
    "EE",
    "ES",
    "EU",
    "FI",
    "FR",
    "GR",
    "HR",
    "HU",
    "IE",
    "LU",
    "LV",
    "MT",
    "NL",
    "PL",
    "PT",
    "RO",
    "SE",
    "SK",
    "UK",
    "US",
]
ParserType = _OtherCode | _CountryCode


def drug_parser_factory(parser_type: ParserType, file: io.BytesIO) -> PandasParser:
    parsers: Dict[ParserType, PandasParser] = {
        "EU": EU_Parser(file),
        "CENTRAL": CA_PillcheckParser(file),
    } | {
        "AT": AT_Parser(file),
        "BE": BE_Parser(file),
        "CA": CA_Parser(file),
        "CY": CY_Parser(file),
        "CZ": CZ_Parser(file),
        "DK": DK_Parser(file),
        "EE": EE_Parser(file),
        "ES": ES_Parser(file),
        "FI": FI_Parser(file),
        "FR": FR_Parser(file),
        "GR": GR_Parser(file),
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
