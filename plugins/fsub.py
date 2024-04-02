#Ansh vachhani

import logging
from database.fsub_db import Fsub_DB
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, get_bad_files
from info import CHANNELS, ADMINS, AUTH_CHANNEL, HOW_TO_VERIFY, CHNL_LNK, GRP_LNK, LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT, CHNL_LNK, GRP_LNK, REQST_CHANNEL, SUPPORT_CHAT_ID, MAX_B_TN, IS_VERIFY, HOW_TO_VERIFY, FSUB_CHANNEL
from utils import temp
from pyrogram import Client, filters, enums
from pyrogram.errors import UserNotParticipant
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ChatJoinRequest, Message
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
LINK = None
FSUB_TEMP = {}


@Client.on_chat_join_request(filters.chat(FSUB_CHANNEL))
async def fetch_requests(bot, message: ChatJoinRequest):
    id = message.from_user.id
    name = message.from_user.first_name
    username = message.from_user.username
    date = message.date
    await Fsub_DB().add_user(id=id, name=name, username=username, date=date)
    file_id = FSUB_TEMP.get(message.from_user.id)           
    if file_id:        
        if IS_VERIFY and not await check_verification(client, message.from_user.id):
            btn = [[
                InlineKeyboardButton("Vᴇʀɪғʏ", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
                InlineKeyboardButton("Hᴏᴡ Tᴏ Vᴇʀɪғʏ", url=HOW_TO_VERIFY)
            ]]
            return await bot.send_message(
            chat_id=message.from_user.id,
            text="<b>Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴠᴇʀɪғɪᴇᴅ!\nKɪɴᴅʟʏ ᴠᴇʀɪғʏ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ Sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ ᴀᴄᴄᴇss ᴛᴏ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏᴠɪᴇs ᴜɴᴛɪʟ 12 ʜᴏᴜʀs ғʀᴏᴍ ɴᴏᴡ !</b>",
            protect_content=True if PROTECT_CONTENT else False,
            reply_markup=InlineKeyboardMarkup(btn)
            )
        files_ = await get_file_details(file_id)
        if not files_:
            return await bot.send_message(message.from_user.id, 'No such file exist.')
        files = files_[0]
        title = files.file_name
        size=get_size(files.file_size)
        f_caption=files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption=f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}" 
        dm = await bot.send_cached_media(
           chat_id=message.from_user.id,
           file_id=file_id,
           caption=f_caption,
           protect_content=False
        )
        buttons = InlineKeyboardMarkup(
           [
               [
                  InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=GRP_LNK),
                  InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
               ],[
                  InlineKeyboardButton("Bᴏᴛ Uᴩᴅᴀᴛᴇꜱ", url="https://t.me/+ixCkCbBsG6hkMzU1")
               ]]
        )
        await dm.edit_reply_markup(buttons)
        FSUB_TEMP[message.from_user.id] = None
        
@Client.on_message(filters.command("total_reqs") & filters.user(ADMINS))
async def total_reqs_num(bot, message):
    num = await Fsub_DB().total_users()
    return await message.reply_text(f"Total Requests: {num}")

@Client.on_message(filters.command("get_reqs") & filters.user(ADMINS))
async def get_all_reqs(bot, message):
    users = await Fsub_DB().get_all_users()
    out="Users who sent requests are:\n\n"
    msg = await message.reply_text(f"{out}")
    if users is None:
        await msg.edit_text("No users found !")
        return
    async for user in users:
        out+=f"ID: {user['id']}\nName: {user['name']}\nUserName: @{user['username']}\nDate Request sent: {user['date']}\n\n"
    try:
        await msg.edit_text(f"{out}")
        return
    except MessageTooLong:
        with open('requests.txt', 'w+') as outfile:
            outfile.write(out)
        return await message.reply_document('requests.txt', caption="List of requests")

@Client.on_message(filters.command("delete_reqs") & filters.user(ADMINS))
async def delete_reqs(bot, message):
    await Fsub_DB().purge_all_users()
    return await message.reply_text("Successfully deleted all requests from DB.")

@Client.on_message(filters.command("delete_req") & filters.user(ADMINS))
async def delete_req(bot, message):
    try:
        userid = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("Give me a userid along with that cmd.\nExample: /delete_req 2890388")
    user = await Fsub_DB().get_user(userid)
    name = user['name']
    await Fsub_DB().purge_user(userid)
    return await message.reply_text(f"Sucessfully deleted {name} from DB.")

@Client.on_message(filters.command("get_req") & filters.user(ADMINS))
async def get_req(bot, message):
    try:
        userid = message.text.split(" ", 1)[1]  
    except:
        return await message.reply_text("Give me a userid along with that cmd.\nExample: /get_req 2890388")
    user = await Fsub_DB().get_user(userid)
    return await message.reply_text(f"Request Details:\nID: {user['id']}\nName: {user['name']}\nUserName: {user['username']}\nDate of Request: {user['date']}")

async def Force_Sub(bot: Client, message: Message, fileid=None):
    global LINK
    if not FSUB_CHANNEL:
        return True
    try:
        user = await Fsub_DB().get_user(message.from_user.id)
        if user and str(user['id']) == str(message.from_user.id):
            return True
    except Exception as e:
        logger.exception(e)
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f"Error: {e}"
        )
    try:
        await bot.get_chat_member(
            chat_id=int(FSUB_CHANNEL),
            user_id=message.from_user.id
        )
        return True
    except UserNotParticipant:
        try:
            if LINK == None:
                link = await bot.create_chat_invite_link(
                    chat_id=FSUB_CHANNEL,
                    creates_join_request=True
                )
                LINK = link
                logger.info("Invite link created !")
            else:
                link = LINK
        except Exception as e:
            logger.exception(e)
            await bot.send_message(
                chat_id=message.from_user.id,
                text=f"Error: {e}"
            )
        btn = [[
            InlineKeyboardButton("📣ʀᴇqᴜᴇꜱᴛ ᴛᴏ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ📣", url=link.invite_link)
        ]]
        if fileid != None:
            btn.append([InlineKeyboardButton("♻️ᴛʀʏ ᴀɢᴀɪɴ♻️", url=f"https://t.me/{temp.U_NAME}?start=file_{fileid}")])
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f"Hey {message.from_user.mention}😍,\n\n♦️ 𝗥𝗘𝗔𝗗 𝗧𝗛𝗜𝗦 𝗜𝗡𝗦𝗧𝗥𝗨𝗖𝗧𝗜𝗢𝗡𝗦♦️\n\nClick the  𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐭𝐨 𝐣𝐨𝐢𝐧 and then click 𝐓𝐫𝐲 𝐀𝐠𝐚𝐢𝐧 and you will get the File...😁\n\n<b>♦️महत्वपूर्ण♦</b>\n\n𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐭𝐨 𝐣𝐨𝐢𝐧 पर क्लिक करें और फिर 𝐓𝐫𝐲 𝐀𝐠𝐚𝐢𝐧 पर क्लिक करें और आपको फ़ाइल मिल जाएगी...😁\n\n<b>♦ശ്രദ്ധിക്കുക♦</b>\n\nതാഴെ ഉള്ള ജോയിൻ ലിങ്കിൽ ക്ലിക്ക് ചെയ്തു 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐭𝐨 𝐣𝐨𝐢𝐧 ക്ലിക്ക് ചെയ്ത് കഴിഞ്ഞ് 𝐓𝐫𝐲 𝐀𝐠𝐚𝐢𝐧 ക്ലിക്ക് ചെയ്‌താൽ നിങ്ങൾക് സിനിമ ലഭിക്കുന്നതാണ്...😁", 
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return False
