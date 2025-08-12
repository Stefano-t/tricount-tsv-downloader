# Tricount API to TSV

**NOTE**: this project is a fork of [https://github.com/MrNachoX/tricount-downloader], forked in August, 9, 2025.
The core remains mostly the same, but with enhancements and fixes.

LINK TO ORIGINAL README: [https://github.com/MrNachoX/tricount-downloader/blob/main/README.md].

----------

# Installation

This project requires python >= 3.9. Install dependencies inside a virtualenv like so:
```bash
python3 -m venv venv
source venv/bin/activate  # or activate.fish, or activate.zsh
pip install -r requirements.txt
```


# Usage

This project can be used in two ways.

## Stand-alone application

After installing required dependencies, you can download a TSV of your Tricount using the `main.py` script.
First of all, you need to retrieve you Tricount project key.
Just share the Tricount in a chat or your notes to get the http link.
The key is the last part of the URL, that is, `https://tricount.com/<your_tricount_key>`.

Once we have the key, you can run the script like:

```bash
./main.py <your_tricount_key>
```

This will download a TSV file in the same directory where the script lives.
The name of the TSV file is the name of the Tricount.

If you want to get raw data in json format, supply the `--raw` flag.

To get more information about the program, add the `--help` flag.

## Telegram Bot

The same functionalities are available as Telegram bot.
The bot is called /Tricount Downloader/, and the bot username is `@tricount_download_bot`.

The usage is pretty simple: just share the Tricount invite with this bot.
It will download and attach the TSV file in the chat.

> **WARNING**
>
> Currently, I do not have a server to run this bot. This means that you will
> likely find the bot unavailable. I do not plan to have a fully functional
> server in the near future. Therefore, you can either use the stand-alone
> version of this code or you are free to deploy your own instance of this bot.


# Author

- Stefano Taverni
- [Ignacio Muñoz MrNachoX](https://github.com/MrNachoX) (original author)


# License

The original code came with no licence at all.
All new code is licenced under the [AGPL-3.0-or-later](./COPYING) licence.
