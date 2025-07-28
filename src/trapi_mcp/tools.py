# tools.py
from typing import List, Dict, Any
from .api_utilities import (
    submit_trapi_query,
    get_trapi_status,
    get_trapi_results,
    name_resolver,
    node_normalizer
)


def trapi(
    subject: str,
    object: str,
    predicate: str,
    attributes: List[Dict[str, Any]] = None,
    qualifiers: List[Dict[str, Any]] = None,
    subject_categories: List[str] = None,
    object_categories: List[str] = None
) -> Dict[str, Any]:
    """
    Build a simple TRAPI query graph for a single edge between subject and object,
    submit it to the ARS, and return the submission response (including pk).
    
    Args:
        subject: CURIE identifier for the subject node (e.g., "MONDO:0021117")
        object: CURIE identifier for the object node (e.g., "HGNC:6284") or leave empty for open query
        predicate: Biolink predicate (e.g., "biolink:risk_affected_by", "biolink:treats")
        attributes: Optional list of edge attributes
        qualifiers: Optional list of edge qualifiers
        subject_categories: Optional biolink categories for subject (e.g., ["biolink:Disease"])
        object_categories: Optional biolink categories for object (e.g., ["biolink:Gene"])
    
    Example usage:
        # Find what affects risk for a specific disease
        result = trapi(
            subject="MONDO:0021117",
            object="",  # Open query - find anything
            predicate="biolink:risk_affected_by",
            subject_categories=["biolink:Disease"],
            object_categories=["biolink:NamedThing"]
        )
        
        # Find phenotypes associated with a gene
        result = trapi(
            subject="HGNC:6284",
            object="",
            predicate="biolink:associated_with",
            subject_categories=["biolink:Gene"],
            object_categories=["biolink:PhenotypicFeature"]
        )
    
    Returns:
        ARS submission response containing:
        - "pk": Primary key to track query status
        - "fields": Query metadata and status
    """
    message: Dict[str, Any] = {
        "message": {
            "query_graph": {
                "nodes": {
                    "n0": {},
                    "n1": {}
                },
                "edges": {
                    "e0": {
                        "subject": "n0",
                        "object": "n1",
                        "predicates": [predicate]
                    }
                }
            }
        }
    }
    
    # Add IDs only if provided (for open queries, nodes have only categories)
    if subject:
        message["message"]["query_graph"]["nodes"]["n0"]["ids"] = [subject]
    if object:
        message["message"]["query_graph"]["nodes"]["n1"]["ids"] = [object]
    if subject_categories:
        message["message"]["query_graph"]["nodes"]["n0"]["categories"] = subject_categories
    if object_categories:
        message["message"]["query_graph"]["nodes"]["n1"]["categories"] = object_categories
    if attributes:
        message["message"]["query_graph"]["edges"]["e0"]["attributes"] = attributes
    if qualifiers:
        message["message"]["query_graph"]["edges"]["e0"]["qualifiers"] = qualifiers
    return submit_trapi_query(message)


def trapi_status(pk: str) -> Dict[str, Any]:
    """
    Check status of a TRAPI job.

    The status is retrieved from the ARS messages endpoint. Typical statuses are:
    - "Running" - The ARS has sent this query to ARAs or begun merging, but it's not complete
    - "Done" - No further changes to this message expected
    - "Error" - Either a Translator tool returned an error or the ARS encountered processing error

    The status of the parent message will be "Done" only after all Translator tools have
    returned (or timed out) and the merging and post-processing is complete.
    """
    return get_trapi_status(pk)


def trapi_results(pk: str) -> Dict[str, Any]:
    """Fetch results of a completed TRAPI job."""
    return get_trapi_results(pk)


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
