import pytest
import requests
from src.trapi_mcp.tools import genetics_kp


class TestGeneticsKP:
    """Integration tests for the genetics_kp tool functionality with real API calls."""
    
    def test_genetics_kp_diabetes_genes_basic_query(self):
        """Test the original large diabetes-gene query with summary enabled by default."""
        result = genetics_kp(
            subject="MONDO:0005148",  # Type 2 diabetes mellitus
            object="",  # Open query - find any genes
            predicate="biolink:condition_associated_with_gene", 
            subject_categories=["biolink:Disease"],
            object_categories=["biolink:Gene"]
        )
        
        # Check basic response structure
        assert isinstance(result, dict)
        assert "query_info" in result
        assert "applied_constraints" in result
        assert "total_results" in result
        assert "results_shown" in result
        assert "top_results" in result
        assert "status" in result
        
        # Verify query info
        assert result["query_info"]["subject"] == "MONDO:0005148"
        assert result["query_info"]["object"] == "open_query"
        assert result["query_info"]["predicate"] == "biolink:condition_associated_with_gene"
        assert result["query_info"]["subject_categories"] == ["biolink:Disease"]
        assert result["query_info"]["object_categories"] == ["biolink:Gene"]
        
        # Verify no constraints were applied
        assert result["applied_constraints"] == "No filtering constraints applied"
        assert result["constraint_details"] is None
        
        # Verify we got results (diabetes should have many gene associations)
        assert result["status"] == "Success"
        assert result["total_results"] > 0
        assert result["results_shown"] > 0
        assert len(result["top_results"]) > 0
        
        # Check individual result structure
        first_result = result["top_results"][0]
        assert "target_id" in first_result
        assert "analysis_score" in first_result
        assert "edge_score" in first_result
        assert first_result["target_id"].startswith("NCBIGene:")
        
        # Verify results are limited to default max_results (20)
        assert result["results_shown"] <= 20
        
        print(f"Basic query returned {result['total_results']} total results, showing {result['results_shown']}")

    def test_genetics_kp_with_score_filtering(self):
        """Test genetics_kp query with score filtering constraints."""
        result = genetics_kp(
            subject="MONDO:0005148",  # Type 2 diabetes mellitus
            object="",
            predicate="biolink:condition_associated_with_gene",
            subject_categories=["biolink:Disease"], 
            object_categories=["biolink:Gene"],
            min_score=0.8,  # Only high-confidence associations
            max_results=10
        )
        
        # Check that applied constraints are documented in response
        assert "applied_constraints" in result
        assert isinstance(result["applied_constraints"], dict)
        assert abs(result["applied_constraints"]["min_score"] - 0.8) < 0.001
        
        # Check constraint details are provided
        assert result["constraint_details"] is not None
        assert "description" in result["constraint_details"]
        assert "available_constraints" in result["constraint_details"]
        
        # Verify available constraints documentation
        available = result["constraint_details"]["available_constraints"]
        assert "min_score" in available
        assert "knowledge_level" in available
        assert "agent_type" in available
        
        # Verify filtering worked (should have fewer results than unfiltered)
        assert result["status"] == "Success"
        assert result["results_shown"] <= 10  # Respects max_results
        
        # Check that returned results have high scores
        for gene_result in result["top_results"]:
            if gene_result["edge_score"] is not None:
                assert gene_result["edge_score"] >= 0.8, (
                    f"Gene {gene_result['target_id']} has score {gene_result['edge_score']} < 0.8"
                )
        
        print(f"Filtered query (min_score=0.8) returned {result['total_results']} total results, "
              f"showing {result['results_shown']}")

    def test_genetics_kp_with_knowledge_level_filtering(self):
        """Test genetics_kp with knowledge level filtering."""
        result = genetics_kp(
            subject="MONDO:0005148",
            object="",
            predicate="biolink:condition_associated_with_gene",
            subject_categories=["biolink:Disease"],
            object_categories=["biolink:Gene"],
            knowledge_level="statistical_association",
            max_results=5
        )
        
        # Check constraints are documented
        assert result["applied_constraints"]["knowledge_level"] == "statistical_association"
        assert result["constraint_details"] is not None
        
        # Should still return results
        assert result["status"] == "Success"
        assert result["results_shown"] <= 5
        
        print(f"Knowledge level filtered query returned {result['total_results']} total results")

    def test_genetics_kp_full_response_mode(self):
        """Test genetics_kp returns full TRAPI response when summary_only=False."""
        result = genetics_kp(
            subject="MONDO:0005148",
            object="",
            predicate="biolink:condition_associated_with_gene",
            subject_categories=["biolink:Disease"],
            object_categories=["biolink:Gene"],
            summary_only=False,
            min_score=0.9,  # High filter to reduce response size
            max_results=5   # Limit results for faster test
        )
        
        # Should return the full TRAPI response structure
        assert "message" in result
        assert "query_graph" in result["message"]
        assert "knowledge_graph" in result["message"]
        assert "results" in result["message"]
        assert "status" in result
        assert "biolink_version" in result
        
        # Verify it's a proper TRAPI response
        kg = result["message"]["knowledge_graph"]
        assert "nodes" in kg
        assert "edges" in kg
        
        results = result["message"]["results"]
        assert len(results) <= 5
        
        print(f"Full response mode returned complete TRAPI response with {len(results)} results")

    def test_genetics_kp_multiple_constraints(self):
        """Test genetics_kp with multiple filtering constraints combined."""
        result = genetics_kp(
            subject="MONDO:0005148",
            object="",
            predicate="biolink:condition_associated_with_gene",
            subject_categories=["biolink:Disease"],
            object_categories=["biolink:Gene"],
            min_score=0.7,
            knowledge_level="statistical_association",
            agent_type="data_analysis_pipeline",
            max_results=8
        )
        
        # Verify all constraints are documented
        applied = result["applied_constraints"]
        assert abs(applied["min_score"] - 0.7) < 0.001
        assert applied["knowledge_level"] == "statistical_association"
        assert applied["agent_type"] == "data_analysis_pipeline"
        
        # Should still return some results
        assert result["status"] == "Success"
        assert result["results_shown"] <= 8
        
        print(f"Multi-constraint query returned {result['total_results']} total results, "
              f"showing {result['results_shown']}")

    def test_genetics_kp_phenotype_to_genes(self):
        """Test a different query type: phenotype to genes."""
        result = genetics_kp(
            subject="HP:0000729",  # Autistic behavior
            object="",
            predicate="biolink:genetic_association",
            subject_categories=["biolink:PhenotypicFeature"],
            object_categories=["biolink:Gene"],
            max_results=5
        )
        
        # Verify query worked
        assert result["status"] == "Success"
        assert result["query_info"]["predicate"] == "biolink:genetic_association"
        assert result["query_info"]["subject_categories"] == ["biolink:PhenotypicFeature"]
        assert result["query_info"]["object_categories"] == ["biolink:Gene"]
        
        print(f"Phenotype-gene query returned {result['total_results']} total results")

    @pytest.mark.skip(reason="Slow test - only run when needed")
    def test_genetics_kp_large_unfiltered_query(self):
        """Test the original problematic large query to verify it's now manageable."""
        result = genetics_kp(
            subject="MONDO:0005148",
            object="",
            predicate="biolink:condition_associated_with_gene",
            subject_categories=["biolink:Disease"],
            object_categories=["biolink:Gene"],
            summary_only=True,  # This should make it manageable
            max_results=50      # Increase limit to see more results
        )
        
        # This should now be manageable even with many results
        assert result["status"] == "Success"
        assert result["total_results"] > 100  # Should be the large result set
        assert result["results_shown"] <= 50  # But limited in summary
        
        print(f"Large query returned {result['total_results']} total results but only showed "
              f"{result['results_shown']} - response size is manageable")


if __name__ == "__main__":
    pytest.main([__file__])