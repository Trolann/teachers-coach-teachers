import os
import glob
from flask import Blueprint, render_template, current_app, jsonify
from datetime import datetime
from flask import request
from extensions.cognito import require_auth

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
            parsed_lines = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Extract timestamp (first 19 characters: YYYY-MM-DD HH:MM:SS)
                timestamp = line[:19] if len(line) >= 19 else ''

                # Look for level between module name and message
                # Pattern is typically: timestamp - module - LEVEL - message
                level = None
                parts = line.split(' - ')
                if len(parts) >= 3:
                    for part in parts:
                        part = part.strip()
                        if part in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                            level = part
                            break

                parsed_lines.append({
                    'content': line,
                    'level': level,
                    'timestamp': timestamp
                })
            return parsed_lines[::-1]  # Reverse to show newest first
    return []

@logs_bp.route('/')
@require_auth
def logs_page():
    """Render logs page"""
    log_files = get_log_files()
    selected_log = request.args.get('file', 'app.log')
    log_content = read_log_file(selected_log)
    
    return render_template('dashboard/logs.html', 
                         log_files=log_files,
                         current_log=log_content,
                         selected_log=selected_log)
