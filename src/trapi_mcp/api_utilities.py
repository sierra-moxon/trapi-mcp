"""TRAPI MCP API Utilities"""

import requests

# Base URLs for the ARS (Automated Relay System)
ARS_SUBMIT_URL = "https://ars-prod.transltr.io/ars/api/submit"
ARS_STATUS_URL_TEMPLATE = "https://ars-prod.transltr.io/ars/api/status/{pk}"
ARS_RESULTS_URL_TEMPLATE = "https://ars-prod.transltr.io/ars/api/results/{pk}"


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
    """
    url = ARS_STATUS_URL_TEMPLATE.format(pk=pk)
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