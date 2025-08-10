import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
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


def main() -> None:
    application = ApplicationBuilder().token(open("./token").read().strip()).build()

    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), downloader))

    application.run_polling()


if __name__ == "__main__":
    main()
