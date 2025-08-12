# tricount-tsv-downloder: download TSV raw data from Tricount
# Copyright (C)  2025  Stefano Taverni
#
# This file is part of tricount-tsv-downloader.
# tricount-tsv-downloader is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
    CommandHandler,
)
import re
from downloader import (
    TricountAPI,
    get_tricount_title,
    parse_tricount_data,
    write_to_tsv,
)


logger = logging.getLogger(__name__)

URL_REGEX = re.compile(r".*(https?://tricount\.com/[a-zA-Z0-9]+).*")
tricount_client = None


LICENSE_NOTICE = """
This bot is free software. The code is released under the GNU Affero General
Public License. You can view license at https://www.gnu.org/licenses/.

To view its source code, just send the /source command to this bot.
""".strip()

START_MESSAGE = """
Hi! This bot processes a Tricount link to get raw data and creates a TSV file
for you! Just send a message with the Tricount link in it. The bot will take
care of everything

To check the code license, use the /license command.
To see the source code, use /source command.
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=START_MESSAGE,
    )


def _get_csv(tricount_key):
    global tricount_client
    if tricount_client is None:
        logger.info("connecting to API")
        tricount_client = TricountAPI()
    tricount_client.authenticate()
    logger.info("fetching data")
    data = tricount_client.fetch_tricount_data(tricount_key)
    tricount_title = get_tricount_title(data)
    transactions = parse_tricount_data(data)
    destination = tricount_title.replace(" ", "_")
    logger.info("writing csv")
    destination = write_to_tsv(transactions, file_name=destination)
    return destination


async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    print(text)
    # Extract URL.
    try:
        if match_ := URL_REGEX.match(text):
            logger.info("found tricount link")
            assert len(match_.groups()) > 0
            tricount_url = match_.groups()[0]
            tricount_key = tricount_url.split("/")[-1]
            response = tricount_key
            file = _get_csv(tricount_key)
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=open(file, "rb"),
                caption=file,
            )
        else:
            logger.error("no tricout link found")
            response = "Can't find tricount url in text!"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=response,
            )
    except Exception as e:
        logger.error(f"Exception: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Internal error: {e}",
        )


async def license(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=LICENSE_NOTICE,
    )


async def source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Source code available at https://github.com/Stefano-t/tricount-tsv-downloader",
    )


def main() -> None:
    application = ApplicationBuilder().token(open("./token").read().strip()).build()

    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("license", license))
    application.add_handler(CommandHandler("source", source))

    application.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), downloader)
    )

    application.run_polling()


if __name__ == "__main__":
    main()
