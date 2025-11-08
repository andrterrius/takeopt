from aiogram.types import CallbackQuery
from aiogram import Router

from aiogram.utils.i18n import gettext as _


from tgbot.db.repositories.repository import Repository
from tgbot.db.models import DBDistribution

from tgbot.misc.logger import logger
from tgbot.misc import callback_factory
from tgbot.misc.telegram_utils import get_telegram_username

from tgbot.core.query.query import DistributionQuery
from tgbot.core.distribution.services.keyboard_updating import DistributionKeyboardUpdater as kb_updater

from tgbot.core.distribution.interfaces import ProcessingStatus
from tgbot.core.distribution.exceptions import ThrottlingChoiceException, LimitChoiceException, CancelChoiceException

from sqlalchemy.exc import IntegrityError, PendingRollbackError

from tgbot.factory.choice_processor_factory import ChoiceProcessorFactory

from sqlalchemy.ext.asyncio import AsyncSession

from redis.asyncio import Redis

distributions_router = Router()

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
    await session.commit()

    async with session.begin():
        await kb_updater.update_distribution_keyboard(call, repo, created_distribution_id, text=_("❓- основная информация"))

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
            await choice_processor.update_user_choices()
        elif process_status is ProcessingStatus.CANCELED:
            await call.answer(_("✅ Ты успешно ОТМЕНИЛ выбор вариант {choiced_index}!").format(choiced_index=choiced_index), show_alert=True)
            choiced_index = None
        elif process_status is ProcessingStatus.PREPARED:
            await call.answer(_("⚠️ Для отмены {choiced_index} варианта нажми на эту же кнопку еще раз!").format(choiced_index=choiced_index), show_alert=True)

        await session.commit()

        async with session.begin():
            await kb_updater.update_distribution_keyboard(call, repo, distribution_id,
                                                          choiced_index)
    except (IntegrityError, PendingRollbackError):
        await call.answer(_("❌ Этот вариант уже занят!"), show_alert=True)
    except (CancelChoiceException, LimitChoiceException, ThrottlingChoiceException)  as e:
        await call.answer(str(e), show_alert=True)
    except Exception as e:
        logger.error(f"❌ Поймали необработанное исключение: {type(e)}, {e}. user_id: {user_id}, distribution_id: {distribution_id}, choiced_index: {choiced_index}")
        await call.answer(_("Произошла ошибка!"), show_alert=True)

@distributions_router.callback_query(callback_factory.GetDistributionChoices.filter())
async def callbacks_get_list_choices(call: CallbackQuery, callback_data: callback_factory.GetDistributionChoices, repo: Repository):
    distribution_id = callback_data.distribution_id

    list_choices = await repo.choices.get_all_choices_by_distribution_id(distribution_id)

    if not list_choices:
        return await call.answer(_("Еще никто не выбрал варианты"), show_alert=True)

    answer_text = ""
    for choice in list_choices:
        user_text = await get_telegram_username(call.bot, choice.user_id)
        answer_text += f"\n{choice.button_index} - {user_text}"

    return await call.answer(answer_text, show_alert=True)

@distributions_router.callback_query(callback_factory.GetHelp.filter())
async def callbacks_get_help(call: CallbackQuery):
    return await call.answer(_("Для выбора варианта жми 🟢\n"
                               "\n🟢 - свободный вариант"
                               "\n🔴 - занятый вариант (для отмены своего занятого варианта нужно 2 раза нажать на свой вариант)"
                               "\n📄 - список занятых вариантов"), show_alert=True)