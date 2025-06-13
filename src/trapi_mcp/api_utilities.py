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
    """
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
    Returns the results payload as JSON.
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
