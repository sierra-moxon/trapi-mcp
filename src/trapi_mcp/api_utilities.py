# api_utilities.py
import requests

# Base URLs for Translator services
NAME_RESOLVER_URL = "https://name-resolution-sri.renci.org/lookup"
NODE_NORMALIZER_URL = "https://nodenormalization-sri.renci.org/1.5/get_normalized_nodes"
GENETICS_KP_URL = "https://genetics-kp.transltr.io/genetics_provider/trapi/v1.5/query"


def name_resolver(
    string: str,
    autocomplete: bool = True,
    highlighting: bool = False,
    offset: int = 0,
    limit: int = 10,
    biolink_type: list[str] | None = None,
    only_prefixes: str | None = None,
    exclude_prefixes: str | None = None,
    only_taxa: str | None = None
) -> list[dict]:
    """
    Query the Name Resolver service to return cliques whose name or synonym contains the given string.
    """
    params: dict[str, str] = {
        "string": string,
        "autocomplete": str(autocomplete).lower(),
        "highlighting": str(highlighting).lower(),
        "offset": str(offset),
        "limit": str(limit)
    }
    if biolink_type:
        params["biolink_type"] = ",".join(biolink_type)
    if only_prefixes:
        params["only_prefixes"] = only_prefixes
    if exclude_prefixes:
        params["exclude_prefixes"] = exclude_prefixes
    if only_taxa:
        params["only_taxa"] = only_taxa

    response = requests.get(NAME_RESOLVER_URL, params=params)
    response.raise_for_status()
    return response.json()


def node_normalizer(
    curies: list[str],
    conflate: bool = True,
    drug_chemical_conflate: bool = False,
    description: bool = False,
    individual_types: bool = False
) -> dict:
    """
    Query the Node Normalizer service to return equivalent identifiers and semantic types for given CURIEs.

    Parameters:
        curies: list of CURIE strings to normalize.
        conflate: apply gene/protein conflation (default True).
        drug_chemical_conflate: apply drug/chemical conflation (default False).
        description: include curie descriptions when available (default False).
        individual_types: return individual types for equivalent identifiers (default False).

    Returns:
        A mapping of input CURIE to normalization results.
    """
    # Prepare query parameters, repeating 'curie' for each
    params: list[tuple[str, str]] = []
    for c in curies:
        params.append(("curie", c))
    params.extend([
        ("conflate", str(conflate).lower()),
        ("drug_chemical_conflate", str(drug_chemical_conflate).lower()),
        ("description", str(description).lower()),
        ("individual_types", str(individual_types).lower()),
    ])

    response = requests.get(NODE_NORMALIZER_URL, params=params)
    response.raise_for_status()
    return response.json()


def genetics_kp_query(query: dict) -> dict:
    """
    Submit a TRAPI query to the Genetics Knowledge Provider and return the response.

    This endpoint supports genetic associations between:
    - Disease ↔ Gene (biolink:condition_associated_with_gene, biolink:gene_associated_with_condition)
    - Disease ↔ Cell (biolink:genetic_association)
    - Disease ↔ Pathway (biolink:genetic_association)
    - Gene ↔ PhenotypicFeature (biolink:gene_associated_with_condition)
    - Cell ↔ PhenotypicFeature (biolink:genetic_association)
    - Pathway ↔ PhenotypicFeature (biolink:genetic_association)

    Supported node types and ID prefixes:
    - biolink:Disease: MONDO, EFO, UMLS, HP, NCIT, MESH, SNOMEDCT, DOID
    - biolink:Gene: NCBIGene, ENSEMBL, HGNC, OMIM, UMLS, UniProtKB
    - biolink:Cell: UBERON
    - biolink:Pathway: GO, REACT, BIOCARTA, KEGG, WP
    - biolink:PhenotypicFeature: MONDO, EFO, UMLS, HP, NCIT, MESH, SNOMEDCT, DOID

    Args:
        query: A TRAPI-formatted query dictionary with a "message" wrapper containing "query_graph"

    Example query structure:
        {
            "message": {
                "query_graph": {
                    "nodes": {
                        "n00": {
                            "ids": ["MONDO:0011936"],
                            "categories": ["biolink:Disease"]
                        },
                        "n01": {
                            "categories": ["biolink:Gene"]
                        }
                    },
                    "edges": {
                        "e00": {
                            "subject": "n00",
                            "object": "n01",
                            "predicates": ["biolink:condition_associated_with_gene"]
                        }
                    }
                }
            }
        }

    Returns:
        Dictionary containing the TRAPI response with:
        - message: Full TRAPI message with query_graph, knowledge_graph, and results
        - status: Success/Error status
        - description: Human-readable description
        - logs: Processing logs
    """
    # Validate that the query has the required "message" wrapper
    if "message" not in query:
        raise ValueError(
            "Genetics KP query must be wrapped in a 'message' object. "
            "Expected format: {'message': {'query_graph': {...}}}"
        )

    if "query_graph" not in query["message"]:
        raise ValueError(
            "Genetics KP message must contain a 'query_graph' object. "
            "Expected format: {'message': {'query_graph': {...}}}"
        )

    response = requests.post(GENETICS_KP_URL, json=query)
    response.raise_for_status()
    return response.json()
