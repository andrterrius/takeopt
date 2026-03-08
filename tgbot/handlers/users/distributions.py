from aiogram.types import CallbackQuery, Message
from aiogram import Router

from aiogram.utils.i18n import gettext as _
from aiogram.utils.deep_linking import create_start_link
from aiogram.filters import CommandStart


from tgbot.db.repositories.repository import Repository
from tgbot.db.models import DBDistribution

from tgbot.misc.logger import logger
from tgbot.misc import callback_factory
from tgbot.misc.telegram_utils import get_telegram_username

from tgbot.query import DistributionQuery
from tgbot.distribution.services import DistributionKeyboardUpdater

from tgbot.distribution import ProcessingStatus
from tgbot.distribution.exceptions import ThrottlingChoiceException, LimitChoiceException, CancelChoiceException

from sqlalchemy.exc import IntegrityError, PendingRollbackError

from tgbot.factory.choice_processor import ChoiceProcessorFactory

from sqlalchemy.ext.asyncio import AsyncSession

from redis.asyncio import Redis

distributions_router = Router()

@distributions_router.message(CommandStart(deep_link=True))
async def bot_start_with_deeplink(message: Message, command: CommandStart, repo: Repository):
    args = command.args
    if args:
        distribution_uuid = args
        try:
            distribution_info = await repo.distributions.get_by_uuid(distribution_uuid)
            if distribution_info:
                list_choices = await repo.choices.get_all_choices_by_distribution_id(distribution_info.id)

                if not list_choices:
                    return await message.answer(_("Еще никто не выбрал варианты"))

                answer_text = _("Список занятых вариантов:")
                for choice in list_choices:
                    user_text = await get_telegram_username(message.bot, choice.user_id)
                    if user_text.isdigit():
                        user_text = f"{('@' + choice.user.username) if choice.user.username else choice.user.name} ({choice.user_id})"
                    answer_text += f"\n{choice.button_index} - {user_text}"

                return await message.answer(answer_text)
            else:
                return await message.answer(_("Это распределение вариантов не найдено"))
        except:
            return await message.answer(_("Произошла ошибка при поиске распределения вариантов!"))

@distributions_router.callback_query(callback_factory.CreateDistribution.filter())
async def callbacks_create_distribution(call: CallbackQuery, callback_data: callback_factory.CreateDistribution,
                                        repo: Repository,
                                        session: AsyncSession):
    distribution_query = DistributionQuery(callback_data.query)
    distribution_data = distribution_query.data

    new_distribution = DBDistribution(creator_id=call.from_user.id, query=distribution_query.get_pretty_query(),
                                      range_data=distribution_data.range_data,
                                      count_choices=distribution_data.count_choices)

    created_distribution = await repo.distributions.save_distribution(new_distribution)
    created_distribution_id = created_distribution.id
    created_distribution_uuid = created_distribution.uuid
    await session.commit()

    async with session.begin():
        distribution_deeplink = await create_start_link(call.bot, created_distribution_uuid)
        await DistributionKeyboardUpdater.update_distribution_keyboard(call, repo, created_distribution_id, distribution_deeplink, text=_("❓- основная информация"))

@distributions_router.callback_query(callback_factory.MakeChoice.filter())
async def callbacks_make_choice(call: CallbackQuery, callback_data: callback_factory.MakeChoice, repo: Repository,
                                session: AsyncSession, redis: Redis):
    user_id = call.from_user.id
    distribution_id = callback_data.distribution_id
    choiced_index = callback_data.choiced_index

    try:
        choice_processor = ChoiceProcessorFactory.create(
            user_id=user_id,
            distribution_id=distribution_id,
            choiced_index=choiced_index,
            redis=redis,
            repo=repo
        )

        process_status = await choice_processor.start_processing()
        if process_status is ProcessingStatus.CHOICED:
            await call.answer(_("✅ Ты успешно ВЫБРАЛ вариант {choiced_index}!").format(choiced_index=choiced_index), show_alert=True)
            await choice_processor.update_after_success()
        elif process_status is ProcessingStatus.CANCELED:
            await call.answer(_("✅ Ты успешно ОТМЕНИЛ выбор вариант {choiced_index}!").format(choiced_index=choiced_index), show_alert=True)
            choiced_index = None
        elif process_status is ProcessingStatus.PREPARED:
            await call.answer(_("⚠️ Для отмены {choiced_index} варианта нажми на эту же кнопку еще раз!").format(choiced_index=choiced_index), show_alert=True)

        await session.commit()

        async with session.begin():
            distribution_uuid = await repo.distributions.get_uui_by_id(distribution_id)
            distribution_deeplink = await create_start_link(call.bot, distribution_uuid)
            await DistributionKeyboardUpdater.update_distribution_keyboard(call, repo, distribution_id, distribution_deeplink,
                                                          choiced_index)
    except (IntegrityError, PendingRollbackError):
        await call.answer(_("❌ Этот вариант уже занят!"), show_alert=True)
    except (CancelChoiceException, LimitChoiceException, ThrottlingChoiceException)  as e:
        await call.answer(str(e), show_alert=True)
    except Exception as e:
        logger.error(f"❌ Поймали необработанное исключение: {type(e)}, {e}. user_id: {user_id}, distribution_id: {distribution_id}, choiced_index: {choiced_index}")
        await call.answer(_("Произошла ошибка!"), show_alert=True)

@distributions_router.callback_query(callback_factory.GetMyDistributionChoices.filter())
async def callbacks_get_list_my_choices(call: CallbackQuery, callback_data: callback_factory.GetMyDistributionChoices, repo: Repository):
    distribution_id = callback_data.distribution_id

    list_choices = await repo.choices.get_user_choices_by_distribution_id(distribution_id, call.from_user.id)

    if not list_choices:
        return await call.answer(_("Ты еще не выбрал варианты"), show_alert=True)

    answer_text = _("Ты выбрал:")
    for choice in list_choices:
        answer_text += f"\n{choice.button_index} ✅"

    return await call.answer(answer_text, show_alert=True)

@distributions_router.callback_query(callback_factory.GetHelp.filter())
async def callbacks_get_help(call: CallbackQuery):
    return await call.answer(_("Для выбора варианта жми 🟢\n"
                               "\n🟢 - свободный вариант"
                               "\n🔴 - занятый вариант (для отмены своего занятого варианта нужно 2 раза нажать на свой вариант)"
                               "\n👤 - список твоих вариантов"
                               "\n📄 - список занятых вариантов"), show_alert=True)