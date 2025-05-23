
import os
from flask import Blueprint

# Get the absolute path to the assistans directory
assistans_dir = os.path.dirname(os.path.abspath(__file__))
static_folder = os.path.join(assistans_dir, 'static')

assistant_bp = Blueprint('assistant', __name__, 
                        template_folder='templates', 
                        static_folder=static_folder)

from . import routes
