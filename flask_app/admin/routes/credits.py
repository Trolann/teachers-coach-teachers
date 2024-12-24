from flask import Blueprint
from extensions.logging import get_logger
from os import path
from models.credits import CreditRedemption, CreditTransfer

logger = get_logger(__name__)

# Get the current directory path
current_dir = path.dirname(path.abspath(__file__))
template_dir = path.join(current_dir, '..', 'templates')
static_dir = path.join(current_dir, '..', 'static')

# Create blueprint with template folder specified
admin_credits_bp = Blueprint('admin_credits', __name__,
                               static_folder=static_dir,
                               static_url_path='/admin/static',
                               template_folder=template_dir)


@admin_credits_bp.route('/', methods=['GET', 'POST'])
def index():
    logger.debug('Rendering admin credits page')
    return 'Admin credits page'