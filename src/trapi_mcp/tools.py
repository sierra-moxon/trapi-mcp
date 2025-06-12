"""basic TRAPI tools for MCP)"""

from typing import List, Dict, Any
from api_utilities import submit_trapi_query, get_trapi_status, get_trapi_results


def trapi(subject: str,
          object_: str,
          predicate: str,
          attributes: List[Dict[str, Any]] = None,
          qualifiers: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Build a simple TRAPI query graph for a single edge between subject and object,
    submit it to the ARS, and return the submission response (including pk).

    Parameters:
        subject: CURIE for the subject node (e.g., "PUBCHEM.COMPOUND:644073").
        object_: CURIE for the object node (e.g., "HP:0000217").
        predicate: Biolink predicate CURIE (e.g., "biolink:related_to").
        attributes: Optional list of TRAPI attribute objects for the edge.
        qualifiers: Optional list of TRAPI qualifier objects for the edge.

    Returns:
        The raw JSON response from the ARS upon submission.
    """
    # Construct the TRAPI message
    message = {
        "message": {
            "query_graph": {
                "nodes": {
                    "n0": {"ids": [subject]},
                    "n1": {"ids": [object_]}
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

    # Attach attributes and qualifiers if provided
    if attributes:
        message["message"]["query_graph"]["edges"]["e0"]["attributes"] = attributes
    if qualifiers:
        message["message"]["query_graph"]["edges"]["e0"]["qualifiers"] = qualifiers

    # Submit to ARS
    submission_response = submit_trapi_query(message)
    return submission_response


def trapi_status(pk: str) -> Dict[str, Any]:
    """
    Wrapper to check the status of a TRAPI job.

    Parameters:
        pk: Primary key returned by trapi().
    Returns:
        Status JSON payload.
    """
    return get_trapi_status(pk)


def trapi_results(pk: str) -> Dict[str, Any]:
    """
    Wrapper to fetch results of a completed TRAPI job.

    Parameters:
        pk: Primary key returned by trapi().
    Returns:
        Results JSON payload.
    """
    return get_trapi_results(pk)



