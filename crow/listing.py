import discord
import math
import os
from .song import Song

def max_length(strings):
    return max(len(x) for x in strings)

async def add_to_msg_list(msg, msg_list, ctx):
    if len(msg) + len(msg_list) > 1997:
        msg_list += "```"
        await ctx.send(msg_list)
        msg_list = f"```\n{msg}"
    else:
        msg_list += msg
    return msg_list

async def list_ls_format(list_title, items, ctx):
    msg_list = f"```\n{list_title}:\n\n"
    longest = max_length(items)
    padded_items = [ i.ljust(longest) for i in items ]
    colwidth = longest + 1
    items_per_line = 98 // colwidth

    # this happens if a filename is long. if so, just list it normal, there may be text wrap
    if items_per_line == 0:
        items_per_line = 1

    items_per_col = math.ceil(len(padded_items) / items_per_line)
    
    for i in range(items_per_col):
        line = ""
        for j in range(items_per_line):
            index = i + (j * items_per_col)

            if index >= len(padded_items):
                break
            else:
                line += f"{padded_items[index]} "
        msg_list = await add_to_msg_list(f"{line}\n", msg_list, ctx)

    msg_list += "```"
    await ctx.send(msg_list)

async def list_songs_format(list_title, songs, list_filenames, ctx):
    msg_list = f"```\n{list_title}\n\n"
    for i, song in enumerate(songs):
        num = i+1
        time = song.formatted_time()
        if list_filenames:
            line = f"{num: <3} | {time: <7} | {song.filename}\n"
        else:
            line = f"{num: <3} | {time: <7} | {song}\n"
        msg_list = await add_to_msg_list(line, msg_list, ctx)
    msg_list += "```"
    await ctx.send(msg_list)
