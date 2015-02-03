from app import app
from app.shared.functions import get_config

debug = get_config('DEBUG')

app.run(host='0.0.0.0', port=8000, debug=debug)
