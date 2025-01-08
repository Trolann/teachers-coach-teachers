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
    """Read and return log file contents with parsed log levels"""
    log_path = os.path.join(os.path.dirname(current_app.root_path), filename)
    if os.path.exists(log_path) and os.path.isfile(log_path):
        with open(log_path, 'r') as f:
            lines = f.readlines()
            # Parse each line to extract log level
            parsed_lines = []
            for line in lines:
                if '[DEBUG]' in line:
                    level = 'DEBUG'
                elif '[INFO]' in line:
                    level = 'INFO'
                elif '[WARNING]' in line:
                    level = 'WARNING'
                elif '[ERROR]' in line:
                    level = 'ERROR'
                elif '[CRITICAL]' in line:
                    level = 'CRITICAL'
                else:
                    level = None
                parsed_lines.append({'content': line.strip(), 'level': level})
            return parsed_lines[::-1]  # Reverse to show newest first
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
