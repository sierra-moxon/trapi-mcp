# api_utilities.py
import requests

# Base URLs for Translator services
NAME_RESOLVER_URL = "https://name-resolution-sri.renci.org/lookup"
NODE_NORMALIZER_URL = "https://nodenormalization-sri.renci.org/1.5/get_normalized_nodes"
GENETICS_KP_URL = "https://genetics-kp.transltr.io/genetics_provider/trapi/v1.5/query"


def lookup_name(
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
    Wrapper around Name Resolver service to find entities by name or synonym.
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


def normalize_nodes(
    curies: list[str],
    conflate: bool = True,
    drug_chemical_conflate: bool = False,
    description: bool = False,
    individual_types: bool = False
) -> dict:
    """
    Wrapper around Node Normalizer service to return equivalent identifiers and semantic types for given CURIEs.

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


def genetics_kp(
    subject: str,
    object: str,
    predicate: str,
    subject_categories: list[str],
    object_categories: list[str],
    attributes: list[dict] | None = None,
    qualifiers: list[dict] | None = None,
    summary_only: bool = True,
    max_results: int = 20,
    min_score: float | None = None,
    max_score: float | None = None,
    min_publications: int | None = None,
    knowledge_level: str | None = None,
    agent_type: str | None = None
) -> dict:
    """
    Query the Genetics Knowledge Provider for genetic associations using TRAPI format.
    
    This tool queries genetic relationships between diseases, genes, cells, pathways, and phenotypic features.
    Immediately returns the complete TRAPI response including knowledge graph and results.
    
    Supported genetic associations:
    - Disease ↔ Gene (condition_associated_with_gene, gene_associated_with_condition)
    - Disease ↔ Cell (genetic_association)  
    - Disease ↔ Pathway (genetic_association)
    - Gene ↔ PhenotypicFeature (gene_associated_with_condition)
    - Cell ↔ PhenotypicFeature (genetic_association)
    - Pathway ↔ PhenotypicFeature (genetic_association)
    
    Args:
        subject: CURIE identifier for the subject node (e.g., "MONDO:0011936", "HGNC:6284")
        object: CURIE identifier for the object node, or leave empty for open query
        predicate: Biolink predicate - must be one of:
            - "biolink:condition_associated_with_gene"
            - "biolink:gene_associated_with_condition" 
            - "biolink:genetic_association"
        subject_categories: Biolink categories for subject node:
            - ["biolink:Disease"] for diseases
            - ["biolink:Gene"] for genes
            - ["biolink:Cell"] for cells
            - ["biolink:Pathway"] for pathways
            - ["biolink:PhenotypicFeature"] for phenotypic features
        object_categories: Biolink categories for object node (same options as subject)
        attributes: Optional list of edge attributes
        qualifiers: Optional list of edge qualifiers
        summary_only: If True (default), returns a condensed summary with key results only. 
                     If False, returns the full TRAPI response with all metadata.
        max_results: Maximum number of results to include (default 20). 
                    Helps manage response size for queries with many results.
        min_score: Minimum score threshold for edge filtering (e.g., 0.7)
        max_score: Maximum score threshold for edge filtering (e.g., 1.0)
        min_publications: Minimum number of publications supporting the association
        knowledge_level: Filter by knowledge level (e.g., "statistical_association", "prediction")
        agent_type: Filter by agent type (e.g., "data_analysis_pipeline", "manual_curation")
    
    Supported ID prefixes by category:
        - Disease: MONDO, EFO, UMLS, HP, NCIT, MESH, SNOMEDCT, DOID
        - Gene: NCBIGene, ENSEMBL, HGNC, OMIM, UMLS, UniProtKB
        - Cell: UBERON
        - Pathway: GO, REACT, BIOCARTA, KEGG, WP
        - PhenotypicFeature: MONDO, EFO, UMLS, HP, NCIT, MESH, SNOMEDCT, DOID
    
    Example usage:
        # Find genes associated with a disease
        result = genetics_kp(
            subject="MONDO:0011936",
            object="",  # Open query
            predicate="biolink:condition_associated_with_gene",
            subject_categories=["biolink:Disease"],
            object_categories=["biolink:Gene"]
        )
        
        # Find pathways genetically associated with a phenotype
        result = genetics_kp(
            subject="HP:0000729",
            object="",
            predicate="biolink:genetic_association", 
            subject_categories=["biolink:PhenotypicFeature"],
            object_categories=["biolink:Pathway"]
        )
        
        # Find high-confidence gene associations with score filtering
        result = genetics_kp(
            subject="MONDO:0005148",
            object="",
            predicate="biolink:condition_associated_with_gene",
            subject_categories=["biolink:Disease"],
            object_categories=["biolink:Gene"],
            min_score=0.8,  # Only associations with score >= 0.8
            knowledge_level="statistical_association"  # Only statistical associations
        )
    
    Returns:
        If summary_only=True: Condensed summary with key results
        If summary_only=False: Complete TRAPI response with all metadata
        
        Summary format includes:
        - total_results: Number of associations found
        - query_info: Original query details
        - top_results: List of top associations with scores
        - full_response_available: Indicates if full data can be requested
    """
    # Build TRAPI query message
    message: dict = {
        "message": {
            "query_graph": {
                "nodes": {
                    "n00": {
                        "categories": subject_categories
                    },
                    "n01": {
                        "categories": object_categories
                    }
                },
                "edges": {
                    "e00": {
                        "subject": "n00",
                        "object": "n01",
                        "predicates": [predicate]
                    }
                }
            }
        }
    }
    
    # Add IDs only if provided (for open queries, nodes have only categories)
    if subject:
        message["message"]["query_graph"]["nodes"]["n00"]["ids"] = [subject]
    if object:
        message["message"]["query_graph"]["nodes"]["n01"]["ids"] = [object]
    if attributes:
        message["message"]["query_graph"]["edges"]["e00"]["attributes"] = attributes
    if qualifiers:
        message["message"]["query_graph"]["edges"]["e00"]["qualifiers"] = qualifiers
    
    # Build attribute constraints according to TRAPI specification
    attribute_constraints = []
    
    if min_score is not None:
        attribute_constraints.append({
            "id": "biolink:score",
            "name": "Confidence Score",
            "operator": ">=",
            "value": min_score
        })
    
    if max_score is not None:
        attribute_constraints.append({
            "id": "biolink:score",
            "name": "Confidence Score", 
            "operator": "<=",
            "value": max_score
        })
    
    if min_publications is not None:
        attribute_constraints.append({
            "id": "biolink:publication_count",
            "name": "Publication Count",
            "operator": ">=", 
            "value": min_publications
        })
    
    if knowledge_level is not None:
        attribute_constraints.append({
            "id": "biolink:knowledge_level",
            "name": "Knowledge Level",
            "operator": "==",
            "value": knowledge_level
        })
    
    if agent_type is not None:
        attribute_constraints.append({
            "id": "biolink:agent_type", 
            "name": "Agent Type",
            "operator": "==",
            "value": agent_type
        })
    
    # Add attribute constraints to the edge if any are specified
    if attribute_constraints:
        message["message"]["query_graph"]["edges"]["e00"]["attribute_constraints"] = attribute_constraints
    
    # Get the full response
    full_response = genetics_kp_query(message)
    
    # Return full response if summary_only is False
    if not summary_only:
        return full_response
    
    # Create a summary
    try:
        results = full_response.get("message", {}).get("results", [])
        knowledge_graph = full_response.get("message", {}).get("knowledge_graph", {})
        
        # Limit results and extract key information
        limited_results = results[:max_results]
        
        # Extract gene/node information with scores
        summary_results = []
        for result in limited_results:
            # Get the target node ID (n01)
            target_bindings = result.get("node_bindings", {}).get("n01", [])
            if target_bindings:
                target_id = target_bindings[0].get("id", "")
                
                # Get the score from analyses
                analyses = result.get("analyses", [])
                score = None
                if analyses:
                    score = analyses[0].get("score", 0)
                
                # Get edge information for additional context
                edge_bindings = result.get("analyses", [{}])[0].get("edge_bindings", {}).get("e00", [])
                edge_id = edge_bindings[0].get("id", "") if edge_bindings else ""
                
                # Look up edge attributes in knowledge graph for additional score info
                edge_info = knowledge_graph.get("edges", {}).get(edge_id, {})
                edge_attributes = edge_info.get("attributes", [])
                edge_score = None
                for attr in edge_attributes:
                    if attr.get("attribute_type_id") == "biolink:score":
                        edge_score = attr.get("value")
                        break
                
                summary_results.append({
                    "target_id": target_id,
                    "analysis_score": score,
                    "edge_score": edge_score,
                    "edge_id": edge_id
                })
        
        # Build applied constraints info for transparency
        applied_constraints = {}
        if min_score is not None:
            applied_constraints["min_score"] = min_score
        if max_score is not None:
            applied_constraints["max_score"] = max_score
        if min_publications is not None:
            applied_constraints["min_publications"] = min_publications
        if knowledge_level is not None:
            applied_constraints["knowledge_level"] = knowledge_level
        if agent_type is not None:
            applied_constraints["agent_type"] = agent_type
        
        return {
            "query_info": {
                "subject": subject,
                "object": object or "open_query",
                "predicate": predicate,
                "subject_categories": subject_categories,
                "object_categories": object_categories
            },
            "applied_constraints": applied_constraints if applied_constraints else "No filtering constraints applied",
            "constraint_details": {
                "description": "Results were filtered using TRAPI attribute constraints",
                "available_constraints": {
                    "min_score": "Minimum confidence score (0-1)",
                    "max_score": "Maximum confidence score (0-1)", 
                    "min_publications": "Minimum supporting publications",
                    "knowledge_level": "Required knowledge level (e.g., statistical_association)",
                    "agent_type": "Required agent type (e.g., data_analysis_pipeline)"
                }
            } if applied_constraints else None,
            "total_results": len(results),
            "results_shown": len(summary_results),
            "top_results": summary_results,
            "status": full_response.get("status", "Unknown"),
            "description": full_response.get("description", ""),
            "full_response_available": "Set summary_only=False to get complete TRAPI response with all metadata"
        }
        
    except Exception as e:
        # If summarization fails, return the original response with a note
        return {
            "error": f"Failed to create summary: {str(e)}",
            "full_response": full_response,
            "note": "Summary creation failed, returning full response"
        }
