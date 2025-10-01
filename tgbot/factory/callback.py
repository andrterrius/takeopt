from aiogram.filters.callback_data import CallbackData


class CreateDistribution(CallbackData, prefix="distribution_"):
    query: str
    owner: int


class MakeChoice(CallbackData, prefix="make_choice_"):
    distribution_id: int
    choice_index: int
    is_free: bool
