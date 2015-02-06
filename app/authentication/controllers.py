from flask import Blueprint

from app.shared.functions import get_config
from app.authentication.views import (
    LoginView, LogoutView, SignupView, RefreshAuthView
)

__all__ = [
    'mod_auth'
]

mod_auth = Blueprint('auth', __name__)

mod_auth.add_url_rule(
    '/',
    view_func=LoginView.as_view('root')
)
mod_auth.add_url_rule(
    '/login/',
    view_func=LoginView.as_view('login')
)
mod_auth.add_url_rule(
    '/logout/',
    view_func=LogoutView.as_view('logout')
)
mod_auth.add_url_rule(
    '/signup/',
    view_func=SignupView.as_view('signup')
)
mod_auth.add_url_rule(
    '/refresh/',
    view_func=RefreshAuthView.as_view('refresh')
)
