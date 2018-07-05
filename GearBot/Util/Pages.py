import discord
from discord import utils

from Util import Utils

page_handlers = dict()

known_messages = dict()

prev_id = 433284297336815616
next_id = 433284297340878849

prev_emoji = None
next_emoji = None


def on_ready(bot):
    global prev_emoji, next_emoji
    prev_emoji = utils.get(bot.emojis, id=prev_id)
    next_emoji = utils.get(bot.emojis, id=next_id)


def register(type, init, update):
    page_handlers[type] = {
        "init": init,
        "update": update
    }

def unregister(type):
    del page_handlers[type]

async def create_new(type, ctx, **kwargs):
    text, embed, has_pages = await page_handlers[type]["init"](ctx, **kwargs)
    message:discord.Message = await ctx.channel.send(text, embed=embed)
    known_messages[str(message.id)] = {
        "type": type,
        "page": 0
    }

    if has_pages:
        await message.add_reaction(prev_emoji)
        await message.add_reaction(next_emoji)

    if len(known_messages.keys()) > 500:
        del known_messages[list(known_messages.keys())[0]]

    save_to_disc()

async def update(message, action):
    message_id = str(message.id)
    if message_id in known_messages.keys():
        type = known_messages[message_id]["type"]
        page_num = known_messages[message_id]["page"]
        text, embed, page = await page_handlers[type]["update"](message, page_num, action)
        await message.edit(content=text, embed=embed)
        known_messages[message_id]["page"] = page
        save_to_disc()
        return True
    return False

def save_to_disc():
    Utils.saveToDisk("known_messages", known_messages)

def load_from_disc():
    global known_messages
    known_messages = Utils.fetchFromDisk("known_messages")