# tools.py
from typing import List, Dict, Any
from .api_utilities import (
    name_resolver,
    node_normalizer
)


def lookup_name(
    string: str,
    autocomplete: bool = True,
    highlighting: bool = False,
    offset: int = 0,
    limit: int = 10,
    biolink_type: List[str] = None,
    only_prefixes: str = None,
    exclude_prefixes: str = None,
    only_taxa: str = None
) -> List[Dict[str, Any]]:
    """Wrapper around Name Resolver service."""
    return name_resolver(
        string=string,
        autocomplete=autocomplete,
        highlighting=highlighting,
        offset=offset,
        limit=limit,
        biolink_type=biolink_type,
        only_prefixes=only_prefixes,
        exclude_prefixes=exclude_prefixes,
        only_taxa=only_taxa
    )


def normalize_nodes(
    curies: List[str],
    conflate: bool = True,
    drug_chemical_conflate: bool = False,
    description: bool = False,
    individual_types: bool = False
) -> Dict[str, Any]:
    """Wrapper around Node Normalizer service."""
    return node_normalizer(
        curies=curies,
        conflate=conflate,
        drug_chemical_conflate=drug_chemical_conflate,
        description=description,
        individual_types=individual_types
    )
