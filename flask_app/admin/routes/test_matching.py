from extensions.cognito import require_auth
from extensions.logging import get_logger
from flask import Blueprint, render_template

logger = get_logger(__name__)
test_matching_bp = Blueprint('test_matching', __name__)

# Load dashboard/test_matching.html when visiting
@test_matching_bp.route('/test_matching')
@require_auth
def test_matching():
    """
    Render the test matching page.
    """
    logger.info("Rendering test matching page")
    return render_template('dashboard/test_matching.html')
