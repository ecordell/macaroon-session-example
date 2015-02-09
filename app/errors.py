from flask import render_template, current_app


def not_found(error):
    return render_template('404.html'), 404


def server_error(error):
    current_app.logger.exception(error)
    return render_template('500.html'), 500


def add_error_handlers(app):
    app.error_handler_spec[None][404] = not_found
    app.error_handler_spec[None][500] = server_error
