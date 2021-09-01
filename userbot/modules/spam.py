# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.

import asyncio
from asyncio import sleep

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern=r"^\.cspam (.+)")
async def leter_spam(cspammer):
    cspam = str(cspammer.pattern_match.group(1))
    message = cspam.replace(" ", "")
    await cspammer.delete()
    for letter in message:
        await cspammer.respond(letter)
    if BOTLOG:
        await cspammer.client.send_message(
            BOTLOG_CHATID, "**#CSPAM** was executed successfully"
        )


@register(outgoing=True, pattern=r"^\.wspam (.+)")
async def word_spam(wspammer):
    wspam = str(wspammer.pattern_match.group(1))
    message = wspam.split()
    await wspammer.delete()
    for word in message:
        await wspammer.respond(word)
    if BOTLOG:
        await wspammer.client.send_message(
            BOTLOG_CHATID, "**#WSPAM** was executed successfully"
        )


@register(outgoing=True, pattern=r"^\.spam (\d+) (.+)")
async def spammer(spamm):
    try:
        counter = int(spamm.pattern_match.group(1).split(" ", 1)[0])
    except IndexError:
        await spamm.edit("**Gunakan Perintah** `.spam <jumlah spam> <text>` **atau** `.spam <jumlah spam>` **sambil reply pesan**")
        await sleep(5)
        await spamm.delete()
        return
    textx = await spamm.get_reply_message()
    if not textx:
        try:
            spam_message = str(spamm.pattern_match.group(1).split(" ", 1)[1])
        except IndexError:
            await spamm.edit("**Gunakan Perintah** `.spam <jumlah spam> <text>` **atau** `.spam <jumlah spam>` **sambil reply pesan**")
            await sleep(5)
            await spamm.delete()
            return
        await spamm.delete()
        await asyncio.wait([spamm.respond(spam_message) for i in range(counter)])
        if BOTLOG:
            await spamm.client.send_message(
                BOTLOG_CHATID, "**#SPAM** was executed successfully"
            )
    elif (textx and textx.text):
        await spamm.delete()
        await asyncio.wait([spamm.respond(textx) for i in range(counter)])
        if BOTLOG:
            await spamm.client.send_message(
                BOTLOG_CHATID, "**#SPAM** was executed successfully\n"
            )


@register(outgoing=True, pattern=r"^\.picspam (\d+) (.+)")
async def tiny_pic_spam(pspam):
    message = pspam.text
    text = message.split()
    try:
        counter = int(text[1])
        link = str(text[2])
    except IndexError:
        await pspam.edit("**Gunakan Perintah** `.picspam` <jumlah spam> <link image/gif>")
        await sleep(5)
        await pspam.delete()
        return
    await pspam.delete()
    for _ in range(1, counter):
        await pspam.client.send_file(pspam.chat_id, link)
    if BOTLOG:
        await pspam.client.send_message(
            BOTLOG_CHATID, "**#PICSPAM** was executed successfully"
        )


@register(outgoing=True, pattern="^.delayspam (.*)")
async def dspammer(dspam):
    try:
        spamDelay = float(dspam.pattern_match.group(1).split(" ", 2)[0])
        counter = int(dspam.pattern_match.group(1).split(" ", 2)[1])
        spam_message = str(dspam.pattern_match.group(1).split(" ", 2)[2])
    except IndexError:
        await dspam.edit("**Gunakan Perintah** `.delayspam` <detik> <jumlah spam> <text>")
        await sleep(5)
        await dspam.delete()
        return
    await dspam.delete()
    for _ in range(1, counter):
        await dspam.respond(spam_message)
        await sleep(spamDelay)
    if BOTLOG:
        await dspam.client.send_message(
            BOTLOG_CHATID, "**#DelaySPAM** was executed successfully"
        )


CMD_HELP.update(
    {
        "spam": "**Plugin : **`spam`\
        \n\n  •  **Syntax :** `.spam` <jumlah spam> <text>\
        \n  •  **Function : **Membanjiri teks dalam obrolan!! \
        \n\n  •  **Syntax :** `.cspam` <text>\
        \n  •  **Function : **Spam surat teks dengan huruf. \
        \n\n  •  **Syntax :** `.wspam` <text>\
        \n  •  **Function : **Spam kata teks demi kata. \
        \n\n  •  **Syntax :** `.picspam` <jumlah spam> <link image/gif>\
        \n  •  **Function : **Spam Foto Seolah-olah spam teks tidak cukup !! \
        \n\n  •  **Syntax :** `.delayspam` <detik> <jumlah spam> <text>\
        \n  •  **Function : **Spam surat teks dengan huruf. \
        \n\n  •  **NOTE : Spam dengan Risiko Anda sendiri**\
    "
    }
)
