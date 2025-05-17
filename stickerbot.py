# https://t.me/StickersAndSetsBot
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand
import asyncio
from PIL import Image
import os
import logging
import sys
import random
bot = Bot(token='7749781181:AAFaHT1HJkv_9BQn6DHpHIU3j5AmfhPts5I')
dp = Dispatcher()
emoji = ['😃', '😄', '😁', '😆', '🥹', '😅', '😂', '🤣', '🥲', '😊', '😇', '🙂', '🙃', '😉', '😌',
         '😍', '🥰', '😘', '😗', '😙', '😚', '😋', '😛', '😝', '😜', '🤪', '🤨', '🧐', '🤓', '😎',
         '🥸', '🤩', '🥳', '😏', '😒', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣', '😖', '😫', '😩',
         '🥺', '😢', '😭', '😤', '😠', '😡', '🤬', '🤯', '😳', '🥵', '🥶', '😱', '😨', '😰', '😥',
         '😓', '🤗', '🤔', '🫣', '🤭', '🫢', '🫡', '🤫', '🫠', '🤥', '🫥', '😐', '🫤', '😑', '😬',
         '🙄', '😯', '😦', '😧', '😮', '😲', '🥱', '😴', '🤤', '😪', '😵', '🤐', '🥴', '🤢', '🤮',
         '🤧', '😷', '🤒', '🤕', '🤑', '🤠', '😈', '👿', '👹', '👺', '🤡', '💩', '👻', '💀', '️👽',
         '👾', '🤖', '🎃', '😺', '😸', '😹', '😻', '😼', '😽', '🙀', '😿', '😾']
if not os.path.exists('temp'):
    os.makedirs('temp')


class NewSticker(StatesGroup):
    first_name = State()
    name = State()
    first_sticker = State()
    next_sticker = State()


def image(fname: str) -> str:
    sname = fname.replace('.png', '_resized.png')
    with Image.open(fname) as img:
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        empty = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        x1 = (512 / img.size[0])
        y1 = (512 / img.size[1])
        x11 = int(img.size[0] * min(x1, y1))
        y11 = int(img.size[1] * min(x1, y1))
        rimg = img.resize((x11, y11))
        x = (512 - x11) // 2
        y = (512 - y11) // 2
        empty.paste(rimg, (x, y), rimg)
        empty.save(sname, 'PNG')
    os.remove(fname)
    return sname


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer('Добрый день! Я помогу создать стикерпак. Выберите в меню команду /create,'
                         'чтобы создать новый стикерпак или /change, чтобы изменить уже созданный в '
                         'этом боте набор стикеров. Чтобы завершить работу используйте команду /end.')


@dp.message(Command('create'))
async def create(message: types.Message, state: FSMContext):
    await message.answer('Отправьте название для вашего стикерпака. Название может содержать английские буквы, цифры.')
    await state.set_state(NewSticker.first_name)


@dp.message(NewSticker.first_name)
async def pack_name(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer('Отправьте фотографию для вашего стикера.')
    await state.set_state(NewSticker.first_sticker)


@dp.message(NewSticker.first_sticker, F.photo)
async def creating_first_sticker_and_pack(message: types.Message, state: FSMContext):
    try:
        file_d = f'temp/{message.photo[-1].file_id}.png'
        await bot.download(message.photo[-1].file_id, destination=file_d)
        file_end = image(file_d)
        inf = await bot.get_me()
        uid = message.from_user.id
        link = inf.username
        emoji_s = random.choice(emoji)
        data = await state.get_data()
        pack = f"pack{uid}_{data['title']}_by_{link}"
        await bot.create_new_sticker_set(
            user_id=uid,
            name=pack,
            title=data['title'],
            stickers=[{'sticker': types.FSInputFile(file_end), 'emoji_list': list(emoji_s), 'format': 'static'}],
            sticker_format='static')
        await state.update_data(pack_name=pack)
        os.remove(file_end)
        await message.answer('Стикерпак создан! Отправьте ещё фотографию или отправьте /end для завершения.')
        await state.set_state(NewSticker.next_sticker)
    except Exception as e:
        await message.answer(f'Произошла ошибка при создании стикерпака: {str(e)}')
        await state.clear()


@dp.message(NewSticker.next_sticker, F.photo)
async def creating_next_sticker(message: types.Message, state: FSMContext):
    try:
        file_d = f'temp/{message.photo[-1].file_id}.png'
        await bot.download(message.photo[-1].file_id, destination=file_d)
        file_end = image(file_d)
        inf = await bot.get_me()
        uid = message.from_user.id
        link = inf.username
        emoji_s = random.choice(emoji)
        data = await state.get_data()
        pack = f"pack{uid}_{data['title']}_by_{link}"
        await bot.add_sticker_to_set(
            user_id=uid,
            name=pack,
            sticker={'sticker': types.FSInputFile(file_end), 'emoji_list': list(emoji_s), 'format': 'static'})
        os.remove(file_end)
        await message.answer('Стикер успешно добавлен! Отправьте ещё фотографию или отправьте /end для завершения.')
    except Exception as e:
        await message.answer(f'Произошла ошибка при добавлении стикера: {str(e)}')
        await state.clear()


@dp.message(Command('change'))
async def change(message: types.Message, state: FSMContext):
    await message.answer('Введите название стикерпака, который хотите изменить.')
    await state.set_state(NewSticker.name)


@dp.message(NewSticker.name)
async def pack_name(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer('Отправьте фотографию для вашего стикера.')
    await state.set_state(NewSticker.next_sticker)


@dp.message(Command('end'))
async def finish_creation(message: types.Message, state: FSMContext):
    inf = await bot.get_me()
    uid = message.from_user.id
    link = inf.username
    data = await state.get_data()
    pack = f"pack{uid}_{data['title']}_by_{link}"
    await message.answer(f'Ваш стикерпак готов!\nt.me/addstickers/{pack}')
    await state.clear()


async def set_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start', description='начать работу бота'),
        BotCommand(command='/create', description='создать новый стикерпак'),
        BotCommand(command='/change', description='изменить существующий стикерпак(только из этого бота!)'),
        BotCommand(command='/end', description='закончить создание или изменение стикерпака')]
    await bot.set_my_commands(main_menu_commands)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    dp.startup.register(set_menu)
    asyncio.run(main())
