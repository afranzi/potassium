import sys
import traceback

from apprise import Apprise, NotifyType
from loguru import logger

from potassium.config.secrets.settings import SecretSettings


class SlackSecret(SecretSettings):
    hook: str
    max_slack_body: int = 20000


def integrate_slack_notifier(secret_name: str) -> None:
    notifier = Apprise()
    slack_secret = SlackSecret(secret_name=secret_name)

    notifier.add(slack_secret.hook)

    def apprise_on_error(message):
        record = message.record

        fn, ln = record["file"].name, record["line"]
        title = f"Error in {fn}:{ln}"
        body = f"{record['message']}"

        exc = record["exception"]
        if exc:
            ex_type = exc.type.__name__
            title = f"{ex_type} in {fn}:{ln}"
            tb_list = traceback.format_exception(exc.type, exc.value, exc.traceback)
            tb_str = "".join(tb_list).rstrip()
            body = f"{record['message']}\n\n{tb_str}"

        if len(body) > slack_secret.max_slack_body:
            body = body[: slack_secret.max_slack_body - 15] + "\n...[truncated]"
        body = f"```{body}```"

        notifier.notify(title=title, body=body, notify_type=NotifyType.FAILURE)

        logger.add(apprise_on_error, level="ERROR", filter={"apprise": False})


def init_logs(verbose: bool = False, slack_secret: str | None = None) -> None:
    logger.remove()
    logger.add(sys.stdout, level="DEBUG" if verbose else "INFO")

    if slack_secret:
        integrate_slack_notifier(secret_name=slack_secret)
