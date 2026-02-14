from aiogram.filters.callback_data import CallbackData

class CreateDistribution(CallbackData, prefix="distribution_"):
    query: str
    owner: int


class MakeChoice(CallbackData, prefix="make_choice_"):
    distribution_id: int
    choiced_index: int

class GetMyDistributionChoices(CallbackData, prefix="get_my_distribution_choices_"):
    distribution_id: int

class GetHelp(CallbackData, prefix="get_help_"):
    pass