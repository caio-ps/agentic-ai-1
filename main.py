from src.core.orchestration import Orchestrator


def main() -> None:
    orchestrator = Orchestrator()
    user_input = input("Enter your website requirement: ").strip()
    result = orchestrator.run(user_input)
    print("\n" + "=" * 50)
    print("FINAL RESULT")
    print("=" * 50)
    print(result)


if __name__ == "__main__":
    main()
