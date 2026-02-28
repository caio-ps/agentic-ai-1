from src.agents.manager import ManagerAgent
from src.core.llm import LLM


def main() -> None:
    llm = LLM()
    manager = ManagerAgent(llm=llm)
    requirement = "Build a simple portfolio website"
    response = manager.run(requirement)
    print(response)


if __name__ == "__main__":
    main()
