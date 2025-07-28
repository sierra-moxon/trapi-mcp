# api_utilities.py
import requests

# Base URLs for Translator services
ARS_SUBMIT_URL = "https://ars-prod.transltr.io/ars/api/submit"
ARS_RESULTS_URL_TEMPLATE = "https://ars-prod.transltr.io/ars/api/messages/{pk}"
NAME_RESOLVER_URL = "https://name-resolution-sri.renci.org/lookup"
NODE_NORMALIZER_URL = "https://nodenormalization-sri.renci.org/1.5/get_normalized_nodes"


def submit_trapi_query(query: dict) -> dict:
    """
    Submit a TRAPI query message to the ARS and return the raw JSON response.
    Raises an HTTPError if the request fails.
    
    Validates that the query is properly wrapped in a "message" object as required by ARS.
    
    Args:
        query: A TRAPI-formatted query dictionary that must be wrapped in a "message" object.
    
    Example of a valid TRAPI query:
        {
            "message": {
                "query_graph": {
                    "nodes": {
                        "n0": {
                            "ids": ["MONDO:0021117"],
                            "categories": ["biolink:Disease"]
                        },
                        "n1": {
                            "categories": ["biolink:NamedThing"]
                        }
                    },
                    "edges": {
                        "e1": {
                            "subject": "n0",
                            "object": "n1",
                            "predicates": ["biolink:risk_affected_by"]
                        }
                    }
                }
            }
        }
    
    Returns:
        Dictionary containing the ARS response with fields like:
        - "pk": Primary key for tracking the query status
        - "fields": Contains query status, data, timestamp, etc.

    """
    # Validate that the query has the required "message" wrapper
    if "message" not in query:
        raise ValueError(
            "TRAPI query must be wrapped in a 'message' object. "
            "Expected format: {'message': {'query_graph': {...}}}"
        )
    
    if "query_graph" not in query["message"]:
        raise ValueError(
            "TRAPI message must contain a 'query_graph' object. "
            "Expected format: {'message': {'query_graph': {...}}}"
        )
    
    response = requests.post(ARS_SUBMIT_URL, json=query)
    response.raise_for_status()
    return response.json()


def get_trapi_status(pk: str) -> dict:
    """
    Check the status of a previously submitted TRAPI query by its primary key (pk).
    Returns the status payload as JSON.

    The ARS tracks status in the message endpoint response. Status can be:
    - "Running" - The query is still being processed
    - "Done" - The query is complete
    - "Error" - An error occurred during processing
    """
    url = ARS_RESULTS_URL_TEMPLATE.format(pk=pk)
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_trapi_results(pk: str) -> dict:
    """
    Retrieve the results of a completed TRAPI query by its primary key (pk).
    
    This endpoint fetches the full TRAPI response from the ARS, which includes:
    - query_graph: The original query that was submitted
    - knowledge_graph: All nodes and edges found across all ARAs
    - results: Array of result objects with node_bindings, analyses, and scores
    
    Args:
        pk: Primary key UUID returned from submit_trapi_query (e.g., "4d3c7605-47ff-4907-8082-9506abcf5a83")
    
    Returns:
        Dictionary with ARS response structure:
        {
            "model": "tr_ars.message",
            "pk": "4d3c7605-47ff-4907-8082-9506abcf5a83",
            "fields": {
                "status": "Done",  # Should be "Done" before calling this
                "data": {
                    "message": {
                        "query_graph": {...},      # Original query
                        "knowledge_graph": {...},  # All found nodes/edges
                        "results": [...]           # Array of answers with bindings and scores
                    }
                }
            }
        }
    
    Usage:
        # First check status until "Done"
        status = trapi_status(pk)
        if status["fields"]["status"] == "Done":
            results = get_trapi_results(pk)
            # Access the TRAPI message
            trapi_message = results["fields"]["data"]["message"]
            # Access individual results
            for result in trapi_message["results"]:
                # Each result has node_bindings, analyses, and normalized_score
                print(f"Score: {result['normalized_score']}")
    """
    url = ARS_RESULTS_URL_TEMPLATE.format(pk=pk)
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


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
