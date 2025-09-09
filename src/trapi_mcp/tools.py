# tools.py
from typing import List, Dict, Any
from .api_utilities import (
    name_resolver,
    node_normalizer,
    genetics_kp_query
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


def genetics_kp(
    subject: str,
    object: str,
    predicate: str,
    subject_categories: List[str],
    object_categories: List[str],
    attributes: List[Dict[str, Any]] = None,
    qualifiers: List[Dict[str, Any]] = None,
    summary_only: bool = True,
    max_results: int = 20,
    min_score: float = None,
    max_score: float = None,
    min_publications: int = None,
    knowledge_level: str = None,
    agent_type: str = None
) -> Dict[str, Any]:
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
    message: Dict[str, Any] = {
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
