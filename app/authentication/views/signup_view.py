from flask import (request, render_template,
                   flash, redirect, url_for, g, current_app)
from flask.views import MethodView

from app.authentication.forms import SignupForm


class SignupView(MethodView):
    def __init__(self):
        super().__init__()
        self.redis = g.redis
        self.logger = current_app.logger

    def get(self):
        form = SignupForm(request.form)
        return render_template("auth/signup.html", form=form)

    def post(self):
        form = SignupForm(request.form)

        if form.validate_on_submit():
            try:
                self._create_account(
                    form.email.data,
                    form.password.data
                )
                flash('Signed up! Now log in.')
                return redirect(url_for('auth.login'))
            except Exception as e:
                self.logger.exception(e)
                flash('Error!')
        return render_template("auth/signup.html", form=form)

    def _create_account(self, username, password):
        pipeline = self.redis.pipeline()
        pipeline.set(username, password)
        pipeline.execute()
