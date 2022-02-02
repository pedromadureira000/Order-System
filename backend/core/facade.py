from core.models import User


def company_has_active_users(company):
    if type(company.user_set.filter(is_active=True).all().first()) == User:
        return True
    return False

