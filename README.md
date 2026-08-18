# Crow (crow-bot.py)

A simple Discord bot for playing local music files (.mp3, .flac, .wav) in voice. Uses a standard queue system for playing music, with basic playback controls (play/pause, skipping, shuffling and stopping). The bot also displays song metadata for music it is playing.

## Concepts

What makes Crow different from other music bots is that it revolves around "albums", i.e. folders with music files in them. Rather than just adding files one at a time, you can add a whole "album" of files to the song queue at once.

In Crow's config file, you add albums by giving each a name and a path to a folder somewhere in your system. This way, you can refer to an album by whatever name you gave it in the config rather than a path to the directory. Albums can also be added en masse by specifying a "collection", a folder which contains many albums.

## Setup

This setup guide assumes you already have a Discord bot made via Discord's developer portal and added to your server. For which privileged gateway intents to turn on, only "Message Content" needs to be enabled.

### Requirements

**This bot requires Python 3.8 or higher.**

Assuming you're in a Linux environment, install the following dependencies:
- libffi
- libnacl
- python3-dev

For a Debian-based system, this command should work:
```bash
sudo apt install libffi-dev libnacl-dev python3-dev
```

Create a Python virtual environment in Crow's directory. This is recommended to avoid conflicts with different versions of Python libraries installed system-wide. Python will yell at you if you don't do this :)
```bash
cd /path/to/crow
python3 -m venv .venv
```

Activate the virtual environement, and install the required libraries using `pip`.
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Running the Bot

You must make a config file named `config.yml` in Crow's directory for the bot to run. Refer to `config.example.yml` to see an example.

Config options:
- `token` (required)
    - Your Discord bot's token, wrapped in quotes.
- `prefix` (required)
    - The command prefix to use for all bot commands. (e.g. '~' -> '~play')
- `owners`
    - A list of user IDs that are the "owners" of Crow, i.e. who is allowed to shut down the bot using the `quit` command.
- `channels`
    - A list of text channel IDs that Crow is allowed to listen to for commands.
- `albums`
    - A list of albums to add to Crow's album list. Each entry must contain a name and the path to the album's directory.
- `collections`
    - A list of folders containing folders that contain music files. Each folder inside a collection is treated as an 'album' and added to Crow's album list.
        - The name of each album added from a collection is the name of the directory.
        - e.g. the folder '/path/to/collection/my-album' is named 'my-album' in the album list.
- `log`
    - A file to output to for logging. Set this option as an empty string ('') if you don't want a log file.

Once you have the bot configured, you can run it using the following. (Note: ensure the virtual environment is activated before running.)
```bash
python3 run.py
```

You can also use the Bash scripts included in the repo (`start.sh` and `stop.sh`) to start and stop the bot in the background.

#### Running as a service

If you'd like, you can run Crow as a systemd service which runs in the background and can be started/stopped using `systemctl`.

Create a service file with the path `/etc/systemd/system/crow.service`. Place the following text into the file, replacing `</path/to/crow>` and `<username>` with the path to Crow's directory and your username respectively.
```
[Unit]
Description=Crow
After=network.target

[Service]
Type=simple
ExecStart=</path/to/crow/>.venv/bin/python3 run.py
User=<username>
WorkingDirectory=</path/to/crow>

[Install]
WantedBy=multi-user.target
```

This is just an example service file. You can configure this further if you'd like.

You can start/stop using the following commands:
```bash
sudo systemctl start crow
sudo systemctl stop crow
```

If you want the bot to start on server boot, then run the following:
```bash
sudo systemctl enable crow
```

## Commands

Below is a list of Crow's commands for reference. Some commands have shorter aliases which can be used instead. Some may also take required arguments (marked with `<>`) and/or optional arguments (marked with `[]`).

### Album-related

- `albums`:
    - Prints a list of all of Crow's albums.
- `list <album_name> [-n | -t]`:
    - Lists all the songs in the album "album_name".
    - With no optional arguments, it lists the songs' filenames alphabetically.
    - Adding `-n` or `-t` outputs the songs in a numbered list along with track length for each. Unlike `-n`, `-t` lists track metadata instead of filenames (e.g. "Artist - Title").

### Player

Crow will automatically connect to the voice channel you're in (if it isn't there already) when any "play"-like command is invoked.

- `nowplaying` (alias `np`):
    - Shows what song is currently playing, including its track metadata (title, artist, album, and cover art) and how far the player is into the song.
- `pause`:
    - Pauses playback.
- `play <filepath>` (alias `p`):
    - Add a song to the queue using its absolute filepath.
- `playalbum <album_name> [-s]` (alias `pa`):
    - Adds all songs in the album "album_name" to the queue.
    - Adding `-s` will shuffle the songs before inserting them into the queue.
- `playtrack <album_name> <index>` (alias `pt`):
    - Adds a song from the album "album_name" with the given index number to the queue.
    - Use `list <album_name> -n` to get the index number of the song you want before using this command.
- `queue` (alias `q`):
    - Prints a numbered list of all the songs currently in the queue.
- `resume`:
    - Resumes playback.
- `shuffle`:
    - Shuffles the songs in the queue.
- `skip [index]`:
    - Skips to the next track in the queue.
    - If an index number is given, the player skips to that track in the queue instead.
- `stop`:
    - Clears all songs in the queue, and disconnects the bot from the voice channel.

### Misc

- `caw`:
    - Caw!
- `help`:
    - Shows all the commands and provides usage information for each.
- `nyon`:
    - Nyon!
- `quit`:
    - Shuts down the bot. This is only usable by "owners".
