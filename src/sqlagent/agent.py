from .config import CHAT_MODEL, MAX_STEPS
from .tools import Toolbox

SYSTEM_PROMPT = (
    "You are a data analyst. Answer the user's question about the shop database "
    "using the available tools. Inspect the schema when unsure, write correct "
    "SQLite queries and base every figure on tool results. Be concise."
)


class SQLAgent:
    def __init__(self, model=CHAT_MODEL, max_steps=MAX_STEPS, db_path=None):
        import anthropic

        self.client = anthropic.Anthropic()
        self.model = model
        self.max_steps = max_steps
        self.toolbox = Toolbox(db_path) if db_path else Toolbox()

    def run(self, question, verbose=False):
        messages = [{"role": "user", "content": question}]
        for _ in range(self.max_steps):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=Toolbox.DEFINITIONS,
                messages=messages,
            )
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason != "tool_use":
                return "".join(block.text for block in response.content if block.type == "text")

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    if verbose:
                        print(f"  -> {block.name}({block.input})")
                    output = self.toolbox.execute(block.name, block.input)
                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": block.id, "content": output}
                    )
            messages.append({"role": "user", "content": tool_results})

        return "Stopped: reached the maximum number of tool-use steps."
