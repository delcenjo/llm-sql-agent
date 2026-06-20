import argparse
import os

from dotenv import load_dotenv


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Ask the SQL agent a question")
    parser.add_argument("question", nargs="?", help="natural-language question")
    parser.add_argument("--verbose", action="store_true", help="print each tool call")
    args = parser.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY (see .env.example) to run the agent.")
        return

    from .agent import SQLAgent

    question = args.question or input("Question: ")
    print(SQLAgent().run(question, verbose=args.verbose))


if __name__ == "__main__":
    main()
