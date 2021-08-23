# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

import io
import math
import random
import urllib.request
from os import remove

import requests
from bs4 import BeautifulSoup as bs
from PIL import Image
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import (
    DocumentAttributeFilename,
    DocumentAttributeSticker,
    InputPeerNotifySettings,
    InputStickerSetID,
    MessageMediaPhoto,
)

from userbot import CMD_HELP
from userbot import S_PACK_NAME as custompack
from userbot import bot
from userbot.events import register

KANGING_STR = [
    "Wao.,Bagus Nih...Colong Dulu Yekan..",
    "Colong Sticker dulu yee kan",
    "ehh, mantep nih.....aku colong ya...",
    "Ini Sticker aku colong yaa DUARR!",
    "leh ugha ni Sticker Colong ahh~",
]


@register(outgoing=True, pattern=r"^\.(?:tikel|kang)\s?(.)?")
async def kang(args):
    user = await bot.get_me()
    if not user.username:
        user.username = user.first_name
    message = await args.get_reply_message()
    photo = None
    emojibypass = False
    is_anim = False
    emoji = None

    if not message or not message.media:
        return await args.edit("`Maaf , Saya Gagal Mengambil Sticker Ini!`")

    if isinstance(message.media, MessageMediaPhoto):
        await args.edit(f"`{random.choice(KANGING_STR)}`")
        photo = io.BytesIO()
        photo = await bot.download_media(message.photo, photo)
    elif "image" in message.media.document.mime_type.split("/"):
        await args.edit(f"`{random.choice(KANGING_STR)}`")
        photo = io.BytesIO()
        await bot.download_file(message.media.document, photo)
        if (
            DocumentAttributeFilename(file_name="sticker.webp")
            in message.media.document.attributes
        ):
            emoji = message.media.document.attributes[1].alt
            if emoji != "✨":
                emojibypass = True
    elif "tgsticker" in message.media.document.mime_type:
        await args.edit(f"`{random.choice(KANGING_STR)}`")
        await bot.download_file(message.media.document, "AnimatedSticker.tgs")

        attributes = message.media.document.attributes
        for attribute in attributes:
            if isinstance(attribute, DocumentAttributeSticker):
                emoji = attribute.alt

        emojibypass = True
        is_anim = True
        photo = 1
    else:
        return await args.edit("`File Tidak Didukung !`")
    if photo:
        splat = args.text.split()
        if not emojibypass:
            emoji = "✨"
        pack = 1
        if len(splat) == 3:
            pack = splat[2]  # User sent both
            emoji = splat[1]
        elif len(splat) == 2:
            if splat[1].isnumeric():
                # User wants to push into different pack, but is okay with
                # thonk as emote.
                pack = int(splat[1])
            else:
                # User sent just custom emote, wants to push to default
                # pack
                emoji = splat[1]

        u_name = user.username
        f_name = user.first_name
        packname = f"StickerBy{u_name}_{pack}"
        custom_packnick = f"{custompack}" or f"{f_name}"
        packnick = f"{custom_packnick}"
        cmd = "/newpack"
        file = io.BytesIO()

        if not is_anim:
            image = await resize_photo(photo)
            file.name = "sticker.png"
            image.save(file, "PNG")
        else:
            packname += "_anim"
            packnick += " (Animated)"
            cmd = "/newanimated"

        response = urllib.request.urlopen(
            urllib.request.Request(f"http://t.me/addstickers/{packname}")
        )
        htmlstr = response.read().decode("utf8").split("\n")

        if (
            "  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>."
            not in htmlstr
        ):
            async with bot.conversation("Stickers") as conv:
                await conv.send_message("/addsticker")
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message(packname)
                x = await conv.get_response()
                while "120" in x.text:
                    pack += 1
                    packname = f"StickerBy{u_name}_{pack}"
                    packnick = f"{custom_packnick}"
                    await args.edit(
                        "`Switching to Pack "
                        + str(pack)
                        + " due to insufficient space`"
                    )
                    await conv.send_message(packname)
                    x = await conv.get_response()
                    if x.text == "Gagal Memilih Pack.":
                        await conv.send_message(cmd)
                        await conv.get_response()
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.send_message(packnick)
                        await conv.get_response()
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        if is_anim:
                            await conv.send_file("AnimatedSticker.tgs")
                            remove("AnimatedSticker.tgs")
                        else:
                            file.seek(0)
                            await conv.send_file(file, force_document=True)
                        await conv.get_response()
                        await conv.send_message(emoji)
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await conv.send_message("/publish")
                        if is_anim:
                            await conv.get_response()
                            await conv.send_message(f"<{packnick}>")
                        # Ensure user doesn't get spamming notifications
                        await conv.get_response()
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.send_message("/skip")
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await conv.send_message(packname)
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        return await args.edit(
                            "`Sticker ditambahkan ke pack yang berbeda !"
                            "\nIni pack yang baru saja dibuat!"
                            f"\nTekan [Sticker Pack](t.me/addstickers/{packname}) Untuk Melihat Sticker Pack",
                            parse_mode="md",
                        )
                if is_anim:
                    await conv.send_file("AnimatedSticker.tgs")
                    remove("AnimatedSticker.tgs")
                else:
                    file.seek(0)
                    await conv.send_file(file, force_document=True)
                rsp = await conv.get_response()
                if "Sorry, the file type is invalid." in rsp.text:
                    return await args.edit(
                        "`Gagal Menambahkan Sticker, Gunakan` @Stickers ` Bot Untuk Menambahkan Sticker Anda.`"
                    )
                await conv.send_message(emoji)
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message("/done")
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
        else:
            await args.edit("`Membuat Pack Sticker Baru`")
            async with bot.conversation("Stickers") as conv:
                await conv.send_message(cmd)
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message(packnick)
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                if is_anim:
                    await conv.send_file("AnimatedSticker.tgs")
                    remove("AnimatedSticker.tgs")
                else:
                    file.seek(0)
                    await conv.send_file(file, force_document=True)
                rsp = await conv.get_response()
                if "Sorry, the file type is invalid." in rsp.text:
                    return await args.edit(
                        "`Gagal Menambahkan Sticker, Gunakan` @Stickers ` Bot Untuk Menambahkan Sticker.`"
                    )
                await conv.send_message(emoji)
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message("/publish")
                if is_anim:
                    await conv.get_response()
                    await conv.send_message(f"<{packnick}>")
                # Ensure user doesn't get spamming notifications
                await conv.get_response()
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message("/skip")
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message(packname)
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)

        await args.edit(
            "** Sticker Berhasil Ditambahkan!**"
            f"\n        👻 **[KLIK DISINI](t.me/addstickers/{packname})** 👻\n**Untuk Menggunakan Stickers**",
            parse_mode="md",
        )


async def resize_photo(photo):
    image = Image.open(photo)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if size1 > size2:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        image = image.resize(sizenew)
    else:
        maxsize = (512, 512)
        image.thumbnail(maxsize)

    return image


@register(outgoing=True, pattern=r"^\.packkang($| )?([0-9]*)?$")
async def kangpack(event):
    await event.edit("`Kanging the whole pack...`")
    user = await bot.get_me()
    pack_username = ""
    if not user.username:
        try:
            user.first_name.decode("ascii")
            pack_username = user.first_name
        except UnicodeDecodeError:  # User's first name isn't ASCII, use ID instead
            pack_username = user.id
    else:
        pack_username = user.username

    textx = await event.get_reply_message()

    if not textx.sticker:
        await event.edit(
            "**Kamu perlu membalas stiker untuk mencuri seluruh paket sticker!**"
        )
        return

    sticker_set = textx.file.sticker_set
    stickers = await event.client(
        GetStickerSetRequest(
            stickerset=InputStickerSetID(
                id=sticker_set.id, access_hash=sticker_set.access_hash
            )
        )
    )
    is_anim = textx.file.mime_type == "application/x-tgsticker"

    number = event.pattern_match.group(2) or 1
    new_pack = False
    while not new_pack:
        packname = f"a{user.id}_by_{pack_username}_{number}{'_anim' if is_anim else ''}"
        packtitle = (
            f"Sticker @{user.username or user.first_name} Vol. "
            f"{number}{' animated' if is_anim else ''}"
        )
        response = urllib.request.urlopen(
            urllib.request.Request(f"http://t.me/addstickers/{packname}")
        )
        htmlstr = response.read().decode("utf8").split("\n")
        new_pack = PACK_DOESNT_EXIST in htmlstr
        if not new_pack:
            if event.pattern_match.group(2):
                await event.edit(
                    "**Paket ini tidak ada! Tentukan nomor lain atau hilangkan argumen untuk membiarkan "
                    "Mendapatkan nomor paket terendah yang tersedia secara otomatis.**"
                )
                return
            number += 1

    # Mute Stickers bot to ensure user doesn't get notification spam
    muted = await bot(
        UpdateNotifySettingsRequest(
            peer="t.me/Stickers",
            settings=InputPeerNotifySettings(mute_until=2 ** 31 - 1),
        )
    )
    if not muted:
        await event.edit(
            "**Tidak dapat membisukan bot Stiker, waspadalah terhadap spam notifikasi.**"
        )

    async with bot.conversation("Stickers") as conv:
        # Cancel any pending command
        await conv.send_message("/cancel")
        await conv.get_response()

        # Send new pack command
        if is_anim:
            await conv.send_message("/newanimated")
        else:
            await conv.send_message("/newpack")
        await conv.get_response()

        # Give the pack a name
        await conv.send_message(packtitle)
        await conv.get_response()

    for sticker in stickers.documents:
        async with bot.conversation("Stickers") as conv2:
            emoji = sticker.attributes[1].alt
            # Upload sticker file
            if is_anim:
                sticker_dl = io.BytesIO()
                await bot.download_media(sticker, sticker_dl)
                sticker_dl.seek(0)
                upload = await bot.upload_file(
                    sticker_dl, file_name="AnimatedSticker.tgs"
                )
                await conv2.send_file(upload, force_document=True)
            else:
                await conv2.send_file(sticker, force_document=True)
            await conv2.get_response()

            # Send the emoji
            await conv2.send_message(emoji)
            await conv2.get_response()

    async with bot.conversation("Stickers") as conv:
        # Publish the pack
        await conv.send_message("/publish")
        if is_anim:
            await conv.get_response()
            await conv.send_message(f"<{packtitle}>")
        await conv.get_response()

        # Skip pack icon selection
        await conv.send_message("/skip")
        await conv.get_response()

        # Send packname
        await conv.send_message(packname)
        await conv.get_response()

    # Read all unread messages
    await bot.send_read_acknowledge("t.me/Stickers")
    # Unmute Stickers bot back
    muted = await bot(
        UpdateNotifySettingsRequest(
            peer="t.me/Stickers", settings=InputPeerNotifySettings(mute_until=None)
        )
    )

    await event.edit(
        f"`Sticker pack {number}{' (animated)' if is_anim else ''} has been created!\n"
        f"It can be found` [here](t.me/addstickers/{packname})`.`",
        parse_mode="md",
    )


@register(outgoing=True, pattern=r"^\.stkrinfo$")
async def get_pack_info(event):
    if not event.is_reply:
        return await event.edit("`Mohon Balas Ke Sticker `")

    rep_msg = await event.get_reply_message()
    if not rep_msg.document:
        return await event.edit("`Balas ke sticker untuk melihat detail pack`")

    try:
        stickerset_attr = rep_msg.document.attributes[1]
        await event.edit("`Fetching details of the sticker pack, please wait..`")
    except BaseException:
        return await event.edit("`Ini bukan sticker, Mohon balas ke sticker.`")

    if not isinstance(stickerset_attr, DocumentAttributeSticker):
        return await event.edit("`Ini bukan sticker, Mohon balas ke sticker.`")

    get_stickerset = await bot(
        GetStickerSetRequest(
            InputStickerSetID(
                id=stickerset_attr.stickerset.id,
                access_hash=stickerset_attr.stickerset.access_hash,
            )
        )
    )
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)

    OUTPUT = (
        f"**Sticker Title:** `{get_stickerset.set.title}\n`"
        f"**Nama Pendek Sticker:** `{get_stickerset.set.short_name}`\n"
        f"**Official:** `{get_stickerset.set.official}`\n"
        f"**Arsip:** `{get_stickerset.set.archived}`\n"
        f"**Sticker Dalam Pack:** `{len(get_stickerset.packs)}`\n"
        f"**Emoji Dalam Pack:**\n{' '.join(pack_emojis)}"
    )

    await event.edit(OUTPUT)


@register(outgoing=True, pattern=r"^\.getsticker$")
async def sticker_to_png(sticker):
    if not sticker.is_reply:
        await sticker.edit("`NULL information to fetch...`")
        return False

    img = await sticker.get_reply_message()
    if not img.document:
        await sticker.edit("`Mohon Balas Ke Sticker`")
        return False

    try:
        img.document.attributes[1]
    except Exception:
        await sticker.edit("`Maaf , Ini Bukanlah Sticker`")
        return

    with io.BytesIO() as image:
        await sticker.client.download_media(img, image)
        image.name = "sticker.png"
        image.seek(0)
        try:
            await img.reply(file=image, force_document=True)
        except Exception:
            await sticker.edit("`Tidak Dapat Mengirim File...`")
        else:
            await sticker.delete()
    return


@register(outgoing=True, pattern=r"^\.findsticker (.*)")
async def cb_sticker(event):
    query = event.pattern_match.group(1)
    if not query:
        return await event.edit("`Masukan Nama Sticker Pack!`")
    await event.edit("`Searching sticker packs...`")
    text = requests.get("https://combot.org/telegram/stickers?q=" + query).text
    soup = bs(text, "lxml")
    results = soup.find_all("div", {"class": "sticker-pack__header"})
    if not results:
        return await event.edit("`Tidak Menemukan Sticker Pack :(`")
    reply = f"**Keyword Sticker Pack:**\n {query}\n\n**Hasil:**\n"
    for pack in results:
        if pack.button:
            packtitle = (pack.find("div", "sticker-pack__title")).get_text()
            packlink = (pack.a).get("href")
            reply += f"- [{packtitle}]({packlink})\n\n"
    await event.edit(reply)


CMD_HELP.update(
    {
        "stickers": "**Plugin : **`stickers`\
        \n\n  •  **Syntax :** `.kang` atau `.tikel` [emoji]?\
        \n  •  **Function : **Balas .kang Ke Sticker Atau Gambar Untuk Menambahkan Ke Sticker Pack Mu\
        \n\n  •  **Syntax :** `.kang` [emoji] atau `.tikel` `[emoji]`\
        \n  •  **Function : **Balas .kang emoji Ke Sticker Atau Gambar Untuk Menambahkan dan costum emoji sticker Ke Pack Mu\
        \n\n  •  **Syntax :** `.stkrinfo`\
        \n  •  **Function : **Dapatkan Informasi Sticker Pack.\
        \n\n  •  **Syntax :** `.findsticker` <nama pack sticker>\
        \n  •  **Function : **Untuk Mencari Sticker Pack.\
    "
    }
)


CMD_HELP.update(
    {
        "sticker_v2": "**Plugin : **`stickers`\
        \n\n  •  **Syntax :** `.getsticker`\
        \n  •  **Function : **Balas Ke Stcker Untuk Mendapatkan File 'PNG' Sticker.\
        \n\n  •  **Syntax :** `.get`\
        \n  •  **Function : **Balas ke sticker untuk mendapatkan file 'PNG' sticker\
        \n\n  •  **Syntax :** `.stoi`\
        \n  •  **Function : **Balas Ke Stcker Untuk Mendapatkan File 'PNG' Sticker.\
        \n\n  •  **Syntax :** `.itos`\
        \n  •  **Function : **Balas ke sticker atau gambar .itos untuk mengambil sticker bukan ke pack\
    "
    }
)
