#!/usr/bin/env python3

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import lmstudio as lms
import requests
from rich.console import Console

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass
class Agent:
    system_prompt: str = "You are a helpful assistant."
    model: str = "qwen3.6"
    base_url: str = "http://127.0.0.1:1234/v1"
    api_key: str = field(default="NO_API_KEY", repr=False)
    contexts: dict[str, Callable[[], str]] = field(default_factory=dict)
    messages: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")

    def context(self, func: Callable[[], str]) -> Callable[[], str]:
        self.contexts[func.__name__] = func
        return func

    def chat(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})
        context_content = "\n\n".join(
            f"<context>\n<{n}>{fn()}</{n}>\n</content>"
            for n, fn in self.contexts.items()
        )

        prefix: list[dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "system", "content": context_content},
        ]

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        req = requests.post(
            url,
            headers=headers,
            json={"model": self.model, "messages": prefix + self.messages},
            timeout=300,
        )
        req.raise_for_status()
        data = req.json()

        choices = data.get("choices")
        if not choices:
            raise RuntimeError

        message = choices[0].get("message")
        if message is None:
            raise RuntimeError

        response = message.get("content") or ""
        self.messages.append({"role": "assistant", "content": response})
        return response


def main() -> None:
    agent = Agent(system_prompt="End every message with a yo mama joke.")
    console = Console()

    while True:
        console.print("[green]You:[/green] ", end="")
        user_input = console.input()

        if user_input.strip().lower() in ("quit", "exit"):
            console.print("[dim]Goodbye![/dim]")
            return

        with console.status("[dim]Thinking...[/dim]", spinner="arc"):
            response = agent.chat(user_input).strip()

        console.print(f"[blue]Assistant:[/blue] {response}")


if __name__ == "__main__":
    main()
