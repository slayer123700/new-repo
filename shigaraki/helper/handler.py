from telegram.ext import CommandHandler
from telegram import Update
from typing import Optional, Union, Collection
from config import config
from telethon import events
from shigaraki import telebot

class MultiCommandHandler(CommandHandler):
    """
    Extended CommandHandler to support multiple prefixes ('/', '!', '.', '&') by default.
    """

    def __init__(
        self,
        command: Union[str, Collection[str]],
        callback,
        filters=None,
        block: bool = True,
        has_args: Optional[Union[bool, int]] = None,
    ):
        super().__init__(command, callback, filters=filters, block=block)

    def check_update(
        self, update: object
    ) -> Optional[Union[bool, tuple[list[str], Optional[Union[bool, dict]]]]]:
        """Override check_update to support multiple prefixes."""
        if isinstance(update, Update) and update.effective_message:
            message = update.effective_message

            if message.text and len(message.text) > 1:
                # Extract the first word (the command) from the message
                fst_word = message.text.split(None, 1)[0]

                # Check if the first word starts with any of the defined prefixes
                if len(fst_word) > 1 and any(fst_word.startswith(start) for start in config.CMD_STARTERS):
                    # Extract the command name (remove the prefix)
                    command = fst_word[1:].split("@")
                    command.append(message.get_bot().username)
                    args = message.text.split()[1:]

                    # Validate the command
                    if not (
                        command[0].lower() in self.commands
                        and command[1].lower() == message.get_bot().username.lower()
                    ):
                        return None

                    # Check argument rules
                    if not self._check_correct_args(args):
                        return None

                    # Apply filters if provided
                    filter_result = self.filters.check_update(update)
                    if filter_result:
                        return args, filter_result
                    return False
        return None


def register(**args):
    """Registers a new message with multiple command prefixes."""
    pattern = args.get("pattern")
    
    # Create a regex pattern that matches any character in CMD_STARTERS
    r_pattern = f"^[{config.CMD_STARTERS}]"

    # Add case-insensitive flag if not already present
    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = f"(?i){pattern}"

    # Replace the initial ^/ with the custom prefix pattern
    if pattern:
        args["pattern"] = pattern.replace("^/", r_pattern, 1)

    def decorator(func):
        telebot.add_event_handler(func, events.NewMessage(**args))
        return func

    return decorator