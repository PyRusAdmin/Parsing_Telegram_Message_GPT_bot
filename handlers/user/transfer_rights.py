from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger
from playhouse.migrate import SqliteMigrator, migrate

from database.database import User, db
from states.states import MyStates

router = Router(name=__name__)


def rename_old_table_to_new_table(user_id, id_transfer_user):
    """Переименовывает таблицу в новую для пользователя"""

    # 1. Инициализируем мигратор
    migrator = SqliteMigrator(db)
    # 2. Выполняем миграцию: указываем старое имя таблицы и новое
    migrate(
        migrator.rename_table(f"{user_id}_keywords", f"{id_transfer_user}_keywords")
    )
    logger.warning("Таблица успешно переименована!")
    
    
    migrate(
        migrator.rename_table(f"{user_id}_group", f"{user_id}_group")
    )
    logger.warning("Таблица успешно переименована!")


@router.message(F.text == "🔄 Передать настройки пользователю")
async def transfer_settings(message: Message, state: FSMContext) -> None:
    await state.clear()  # Завершаем текущее состояние машины состояния

    await message.answer("Введите ID пользователя для передачи настроек:\n\nПример ввода - 1234567890")

    await state.set_state(MyStates.get_id_user_transfer)


@router.message(MyStates.get_id_user_transfer)
async def get_id_for_transferring(message, state: FSMContext, bot):
    user = User.get(User.user_id == message.from_user.id)
    id_transfer_user = message.text.strip()

    await state.clear()  # Завершаем текущее состояние машины состояния

    rename_old_table_to_new_table(
        user_id=message.from_user.id, 
        id_transfer_user=id_transfer_user

        )

    await message.answer(f"Настройки успешно переданы! пользователю с id {id_transfer_user}")
