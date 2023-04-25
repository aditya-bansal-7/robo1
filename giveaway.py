import telebot
import random
import time
from telebot import types 
import requests
import threading
import uuid


bot = telebot.TeleBot("6133256899:AAEKrNeoX4iLQk3vmsDnzMbhOA-dqgaKnIY")

giveaways = {} 

blacklist = []

API_KEY = "2748b8f5-8e99-4210-845d-78176b3a1f62"

allowed_groups = [-648266309,-1001679321636,-1001856181857,-1001467085152,-1001733766092]

lock = threading.Lock()

@bot.message_handler(commands=['start'])
def start_command(message):
    markup = types.InlineKeyboardMarkup()
    markup.row(
    types.InlineKeyboardButton('Join Binaryx Global ➕', url='https://t.me/binaryxGlobal')
    
)
    markup.row(
    types.InlineKeyboardButton('Get Help', url='https://telegra.ph/Binaryx-Robot-04-23'),
    types.InlineKeyboardButton('Local Groups', callback_data='local')
    
)
    markup.row(
    types.InlineKeyboardButton('💠BNX Price💠', callback_data='price')
    )
    first_name = message.chat.first_name
    user_name = message.from_user.username

    bot.send_message(
        chat_id=message.chat.id,
        text=f'<a href="https://telegra.ph/file/0c7b5d3f0fee181375409.jpg">👋 </a> Hey <a href="https://t.me/{user_name}">{first_name}</a>! \nWelcome to <b>BINARYX ROBOT!</b>\n ──────────────────────────────────────────────────── \nJoin our community Now 🌐 ',
        parse_mode = 'HTML',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'local':
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton('中文 中国 Chinese 🇨🇳', url='https://t.me/binaryxOfficial'),
            types.InlineKeyboardButton('हिन्दी Hindi India 🇮🇳', url='https://t.me/BinaryX_Hindi')
        )
        markup.row(
            types.InlineKeyboardButton('Brazil Português 🇧🇷', url='https://t.me/BinaryXChat'),
            types.InlineKeyboardButton('Bengali বাংলা 🇧🇩', url='https://t.me/BinaryX_Bengali')  
        )
        markup.row(
            types.InlineKeyboardButton('Arabic عربى ', url='https://t.me/BinaryX_Arabic'),
            types.InlineKeyboardButton('Turkish Türkçe ', url='https://t.me/BinaryXTurkeyOfficial')
        )
        markup.row(
            types.InlineKeyboardButton('Indonesia 🇮🇩', url='https://t.me/BinaryXIndonesia'),
            types.InlineKeyboardButton('Pakistan ', url='https://t.me/binaryxurdu')
        )
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Join BinaryX local group 🌍",
            reply_markup=markup
        )
    elif call.data == 'price':
        symbol = "BNX"
        result = get_price(symbol)
        price, percent_change_24h = result
        response_text = f"💸 Current Price💲 \n\n💠<b>{symbol}</b> :<code> ${price:,.2f}</code> "
        if percent_change_24h is not None:
            change_24h_text = f"{percent_change_24h:.2f}%"
            if percent_change_24h > 0:
                response_text += f" (🟢{change_24h_text})"
            elif percent_change_24h < 0:
                response_text += f" (🔴{change_24h_text})"
            else:
                response_text += f" ({change_24h_text})"
        bot.send_message(call.message.chat.id, response_text, parse_mode='HTML')
    elif call.data.startswith(("join_giveaway:", "leave_giveaway:")):
        giveaway_id = call.data.split(":")[1]
        giveaway = giveaways.get(giveaway_id)
        if giveaway is None:
            bot.answer_callback_query(call.id, "Sorry, this giveaway is no longer available.")
            return
        user_id = call.from_user.id
        if user_id in blacklist:
            bot.answer_callback_query(call.id, "You are blacklisted and cannot join this giveaway.")
            return
        chat_id = call.message.chat.id
        user_id = call.from_user.id
        # Check if user is a member of the chat
        chat_info = bot.get_chat(chat_id)
        members_count = bot.get_chat_members_count(chat_id)
        if bot.get_chat_member(chat_id, user_id).status == "left" or members_count == 0:
            bot.answer_callback_query(call.id, "You must be a member of the group to join the giveaway.")
            return
        if call.data.startswith(("join_giveaway:")):
            giveaway_id = call.data.split(":")[1]
            user_id = call.from_user.id
            if user_id in giveaways[giveaway_id]["participants"]:
                bot.answer_callback_query(call.id, "You have already joined the giveaway.")
                return
            giveaways[giveaway_id]["participants"].append(user_id)
            
            num_participants = len(giveaways[giveaway_id]["participants"])
            reply_markup = telebot.types.InlineKeyboardMarkup()
            reply_markup.add(telebot.types.InlineKeyboardButton(f"Join Giveaway [{num_participants}]", callback_data=f"join_giveaway:{giveaway_id}"))
            reply_markup.add(telebot.types.InlineKeyboardButton("Leave Giveaway", callback_data=f"leave_giveaway:{giveaway_id}"))
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=reply_markup)
            bot.answer_callback_query(call.id, "You have successfully joined the giveaway.")

            print(giveaways)
            
        elif call.data.startswith(("leave_giveaway:")):
            giveaway_id = call.data.split(":")[1]
            if user_id not in giveaways[giveaway_id]["participants"]:
                bot.answer_callback_query(call.id, "You have not joined this giveaway.")
                return
            giveaways[giveaway_id]["participants"].remove(user_id)
            num_participants = len(giveaways[giveaway_id]["participants"])
            reply_markup = telebot.types.InlineKeyboardMarkup()
            reply_markup.add(telebot.types.InlineKeyboardButton(f"Join Giveaway [{num_participants}]", callback_data=f"join_giveaway:{giveaway_id}"))
            reply_markup.add(telebot.types.InlineKeyboardButton("Leave Giveaway", callback_data=f"leave_giveaway:{giveaway_id}"))
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=reply_markup)
            bot.answer_callback_query(call.id, "You have successfully left the giveaway.")


def get_price(crypto_symbol):
    url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={crypto_symbol}&convert=USD'
    headers = {'X-CMC_PRO_API_KEY': API_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()
    if 'status' in data and data['status']['error_code'] == 400:
        return None
    try:
        price = data['data'][crypto_symbol]['quote']['USD']['price']
        percent_change_24h = data['data'][crypto_symbol]['quote']['USD']['percent_change_24h']
        return price, percent_change_24h
    except KeyError:
        return None

@bot.message_handler(commands=['local'])
def local(message):
    markup = types.InlineKeyboardMarkup()

    markup.row(
    types.InlineKeyboardButton('中文 中国 Chinese 🇨🇳', url='https://t.me/binaryxOfficial'),
    types.InlineKeyboardButton('हिन्दी Hindi India 🇮🇳', url='https://t.me/BinaryX_Hindi')
)
    markup.row(
    types.InlineKeyboardButton('Brazil Português 🇧🇷', url='https://t.me/BinaryXChat'),
    types.InlineKeyboardButton('Bengali বাংলা 🇧🇩', url='https://t.me/BinaryX_Bengali')  
)
    markup.row(
    types.InlineKeyboardButton('Arabic عربى ', url='https://t.me/BinaryX_Arabic'),
    types.InlineKeyboardButton('Turkish Türkçe ', url='https://t.me/BinaryXTurkeyOfficial')
)
    markup.row(
    types.InlineKeyboardButton('Indonesia 🇮🇩', url='https://t.me/BinaryXIndonesia'),
    types.InlineKeyboardButton('Pakistan ', url='https://t.me/binaryxurdu')
)
    bot.send_message(
        chat_id=message.chat.id,
        text="Join BinaryX local group 🌍",
        reply_markup=markup
        )
@bot.message_handler(commands=['social'])
def social(message):
    bot.send_message(
        chat_id=message.chat.id,
        text="👺 Twitter - https://twitter.com/binary_x \n\n👺 Discord - https://discord.gg/binaryx"
        )

@bot.message_handler(commands=['website'])
def website(message):
    bot.send_message(
        chat_id=message.chat.id,
        text="binaryx.pro"
        )

@bot.message_handler(commands=['BNX','bnx'])
def bnx(message):
        symbol = "BNX"
        result = get_price(symbol)
        price, percent_change_24h = result
        response_text = f"💸 Current Price💲 \n\n💠<b>{symbol}</b> :<code> ${price:,.2f}</code> "
        if percent_change_24h is not None:
            change_24h_text = f"{percent_change_24h:.2f}%"
            if percent_change_24h > 0:
                response_text += f" (🟢{change_24h_text})"
            elif percent_change_24h < 0:
                response_text += f" (🔴{change_24h_text})"
            else:
                response_text += f" ({change_24h_text})"

        bot.send_message(message.chat.id, response_text, parse_mode='HTML')


@bot.message_handler(commands=['giveaway'])
def giveaway_handler(message):
    
    chat_id = message.chat.id
    print(chat_id)
    if chat_id not in allowed_groups:
        bot.reply_to(message, "Sorry, this command is only available in specific groups.")
        return
    
    chat_members = bot.get_chat_administrators(chat_id)
    user_id = message.from_user.id
    is_admin = False
    for member in chat_members:
        if member.user.id == user_id and member.status in ['creator', 'administrator']:
            is_admin = True
            break

    if is_admin:
        args = message.text.split()[1:]
        if len(args) == 4:
            amount, currency, num_winners, duration = args
            description = ""
        elif len(args) >= 5:
            amount, currency, num_winners, duration, *description = args
            description = " ".join(description)
        else:
            bot.reply_to(message, "Invalid command format. Usage: /giveaway <amount> <currency> <num_winners> <duration (optional)> ")
            return
        try:
            amount = int(amount)
            num_winners = int(num_winners)
            duration = int(duration[:-1]) * {"d": 86400, "h": 3600, "m": 60, "s": 1}[duration[-1]]
        except ValueError:
            bot.reply_to(message, "Invalid command format. Usage: /giveaway <amount> <currency> <num_winners> <duration>")
            return
        except KeyError:
            bot.reply_to(message, "Invalid duration format. Duration should be in the format 1d, 1h, 1m, or 1s.")
            return
        except:
            bot.reply_to(message, "Invalid command format. Usage: /giveaway <amount> <currency> <num_winners> <duration>")
    
        # Generate a unique identifier for the giveaway
        giveaway_id = str(uuid.uuid4())

        # Store the giveaway data using the unique identifier
        giveaways[giveaway_id] = {"chat_id": chat_id,"amount": amount, "currency": currency, "num_winners": num_winners, "duration": duration, "participants": []}
        num_participants = len(giveaways[giveaway_id]["participants"])
        time_left = duration

        if description:

            message_text = f"🎉 Giveaway Time 🎉 \n\n🎁Reward - {amount} {currency} \n\n🏆Winners - {num_winners}\n\n⏱End In {time_left//86400}d:{time_left%86400//3600}h:{time_left%3600//60}m:{time_left%60}s. \n\n Note - {description}"
        else:
            message_text = f"🎉 Giveaway Time 🎉 \n\n🎁Reward - {amount} {currency} \n\n🏆Winners - {num_winners}\n\n⏱End In {time_left//86400}d:{time_left%86400//3600}h:{time_left%3600//60}m:{time_left%60}s."
        
            
        # Add the unique identifier as a callback data to the inline keyboard button
        reply_markup = telebot.types.InlineKeyboardMarkup()
        reply_markup.add(telebot.types.InlineKeyboardButton(f"Join Giveaway [{num_participants}]", callback_data=f"join_giveaway:{giveaway_id}"))
        bot.send_message(chat_id, message_text, reply_markup=reply_markup)
        giveaways[giveaway_id]["message_id"] = message.message_id +1
        bot.delete_message(message.chat.id,message.id)
        time_thread = threading.Thread(target=time_check)
        time_thread.start()
    else:
        bot.reply_to(message, "You must be an admin to use this command.")




def end_giveaway(giveaway_id):
    giveaway = giveaways.pop(giveaway_id, None)
    chat_id = giveaway["chat_id"]
    if giveaway is None:
        return
    if len(giveaway["participants"]) < giveaway["num_winners"]:
        message_text = "Not enough participants to select a winner. The giveaway has been cancelled."
        bot.send_message(chat_id, message_text)
        return
    winners = []
    for i in range(giveaway["num_winners"]):
        winner = random.choice(giveaway["participants"])
        winners.append(winner)
        giveaway["participants"].remove(winner)
    message_text = f"The giveaway for {giveaway['amount']} {giveaway['currency']} has ended. The winners are:"
    for winner in winners:
        member = bot.get_chat_member(chat_id, winner)
        first_name = member.first_name
        message_text += f"<a href='tg://user?id={member}'>{first_name}</a> - @{member.user.username}"
    message_text += f"\n\nPlease submit your wallet address to @xingman within 2 hours."
    bot.send_message(chat_id, message_text , parse_mode='HTML')
   






@bot.message_handler(commands=['blacklist'])
def blacklist_user(message):

    chat_id = message.chat.id
    if chat_id not in allowed_groups:
        bot.reply_to(message, "Sorry, this command is only available in specific groups.")
        return
    
    chat_members = bot.get_chat_administrators(chat_id)
    user_id = message.from_user.id
    is_admin = False
    for member in chat_members:
        if member.user.id == user_id and member.status in ['creator', 'administrator']:
            is_admin = True
            break

    if is_admin:
        if message.reply_to_message is not None:
            user_id = message.reply_to_message.from_user.id
            username = message.reply_to_message.from_user.username
            if user_id not in blacklist:
                blacklist.append(user_id)
                bot.reply_to(message, f"User @{username} has been added to the blacklist.")
            else:
                bot.reply_to(message, f"User @{username} is already in the blacklist.")
        else:
            bot.reply_to(message, "Please reply to user message to blacklist.")
    else:
        bot.reply_to(message, "You must be an admin to use this command.")


@bot.message_handler(commands=['unblacklist'])
def unblacklist_user(message):

    chat_id = message.chat.id
    if chat_id not in allowed_groups:
        bot.reply_to(message, "Sorry, this command is only available in specific groups.")
        return
    
    chat_members = bot.get_chat_administrators(chat_id)
    user_id = message.from_user.id
    is_admin = False
    for member in chat_members:
        if member.user.id == user_id and member.status in ['creator', 'administrator']:
            is_admin = True
            break

    if is_admin:
        if message.reply_to_message is not None:
            user_id = message.reply_to_message.from_user.id
            username = message.reply_to_message.from_user.username
            if user_id in blacklist:
                blacklist.remove(user_id)
                bot.reply_to(message, f"User @{username} has been removed from the blacklist.")
            else:
                bot.reply_to(message, f"User @{username} is not in the blacklist.")
        else:
            bot.reply_to(message, "Please reply to a message to unblacklist the user.")
    else:
            bot.reply_to(message, "You must be an admin to use this command.")

def time_check():
    with lock:
        time.sleep(10)
        while True:
            for giveaway_id, giveaway in list(giveaways.items()):
                giveaway["duration"] -= 10
                num_winners = giveaway["num_winners"]
                currency = giveaway["currency"]
                amount = giveaway["amount"]
                time_left = giveaway["duration"]
                if time_left > 0 :
                    message_text = f"🎉 Giveaway Time 🎉 \n\n🎁Reward - {amount} {currency} \n\n🏆Winners - {num_winners}\n\n⏱End In {time_left//86400}d:{time_left%86400//3600}h:{time_left%3600//60}m:{time_left%60}s."
                    reply_markup = telebot.types.InlineKeyboardMarkup()
                    num_participants = len(giveaway["participants"])
                    reply_markup.add(telebot.types.InlineKeyboardButton(f"Join Giveaway [{num_participants}]", callback_data=f"join_giveaway:{giveaway_id}"))
                    reply_markup.add(telebot.types.InlineKeyboardButton("Leave Giveaway", callback_data=f"leave_giveaway:{giveaway_id}"))
                    bot.edit_message_text(chat_id=giveaway["chat_id"], message_id=giveaway["message_id"], text=message_text, reply_markup=reply_markup)
                else:
                    end_giveaway(giveaway_id)
            time.sleep(10)

bot.infinity_polling()
