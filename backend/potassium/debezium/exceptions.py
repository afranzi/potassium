from typing import Optional


class KafkaConnectAPIError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(f"{message} [Status: {status_code}]")


class ResponseParsingError(KafkaConnectAPIError):
    pass


class ConnectorFailedStateError(Exception):
    def __init__(self, connector: str, task_errors: list[str], restart_connectors: bool):
        self.connector = connector
        self.task_errors = "\n\t".join(task_errors) if task_errors else "Unknown error"
        self.restart_connectors = "Restarting it automatically" if restart_connectors else "Please restart it manually"

        super().__init__(f"Connector {connector} is in FAILED state. {self.restart_connectors}\n{self.task_errors}")


def extract_root_cause_message(stack_trace: str) -> str:
    """
    Parses a Java stack trace to extract the root exception message and
    the primary "Caused by" message for a more complete error summary.
    """
    root_message_lines = []
    cause_message_lines = []

    # We use a state to track whether we are parsing the root or the 'Caused by' part.
    parsing_mode = "root"

    for line in stack_trace.splitlines():
        cleaned_line = line.strip()
        if not cleaned_line:
            continue

        if cleaned_line.startswith("Caused by:"):
            parsing_mode = "cause"
            cause_message_lines.append(cleaned_line)
            continue  # Move to the next line

        if cleaned_line.startswith("at ") or cleaned_line.startswith("..."):
            if parsing_mode == "cause":
                break
            continue

        if parsing_mode == "root":
            root_message_lines.append(cleaned_line)
        elif parsing_mode == "cause":
            cause_message_lines.append(cleaned_line)

    root_message = " ".join(root_message_lines).strip().removesuffix(":")

    if not cause_message_lines:
        return root_message
    else:
        # Join the 'Caused by' lines and format it nicely.
        cause_message = " ".join(cause_message_lines).strip().replace("Caused by: ", "")
        return f"{root_message} (Caused by: {cause_message})"
