import json
from urllib.parse import quote, quote_plus, unquote_plus

from aiogram import types, F
from aiogram.types import InlineKeyboardMarkup

from config import dp, ROOM_MANAGER
from utlis.web_scarper import Movie

users = {}

@dp.message(F.text == '/start')
async def start_command(message: types.Message):
    keyboard = types.InlineKeyboardButton(text='Kino qidirsh', switch_inline_query_current_chat='')
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=[[keyboard]])
    await message.reply('Kino botga xush kelibsiz, kino qidirish uchun quyidagi tugmani bosing.\n\n'
                    'Televizorda tomosha qilish uchun esa televizordan https://4study.uz/ saytiga kiring va botga\n kodni /tv "kod" shaklida kiriting.\n'
                    'Masalan /tv 1403', reply_markup=reply_markup)


@dp.message(F.text.startswith('/tv'))
async def save_tv_code(message: types.Message):
    if ' ' not in message.text:
        if message.from_user.id in users:
            await message.reply(f'Hozirda {users[message.from_user.id]} TV boshqarilmoqda')
        else:
            await message.reply('Boshqarilayotgan TV mavjud emas')
        return
    tv_code = message.text.split(' ')[1]
    if tv_code.isnumeric():
        if tv_code in ROOM_MANAGER and not ROOM_MANAGER[tv_code]['user']:
            ROOM_MANAGER[tv_code]['user'] = message.from_user.id
            await ROOM_MANAGER[tv_code]['tv'].send_json({'type': 'change_owner', 'owner': message.from_user.full_name})
            users[message.from_user.id] = tv_code
            await message.reply('TV ulandi')
        else:
            await message.reply('TV topilmadi')
    else:
        await message.reply('TV kod xato')


@dp.inline_query()
async def search_movie_inline(query: types.InlineQuery):
    movie_prompt = query.query
    result = await Movie.search(movie_prompt)
    inline_answer = []
    for movie_id, movie in enumerate(result):
        movie_data = quote_plus(json.dumps(
            movie.dump_json()
        ))
        inline_answer.append(types.InlineQueryResultArticle(
            id=str(movie_id),
            title=movie.title,
            input_message_content=types.InputTextMessageContent(
                message_text=f"cinema={movie_data}",
            ),
            thumb_url=movie.picture,
            description=movie.info,
        ))
    await query.answer(inline_answer, cache_time=0)


@dp.message(F.text.startswith('cinema='))
async def get_cinema(message: types.Message):
    cinema_data = message.text[7:]
    movie = Movie(**json.loads(unquote_plus(cinema_data)))
    await movie.approve_videos()

    keyboards = []
    for video in movie.videos:
        keyboards.append([])
        keyboards[-1].append(
            types.InlineKeyboardButton(text=video.quality, url=video.url)
        )
        keyboards[-1].append(
            types.InlineKeyboardButton(text='TV da ko\'rish', callback_data=f"tv:{video.quality}")
        )
    caption = f"<b>{movie.title}</b>\n<i>{movie.info}</i>\n\n{movie.description}"
    caption = caption if len(caption) < 1025 else caption[:1021] + '...'
    await message.answer_photo(photo=movie.picture, caption=caption,
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboards))


@dp.callback_query()
async def show_cinema_in_tv(call: types.CallbackQuery):
    if call.from_user.id not in users:
        return await call.answer('TV ulanmagan', show_alert=True)
    quality = call.data[3:]
    video_url = str()
    for buttons in call.message.reply_markup.inline_keyboard:
        if buttons[0].text == quality:
            video_url = buttons[0].url
            break
    if users[call.from_user.id] not in ROOM_MANAGER:
        return await call.answer('TV uzilgan', show_alert=True)
    user_websocket = ROOM_MANAGER[users[call.from_user.id]]['tv']
    await user_websocket.send_json({"type": "play_video", "url": video_url})
    await call.answer('Kino qo\'yildi', show_alert=True)
