from src.core.orchestration.orchestrator import Orchestrator
from src.core.mock_llm import MockLLM


def test_orchestrator_runs_full_pipeline_with_mocked_dependencies(
    monkeypatch,
    tmp_path,
    product_requirements_output: str,
    research_scope_output: str,
    strategic_queries_output: str,
    knowledge_queries_output: str,
    research_output_json: str,
    site_structure_json: str,
    architecture_spec_json: str,
    design_spec_json: str,
    development_tasks_json: str,
    generated_files_json: str,
    qa_approved_feedback: str,
    devops_output: str,
    fake_web_search_service,
    fake_image_generator_factory,
) -> None:
    llm = MockLLM(
        {
            "product_manager": [product_requirements_output],
            "researcher.extract_scope": [research_scope_output],
            "researcher.strategic_queries": [strategic_queries_output],
            "researcher.knowledge_queries": [knowledge_queries_output],
            "researcher": [research_output_json],
            "content_designer": [site_structure_json],
            "architect": [architecture_spec_json],
            "designer": [design_spec_json],
            "planner": [development_tasks_json],
            "developer": [generated_files_json],
            "qa": [qa_approved_feedback],
            "devops": [devops_output],
        }
    )

    monkeypatch.setattr(
        "src.core.orchestration.orchestrator.ImageGenerator",
        fake_image_generator_factory,
    )
    monkeypatch.chdir(tmp_path)

    orchestrator = Orchestrator(llm=llm)
    orchestrator.researcher.web_search_service = fake_web_search_service

    result = orchestrator.run("Build a cryptocurrency education website")

    assert "Deployment instructions" in result
    assert (tmp_path / "workspace" / "index.html").exists()
    assert (tmp_path / "workspace" / "assets" / "images" / "hero.png").exists()
    assert fake_web_search_service.queries
    assert fake_image_generator_factory.instances[0].prompts
