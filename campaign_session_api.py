"""
Campaign and Session Management API Endpoints
Handles creation, loading, and management of campaigns and sessions
"""

import sqlite3
import json
from datetime import datetime
from flask import jsonify, request, session

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('vtm_storyteller.db')
    conn.row_factory = sqlite3.Row
    return conn

# ==================== CAMPAIGN ENDPOINTS ====================

def get_all_campaigns():
    """Get all campaigns"""
    conn = get_db_connection()
    campaigns = conn.execute('''
        SELECT id, name, city, faction, status, total_sessions, created_at, updated_at
        FROM campaigns
        ORDER BY updated_at DESC
    ''').fetchall()
    conn.close()
    
    return jsonify([dict(c) for c in campaigns])

def get_campaign(campaign_id):
    """Get a specific campaign by ID"""
    conn = get_db_connection()
    campaign = conn.execute('''
        SELECT * FROM campaigns WHERE id = ?
    ''', (campaign_id,)).fetchone()
    conn.close()
    
    if campaign:
        return jsonify(dict(campaign))
    else:
        return jsonify({'error': 'Campaign not found'}), 404

def create_campaign():
    """Create a new campaign"""
    data = request.get_json()
    
    name = data.get('name')
    city = data.get('city', '')
    faction = data.get('faction', '')
    description = data.get('description', '')
    
    if not name:
        return jsonify({'error': 'Campaign name is required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO campaigns (name, city, faction, description, status, total_sessions, created_at, updated_at)
        VALUES (?, ?, ?, ?, 'active', 0, ?, ?)
    ''', (name, city, faction, description, datetime.now(), datetime.now()))
    
    campaign_id = cursor.lastrowid
    conn.commit()
    
    # Get the created campaign
    campaign = conn.execute('SELECT * FROM campaigns WHERE id = ?', (campaign_id,)).fetchone()
    conn.close()
    
    return jsonify(dict(campaign)), 201

def update_campaign(campaign_id):
    """Update an existing campaign"""
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build update query dynamically based on provided fields
    update_fields = []
    values = []
    
    for field in ['name', 'city', 'faction', 'description', 'status']:
        if field in data:
            update_fields.append(f'{field} = ?')
            values.append(data[field])
    
    if not update_fields:
        return jsonify({'error': 'No fields to update'}), 400
    
    update_fields.append('updated_at = ?')
    values.append(datetime.now())
    values.append(campaign_id)
    
    cursor.execute(f'''
        UPDATE campaigns
        SET {', '.join(update_fields)}
        WHERE id = ?
    ''', values)
    
    conn.commit()
    
    # Get the updated campaign
    campaign = conn.execute('SELECT * FROM campaigns WHERE id = ?', (campaign_id,)).fetchone()
    conn.close()
    
    return jsonify(dict(campaign))

def delete_campaign(campaign_id):
    """Delete a campaign"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM campaigns WHERE id = ?', (campaign_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Campaign deleted successfully'})

# ==================== SESSION ENDPOINTS ====================

def start_session():
    """Start a new session"""
    data = request.get_json()
    campaign_id = data.get('campaign_id')
    
    if not campaign_id:
        return jsonify({'error': 'Campaign ID is required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current session count for this campaign
    campaign = conn.execute('SELECT total_sessions FROM campaigns WHERE id = ?', (campaign_id,)).fetchone()
    
    if not campaign:
        conn.close()
        return jsonify({'error': 'Campaign not found'}), 404
    
    session_number = campaign['total_sessions'] + 1
    
    # Create new session record
    cursor.execute('''
        INSERT INTO campaign_sessions (campaign_id, session_number, start_time, status)
        VALUES (?, ?, ?, 'active')
    ''', (campaign_id, session_number, datetime.now()))
    
    session_id = cursor.lastrowid
    
    # Update campaign total_sessions and updated_at
    cursor.execute('''
        UPDATE campaigns
        SET total_sessions = ?, updated_at = ?
        WHERE id = ?
    ''', (session_number, datetime.now(), campaign_id))
    
    conn.commit()
    
    # Get the created session
    new_session = conn.execute('SELECT * FROM campaign_sessions WHERE id = ?', (session_id,)).fetchone()
    conn.close()
    
    # Store session ID in Flask session
    session['active_session_id'] = session_id
    session['active_campaign_id'] = campaign_id
    
    return jsonify(dict(new_session)), 201

def end_session():
    """End the current session"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id:
        session_id = session.get('active_session_id')
    
    if not session_id:
        return jsonify({'error': 'No active session'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update session record
    cursor.execute('''
        UPDATE campaign_sessions
        SET end_time = ?, status = 'completed'
        WHERE id = ?
    ''', (datetime.now(), session_id))
    
    conn.commit()
    
    # Get the updated session
    updated_session = conn.execute('SELECT * FROM campaign_sessions WHERE id = ?', (session_id,)).fetchone()
    conn.close()
    
    # Clear session data
    session.pop('active_session_id', None)
    
    return jsonify(dict(updated_session))

def get_session_summary(session_id):
    """Get summary of a session"""
    conn = get_db_connection()
    
    # Get session info
    session_data = conn.execute('SELECT * FROM campaign_sessions WHERE id = ?', (session_id,)).fetchone()
    
    if not session_data:
        conn.close()
        return jsonify({'error': 'Session not found'}), 404
    
    # Get events from this session
    events = conn.execute('''
        SELECT * FROM campaign_events
        WHERE campaign_id = ? AND created_at BETWEEN ? AND ?
        ORDER BY created_at
    ''', (session_data['campaign_id'], session_data['start_time'], session_data['end_time'] or datetime.now())).fetchall()
    
    # Get NPCs created/modified in this session
    npcs = conn.execute('''
        SELECT * FROM campaign_npcs
        WHERE campaign_id = ? AND created_at BETWEEN ? AND ?
    ''', (session_data['campaign_id'], session_data['start_time'], session_data['end_time'] or datetime.now())).fetchall()
    
    # Get locations created/modified in this session
    locations = conn.execute('''
        SELECT * FROM campaign_locations
        WHERE campaign_id = ? AND created_at BETWEEN ? AND ?
    ''', (session_data['campaign_id'], session_data['start_time'], session_data['end_time'] or datetime.now())).fetchall()
    
    # Get items created/modified in this session
    items = conn.execute('''
        SELECT * FROM campaign_items
        WHERE campaign_id = ? AND created_at BETWEEN ? AND ?
    ''', (session_data['campaign_id'], session_data['start_time'], session_data['end_time'] or datetime.now())).fetchall()
    
    conn.close()
    
    return jsonify({
        'session': dict(session_data),
        'events': [dict(e) for e in events],
        'npcs_created': [dict(n) for n in npcs],
        'locations_created': [dict(l) for l in locations],
        'items_created': [dict(i) for i in items]
    })

def get_campaign_sessions(campaign_id):
    """Get all sessions for a campaign"""
    conn = get_db_connection()
    sessions = conn.execute('''
        SELECT * FROM campaign_sessions
        WHERE campaign_id = ?
        ORDER BY session_number DESC
    ''').fetchall()
    conn.close()
    
    return jsonify([dict(s) for s in sessions])

# ==================== DATABASE QUERY ENDPOINTS ====================

def list_campaign_npcs(campaign_id):
    """List all NPCs in a campaign"""
    conn = get_db_connection()
    npcs = conn.execute('''
        SELECT id, name, real_name, clan, faction, status, tags
        FROM campaign_npcs
        WHERE campaign_id = ?
        ORDER BY name
    ''', (campaign_id,)).fetchall()
    conn.close()
    
    return jsonify([dict(n) for n in npcs])

def search_campaign_npcs(campaign_id, search_term):
    """Search for NPCs in a campaign"""
    conn = get_db_connection()
    npcs = conn.execute('''
        SELECT * FROM campaign_npcs
        WHERE campaign_id = ? AND (
            name LIKE ? OR
            real_name LIKE ? OR
            clan LIKE ? OR
            tags LIKE ?
        )
        ORDER BY name
    ''', (campaign_id, f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%')).fetchall()
    conn.close()
    
    return jsonify([dict(n) for n in npcs])

def list_campaign_locations(campaign_id):
    """List all locations in a campaign"""
    conn = get_db_connection()
    locations = conn.execute('''
        SELECT id, name, type, city, status, tags
        FROM campaign_locations
        WHERE campaign_id = ?
        ORDER BY name
    ''', (campaign_id,)).fetchall()
    conn.close()
    
    return jsonify([dict(l) for l in locations])

def search_campaign_locations(campaign_id, search_term):
    """Search for locations in a campaign"""
    conn = get_db_connection()
    locations = conn.execute('''
        SELECT * FROM campaign_locations
        WHERE campaign_id = ? AND (
            name LIKE ? OR
            type LIKE ? OR
            tags LIKE ?
        )
        ORDER BY name
    ''', (campaign_id, f'%{search_term}%', f'%{search_term}%', f'%{search_term}%')).fetchall()
    conn.close()
    
    return jsonify([dict(l) for l in locations])

def list_campaign_items(campaign_id):
    """List all items in a campaign"""
    conn = get_db_connection()
    items = conn.execute('''
        SELECT id, name, type, status, tags
        FROM campaign_items
        WHERE campaign_id = ?
        ORDER BY name
    ''', (campaign_id,)).fetchall()
    conn.close()
    
    return jsonify([dict(i) for i in items])

def search_campaign_items(campaign_id, search_term):
    """Search for items in a campaign"""
    conn = get_db_connection()
    items = conn.execute('''
        SELECT * FROM campaign_items
        WHERE campaign_id = ? AND (
            name LIKE ? OR
            type LIKE ? OR
            tags LIKE ?
        )
        ORDER BY name
    ''', (campaign_id, f'%{search_term}%', f'%{search_term}%', f'%{search_term}%')).fetchall()
    conn.close()
    
    return jsonify([dict(i) for i in items])

# ==================== HELPER FUNCTIONS ====================

def get_active_campaign_id():
    """Get the currently active campaign ID from session"""
    return session.get('active_campaign_id')

def get_active_session_id():
    """Get the currently active session ID from session"""
    return session.get('active_session_id')

def create_campaign_sessions_table():
    """Create campaign_sessions table if it doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaign_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER NOT NULL,
            session_number INTEGER NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            status TEXT DEFAULT 'active',
            notes TEXT,
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize sessions table on module load
create_campaign_sessions_table()

