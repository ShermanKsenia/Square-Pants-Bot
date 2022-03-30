import telebot
import markovify
import random
import config
import json
from telebot import types
from user_db import DBHelper
from stickers import happy, sad, funny

db = DBHelper()
db.setup()

with open('who_to_guess.json') as f:
    who_to_guess = json.load(f)

for char, speech in who_to_guess['Model'].items():
    who_to_guess['Model'][char] = markovify.Text.from_json(speech)

characters = list(who_to_guess.keys())

with open('char_info.json') as f_info:
    char_info = json.load(f_info)

with open('episodes.json') as f_ep:
    ep_info = json.load(f_ep)

with open('personal_info.json') as f_per:
    per_info = json.load(f_per)

char_to_char = {
    'SpongeBob': 'SpongeBob SquarePants',
    'Patrick': 'Patrick Star',
    'Mr. Krabs': 'Eugene H. Krabs',
    'Squidward': 'Squidward J. Q. Tentacles',
    'Plankton': 'Sheldon J. Plankton',
    'Sandy': 'Sandra Jennifer Olivia "Sandy" Cheeks',
    'Karen': 'Karen Plankton',
    'Gary':'Gary/ Garold Wilson Jr'
}

TOKEN = config.conf
bot = telebot.TeleBot(TOKEN)

answer = ''

@bot.callback_query_handler(func=lambda call: call.data in ['own_stat', 'rating'])
def stat_again(call):
    markup = types.InlineKeyboardMarkup()
    main_menu = types.InlineKeyboardButton(text="Get to the main menu", callback_data="main_menu")
    markup.add(main_menu)
    if call.data == 'own_stat':
        bot_answer = db.get_statistics(user_id=call.from_user.id)
        bot.edit_message_text(
            chat_id=call.from_user.id, 
            message_id=call.message.message_id,
            text=bot_answer,
            parse_mode="Markdown",
            reply_markup=markup)
    else:
        bot_answer = db.get_rating(user_id=call.from_user.id)
        bot.edit_message_text(
            chat_id=call.from_user.id, 
            message_id=call.message.message_id,
            text=bot_answer,
            parse_mode="Markdown",
            reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'button3')
def send_own_stat(call):
    markup = types.InlineKeyboardMarkup()
    own_stat = types.InlineKeyboardButton(text="Personal statistics", callback_data="own_stat")
    rating = types.InlineKeyboardButton(text="Leaderboard", callback_data="rating")
    markup.add(own_stat, rating)
    bot.edit_message_text(
        chat_id=call.from_user.id, 
        message_id=call.message.message_id, 
        text=f'Choose the statistics you want to know', 
        reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.endswith('_stat'))
def send_statistics(call):
    markup = types.InlineKeyboardMarkup()
    personal = types.InlineKeyboardButton(text="Personal info", callback_data=f"{call.data[:-5]}_personal_info")
    episode = types.InlineKeyboardButton(text='Info about lines and episodes', callback_data=f'{call.data[:-5]}_episode_info')
    markup.add(personal)
    markup.add(episode)
    char = call.data[:-5]
    char2 = char_to_char[char]
    if char in characters:
        bot.send_photo(
            chat_id=call.from_user.id,
            photo=open(f'./pics/{char}.png', 'rb'),
            caption=per_info[char2]['short_info'])
    bot.send_message(
        chat_id=call.from_user.id,
        text='Choose which iformation you want to learn',
        reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.endswith('personal_info'))
def send_statistics(call):
    char_top = call.data[:-14].split('_')
    char = char_top[0]
    char1 = char_to_char[char]
    topics = list(per_info[char1]['gen_info'].keys())
    markup = types.InlineKeyboardMarkup()
    for i in range(0, len(topics)-1, 2):
        markup.add(types.InlineKeyboardButton(topics[i][:-1], callback_data=f'{char}_{topics[i]}_personal_info'),
                    types.InlineKeyboardButton(topics[i+1][:-1], callback_data=f'{char}_{topics[i+1]}_personal_info'))
    markup.add(types.InlineKeyboardButton(topics[-1][:-1], callback_data=f'{char}_{topics[-1]}_personal_info'))
    markup.add(types.InlineKeyboardButton('Return to the characters', callback_data='button2'))
    if len(char_top) == 1:
        bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text = 'Choose the topic',
            reply_markup=markup,
            parse_mode="Markdown")
    elif len(char_top) == 2:
        topic = char_top[1]
        char = char_to_char[char]
        info = per_info[char]
        general_info = info['gen_info']
        bot_message = f'*{topic}*\n{general_info[topic]}'
        bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text = bot_message,
            reply_markup=markup,
            parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data.endswith('episode_info'))
def send_statistics(call):
    markup = types.InlineKeyboardMarkup()
    main_menu = types.InlineKeyboardButton(text="Get back to main menu", callback_data="main_menu")
    next_character = types.InlineKeyboardButton(text='Choose again', callback_data='button2')
    markup.add(main_menu)
    markup.add(next_character)
    char = call.data[:-13]
    com_words = '\n'.join([f'\'{word[0]}\' was used {word[1]} times' for word in char_info[char]['most_words']])
    bot_message = f"*Average length of a line:* {char_info[char]['length']}\n" + \
        f'*Most used words:* \n{com_words}' + '\n' + \
        f"*Number of episodes:* {char_info[char]['count_episodes']}"
    bot.send_photo(
        chat_id=call.from_user.id, 
        photo=open(char_info[char]['wordcloud'], 'rb'),
        caption = bot_message,
        reply_markup=markup,
        parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.endswith('_cnt'))
def send_another_stat(call):
    markup = types.InlineKeyboardMarkup()
    main_menu = types.InlineKeyboardButton(text="Get back to main menu", callback_data="main_menu")
    next_character = types.InlineKeyboardButton(text='Choose again', callback_data='button2')
    markup.add(main_menu)
    markup.add(next_character)
    stat = ep_info[call.data]
    if call.data == 'lines_cnt':
        stat = [f'_{k}_ has {v} lines' for k, v in sorted(stat.items(), key=lambda x: x[1], reverse=True)]
        most_stat = '\n'.join(stat[:3])
        least_stat = '\n'.join(stat[3:])
        bot_message = f"*Most lines*:\n{most_stat}\n" + \
            f"*Least lines*:\n{least_stat}"
        bot.send_photo(
            chat_id=call.from_user.id,
            photo=open('./pics/Sponge Bobs Big Birthday Blowout.png', 'rb'))
        bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id, 
            text=bot_message,
            reply_markup=markup,
            parse_mode="Markdown")
    else:
        stat = [(k, v) for k, v in sorted(stat.items(), key=lambda x: x[1][0], reverse=True)]
        bot_message_most = '*Most characters:*\n'
        bot_message_least = '*Least characters:*\n'
        for i, item in enumerate(stat):
            if i >= 3:
                c = ', '.join(item[1][1])
                bot_message_least += f'_{item[0]}_ has {item[1][0]} characters: {c}\n'
            else:
                bot_message_most += f'_{item[0]}_ has {item[1][0]} characters\n'
        bot_message = bot_message_most + bot_message_least
        bot.send_photo(
        chat_id=call.from_user.id,
        photo=open('./pics/Sponge Bobs Big Birthday Blowout.png', 'rb'))
        bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id, 
            text=bot_message,
            reply_markup=markup,
            parse_mode="Markdown")

@bot.callback_query_handler(lambda call: call.data == 'another_stats')
def send_another_stat(call):
    markup = types.InlineKeyboardMarkup()
    stat_lines =  types.InlineKeyboardButton(text="Lines statistics", callback_data="lines_cnt")
    stat_characters = types.InlineKeyboardButton(text="Characters statistics", callback_data="chatacters_cnt")
    markup.add(stat_lines, stat_characters)
    bot.edit_message_text(
        chat_id=call.from_user.id,
        message_id=call.message.message_id, 
        text='Choose the statistics you want to know',
        reply_markup=markup)

@bot.callback_query_handler(lambda call: call.data == 'button2')
def choose_statistics(call):
    markup = types.InlineKeyboardMarkup(row_width=2) # по умолчанию 3
    for i in range(0, len(characters)-1, 2):
        markup.add(types.InlineKeyboardButton(characters[i], callback_data=f'{characters[i]}_stat'),
                    types.InlineKeyboardButton(characters[i+1], callback_data=f'{characters[i+1]}_stat'))
    markup.add(types.InlineKeyboardButton(text='Another statistics', callback_data=f'another_stats'))
    markup.add(types.InlineKeyboardButton(text='Return to the main menu', callback_data=f'main_menu'))
    bot.send_message(
        chat_id=call.from_user.id, 
        text=f'Choose the character', 
        reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in characters)
def answer(call):
    answer_markup = types.InlineKeyboardMarkup(row_width=2)
    new_sent = types.InlineKeyboardButton(text="New sentence", callback_data="button1.2")
    game_exit = types.InlineKeyboardButton(text="The end of the game", callback_data="end")
    answer_markup.add(new_sent)
    answer_markup.add(game_exit)
    bot.answer_callback_query(call.id)
    global answer
    if call.message:
        if call.data == answer:
            db.add_item_rates(user_id=call.from_user.id, user_ans=call.data, correct_ans=answer, if_correct=1)
            bot.send_sticker(
                chat_id=call.from_user.id,
                sticker=random.choice(happy))
            bot.edit_message_text(
                chat_id=call.from_user.id, 
                message_id=call.message.message_id, 
                text='You\'re right!', 
                reply_markup=answer_markup)
        else:
            db.add_item_rates(user_id=call.from_user.id, user_ans=call.data, correct_ans=answer, if_correct=0)
            bot.send_sticker(
                chat_id=call.from_user.id,
                sticker=random.choice(sad))
            bot.edit_message_text(
                chat_id=call.from_user.id, 
                message_id=call.message.message_id, 
                text=f'Oh no, it was {answer}', 
                reply_markup=answer_markup)

@bot.callback_query_handler(func=lambda call: call.data == 'end')
def end_of_the_game(call):
    markup = types.InlineKeyboardMarkup()
    main_menu = types.InlineKeyboardButton(text="Get to the main menu", callback_data="main_menu")
    markup.add(main_menu)
    bot_answer = db.get_statistics(user_id=call.from_user.id)
    bot.edit_message_text(
        chat_id=call.from_user.id, 
        message_id=call.message.message_id,
        text=bot_answer,
        parse_mode="Markdown",
        reply_markup=markup)

@bot.callback_query_handler(lambda call: call.data in ['button1', 'button1.2'])
def speech_game(call):
    markup = types.InlineKeyboardMarkup(row_width=2) # по умолчанию 3
    for i in range(0, len(characters)-1, 2):
        markup.add(types.InlineKeyboardButton(characters[i], callback_data=characters[i]),
                    types.InlineKeyboardButton(characters[i+1], callback_data=characters[i+1]))
    markup.add(types.InlineKeyboardButton(characters[-1], callback_data=characters[-1]))
    global answer
    if call.data == 'button1':
        game_rules = '*RULES*\n' + \
            'The bot will send you a sentence which was ' + \
            'the line of one of the character or was made by the model. ' + \
            'Your aim is to guess who said the line or was it artificially created'
        bot.send_message(
            call.message.chat.id, 
            text=game_rules,
            parse_mode='Markdown')
        answer = random.choice(list(who_to_guess.keys()))
        if answer == 'Model':
            char = random.choice(list(who_to_guess['Model'].keys()))
            bot.send_message(
                chat_id=call.message.chat.id,  
                text=who_to_guess['Model'][char].make_sentence(), 
                reply_markup=markup)
        else:
            bot.send_message(
                chat_id=call.message.chat.id,  
                text=random.choice(who_to_guess[answer]), 
                reply_markup=markup)
    else:
        answer = random.choice(list(who_to_guess.keys()))
        if answer == 'Model':
            char = random.choice(list(who_to_guess['Model'].keys()))
            bot.send_message(
                chat_id=call.message.chat.id,  
                text=who_to_guess['Model'][char].make_sentence(), 
                reply_markup=markup)
        else:
            bot.send_message(
                chat_id=call.message.chat.id,  
                text=random.choice(who_to_guess[answer]), 
                reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ['main_menu', 'start_bot'])
def main_menu(call):
    if call.data == 'start_bot':
        first = db.check(call.from_user.id)
        if first == None:
            db.add_item_users(user_id=call.from_user.id, name=call.from_user.first_name)
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="Speech Game", callback_data="button1")
    button2 = types.InlineKeyboardButton(text='Interesting Facts', callback_data='button2')
    button3 = types.InlineKeyboardButton(text='Get statistics', callback_data='button3')
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    bot.send_message(
        chat_id=call.from_user.id,
        text=f"{call.from_user.first_name}, choose the button to start a game, learn some interesting facts or get the statistics",
        reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'name')
def get_name(call):
    bot_message = f"{call.from_user.first_name}, please, write the nickname you want the bot to use in the Leaderboard. You should write it starting with \'&\' symbol.\n*Example*: &SpongeBob\n" + \
    "Otherwise, your user name will be added to the Leaderboard."
    bot.send_message(
        chat_id=call.from_user.id, 
        text=bot_message,
        parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text.startswith('&'))
def add_name(message):
    print(message.text[1:])
    db.add_item_users(user_id=message.from_user.id, name=message.text[1:])
    keyboard = types.InlineKeyboardMarkup()
    start = types.InlineKeyboardButton(text='Start Bot', callback_data='main_menu')
    keyboard.add(start)
    bot.send_message(
        chat_id=message.chat.id, 
        text='Well done! Press the button to start!',
        reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = types.InlineKeyboardMarkup()
    change_name = types.InlineKeyboardButton(text="Set/change name", callback_data="name")
    start = types.InlineKeyboardButton(text='Start Bot', callback_data='start_bot')
    keyboard.add(change_name)
    keyboard.add(start)
    bot_message = f"Hello, {message.from_user.first_name}! It's a Square Pants bot!\n" + \
    "- If you are tired of the routine, you can play a little game on guessing the character by his or her line in the TV series.\n" + \
    "- Another way to brighten up your life is to learn something new about the characters or about the episodes. You can find some interesting facts in the second section.\n" + \
    "- The last but not least, this bot saves the result of your games and games of other users so you can learn your personal statistics and the leadership in the third section!\n" + \
    "-" * 15 + \
    "\nIf you have not used this bot yet, press the button to set (or change) your nickname to use it in the Leaderboard. Otherwise, your user name will be used."
    bot.send_message(
        chat_id=message.chat.id, 
        text=bot_message,
        reply_markup=keyboard,
        parse_mode='Markdown')
    
@bot.message_handler(func=lambda m: True)
def add_name(message):
    bot.send_message(
        chat_id=message.chat.id,
        text='I don\'t understand. Please, write /start to return to the bot.')
    bot.send_sticker(
        chat_id=message.chat.id,
        sticker=random.choice(funny))


if __name__ == '__main__':
    bot.polling(none_stop=True)
