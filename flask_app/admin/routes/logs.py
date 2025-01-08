import os
import glob
from flask import Blueprint, render_template, current_app, jsonify
from datetime import datetime
from flask import request

logs_bp = Blueprint('logs', __name__, url_prefix='/logs')

def get_log_files():
    """Get list of available log files sorted by modification time"""
    log_dir = os.path.dirname(current_app.root_path)
    log_files = glob.glob(os.path.join(log_dir, '*.log*'))
    log_files = [(os.path.basename(f), 
                  datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%d %H:%M:%S'))
                 for f in log_files]
    return sorted(log_files, key=lambda x: x[1], reverse=True)

def read_log_file(filename):
    """Read and return log file contents"""
    log_path = os.path.join(os.path.dirname(current_app.root_path), filename)
    if os.path.exists(log_path) and os.path.isfile(log_path):
        with open(log_path, 'r') as f:
            return f.readlines()[::-1]  # Reverse to show newest first
    return []

@logs_bp.route('/')
def logs_page():
    """Render logs page"""
    log_files = get_log_files()
    selected_log = request.args.get('file', 'app.log')
    tail_mode = request.args.get('tail', 'false') == 'true'
    
    log_content = read_log_file(selected_log)
    if tail_mode:
        log_content = log_content[:1000]  # Show last 1000 lines in tail mode
        
    return render_template('dashboard/logs.html', 
                         log_files=log_files,
                         current_log=log_content,
                         selected_log=selected_log,
                         tail_mode=tail_mode)
