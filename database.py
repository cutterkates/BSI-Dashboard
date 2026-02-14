import sqlite3
import pandas as pd
from datetime import datetime
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'bsi_kpi_data.db')

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with required tables"""
    conn = get_connection()
    cursor = conn.cursor()

    # Upload history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            month_year TEXT,
            record_count INTEGER
        )
    ''')

    # Company level metrics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            upload_id INTEGER,
            record_date DATE,
            month_year TEXT,
            member_net REAL,
            lead_to_member_pct REAL,
            lead_booked_pct REAL,
            appt_show_pct REAL,
            appt_close_pct REAL,
            ob_phone_calls_day REAL,
            downpayment_wo_tax REAL,
            fc_booking_pct REAL,
            show_pct REAL,
            close_pct REAL,
            avg_deal REAL,
            avg_fcs_day REAL,
            downpayments REAL,
            downpayment_pct REAL,
            tav REAL,
            revenue REAL,
            remaining_draft REAL,
            projected_revenue REAL,
            ob_phone_calls REAL,
            new_leads REAL,
            appt_scheduled REAL,
            appt_show_count REAL,
            total_tours REAL,
            walk_ins REAL,
            new_members REAL,
            downpayment_amount REAL,
            square_dps REAL,
            fcs_booked_pos REAL,
            fcs_made REAL,
            fcs_scheduled REAL,
            fcs_shows REAL,
            fcs_closes REAL,
            new_deals REAL,
            locations REAL,
            FOREIGN KEY (upload_id) REFERENCES uploads(id)
        )
    ''')

    # Territory level metrics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS territory_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            upload_id INTEGER,
            record_date DATE,
            month_year TEXT,
            territory_name TEXT,
            member_net REAL,
            lead_to_member_pct REAL,
            lead_booked_pct REAL,
            appt_show_pct REAL,
            appt_close_pct REAL,
            ob_phone_calls_day REAL,
            downpayment_wo_tax REAL,
            fc_booking_pct REAL,
            show_pct REAL,
            close_pct REAL,
            avg_deal REAL,
            avg_fcs_day REAL,
            downpayments REAL,
            downpayment_pct REAL,
            tav REAL,
            revenue REAL,
            remaining_draft REAL,
            projected_revenue REAL,
            ob_phone_calls REAL,
            new_leads REAL,
            appt_scheduled REAL,
            appt_show_count REAL,
            total_tours REAL,
            walk_ins REAL,
            new_members REAL,
            downpayment_amount REAL,
            square_dps REAL,
            fcs_booked_pos REAL,
            fcs_made REAL,
            fcs_scheduled REAL,
            fcs_shows REAL,
            fcs_closes REAL,
            new_deals REAL,
            locations REAL,
            FOREIGN KEY (upload_id) REFERENCES uploads(id)
        )
    ''')

    # Region level metrics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS region_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            upload_id INTEGER,
            record_date DATE,
            month_year TEXT,
            territory_name TEXT,
            region_name TEXT,
            member_net REAL,
            lead_to_member_pct REAL,
            lead_booked_pct REAL,
            appt_show_pct REAL,
            appt_close_pct REAL,
            ob_phone_calls_day REAL,
            downpayment_wo_tax REAL,
            fc_booking_pct REAL,
            show_pct REAL,
            close_pct REAL,
            avg_deal REAL,
            avg_fcs_day REAL,
            downpayments REAL,
            downpayment_pct REAL,
            tav REAL,
            revenue REAL,
            remaining_draft REAL,
            projected_revenue REAL,
            ob_phone_calls REAL,
            new_leads REAL,
            appt_scheduled REAL,
            appt_show_count REAL,
            total_tours REAL,
            walk_ins REAL,
            new_members REAL,
            downpayment_amount REAL,
            square_dps REAL,
            fcs_booked_pos REAL,
            fcs_made REAL,
            fcs_scheduled REAL,
            fcs_shows REAL,
            fcs_closes REAL,
            new_deals REAL,
            locations REAL,
            FOREIGN KEY (upload_id) REFERENCES uploads(id)
        )
    ''')

    # Club level metrics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS club_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            upload_id INTEGER,
            record_date DATE,
            month_year TEXT,
            territory_name TEXT,
            region_name TEXT,
            club_name TEXT,
            member_net REAL,
            lead_to_member_pct REAL,
            lead_booked_pct REAL,
            appt_show_pct REAL,
            appt_close_pct REAL,
            ob_phone_calls_day REAL,
            downpayment_wo_tax REAL,
            fc_booking_pct REAL,
            show_pct REAL,
            close_pct REAL,
            avg_deal REAL,
            avg_fcs_day REAL,
            downpayments REAL,
            downpayment_pct REAL,
            tav REAL,
            revenue REAL,
            remaining_draft REAL,
            projected_revenue REAL,
            ob_phone_calls REAL,
            new_leads REAL,
            appt_scheduled REAL,
            appt_show_count REAL,
            total_tours REAL,
            walk_ins REAL,
            new_members REAL,
            downpayment_amount REAL,
            square_dps REAL,
            fcs_booked_pos REAL,
            fcs_made REAL,
            fcs_scheduled REAL,
            fcs_shows REAL,
            fcs_closes REAL,
            new_deals REAL,
            FOREIGN KEY (upload_id) REFERENCES uploads(id)
        )
    ''')

    # Create indexes for faster queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_company_date ON company_metrics(record_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_territory_date ON territory_metrics(record_date, territory_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_region_date ON region_metrics(record_date, region_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_club_date ON club_metrics(record_date, club_name)')

    conn.commit()
    conn.close()

def save_upload(filename, month_year, record_count):
    """Record an upload and return the upload_id"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO uploads (filename, month_year, record_count)
        VALUES (?, ?, ?)
    ''', (filename, month_year, record_count))
    upload_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return upload_id

def metric_to_db_value(value):
    """Convert metric value to database-safe float"""
    if pd.isna(value) or value == '$ -' or value == '-':
        return None
    try:
        return float(value)
    except:
        return None

def save_company_metrics(upload_id, record_date, month_year, metrics):
    """Save company level metrics"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO company_metrics (
            upload_id, record_date, month_year,
            member_net, lead_to_member_pct, lead_booked_pct, appt_show_pct, appt_close_pct,
            ob_phone_calls_day, downpayment_wo_tax, fc_booking_pct, show_pct, close_pct,
            avg_deal, avg_fcs_day, downpayments, downpayment_pct, tav, revenue,
            remaining_draft, projected_revenue, ob_phone_calls, new_leads, appt_scheduled,
            appt_show_count, total_tours, walk_ins, new_members, downpayment_amount,
            square_dps, fcs_booked_pos, fcs_made, fcs_scheduled, fcs_shows, fcs_closes,
            new_deals, locations
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        upload_id, record_date, month_year,
        metric_to_db_value(metrics.get('Member Net')),
        metric_to_db_value(metrics.get('Lead to Member %')),
        metric_to_db_value(metrics.get('Lead Booked %')),
        metric_to_db_value(metrics.get('Appt Show %')),
        metric_to_db_value(metrics.get('Appt Close %')),
        metric_to_db_value(metrics.get('OB Phone Calls/Day')),
        metric_to_db_value(metrics.get('Downpayment (w/o Sales Tax)')),
        metric_to_db_value(metrics.get('FC Booking %')),
        metric_to_db_value(metrics.get('Show %')),
        metric_to_db_value(metrics.get('Close %')),
        metric_to_db_value(metrics.get('Avg Deal')),
        metric_to_db_value(metrics.get('Avg FCs/Day')),
        metric_to_db_value(metrics.get('Downpayments')),
        metric_to_db_value(metrics.get('Downpayment %')),
        metric_to_db_value(metrics.get('TAV')),
        metric_to_db_value(metrics.get('Revenue')),
        metric_to_db_value(metrics.get('Remaining Draft')),
        metric_to_db_value(metrics.get('Projected Revenue')),
        metric_to_db_value(metrics.get('OB Phone Calls')),
        metric_to_db_value(metrics.get('New Leads')),
        metric_to_db_value(metrics.get('Appt Scheduled')),
        metric_to_db_value(metrics.get('Appt Show Count')),
        metric_to_db_value(metrics.get('Total Tours')),
        metric_to_db_value(metrics.get('Walk-Ins')),
        metric_to_db_value(metrics.get('New Members')),
        metric_to_db_value(metrics.get('Downpayment Amount')),
        metric_to_db_value(metrics.get('Square DPs')),
        metric_to_db_value(metrics.get('FCs Booked @ POS')),
        metric_to_db_value(metrics.get('FCs Made')),
        metric_to_db_value(metrics.get('FCs Scheduled')),
        metric_to_db_value(metrics.get('FCs Shows')),
        metric_to_db_value(metrics.get('FCs Closes')),
        metric_to_db_value(metrics.get('New Deals')),
        metric_to_db_value(metrics.get('Locations'))
    ))
    conn.commit()
    conn.close()

def save_territory_metrics(upload_id, record_date, month_year, territory_name, metrics):
    """Save territory level metrics"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO territory_metrics (
            upload_id, record_date, month_year, territory_name,
            member_net, lead_to_member_pct, lead_booked_pct, appt_show_pct, appt_close_pct,
            ob_phone_calls_day, downpayment_wo_tax, fc_booking_pct, show_pct, close_pct,
            avg_deal, avg_fcs_day, downpayments, downpayment_pct, tav, revenue,
            remaining_draft, projected_revenue, ob_phone_calls, new_leads, appt_scheduled,
            appt_show_count, total_tours, walk_ins, new_members, downpayment_amount,
            square_dps, fcs_booked_pos, fcs_made, fcs_scheduled, fcs_shows, fcs_closes,
            new_deals, locations
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        upload_id, record_date, month_year, territory_name,
        metric_to_db_value(metrics.get('Member Net')),
        metric_to_db_value(metrics.get('Lead to Member %')),
        metric_to_db_value(metrics.get('Lead Booked %')),
        metric_to_db_value(metrics.get('Appt Show %')),
        metric_to_db_value(metrics.get('Appt Close %')),
        metric_to_db_value(metrics.get('OB Phone Calls/Day')),
        metric_to_db_value(metrics.get('Downpayment (w/o Sales Tax)')),
        metric_to_db_value(metrics.get('FC Booking %')),
        metric_to_db_value(metrics.get('Show %')),
        metric_to_db_value(metrics.get('Close %')),
        metric_to_db_value(metrics.get('Avg Deal')),
        metric_to_db_value(metrics.get('Avg FCs/Day')),
        metric_to_db_value(metrics.get('Downpayments')),
        metric_to_db_value(metrics.get('Downpayment %')),
        metric_to_db_value(metrics.get('TAV')),
        metric_to_db_value(metrics.get('Revenue')),
        metric_to_db_value(metrics.get('Remaining Draft')),
        metric_to_db_value(metrics.get('Projected Revenue')),
        metric_to_db_value(metrics.get('OB Phone Calls')),
        metric_to_db_value(metrics.get('New Leads')),
        metric_to_db_value(metrics.get('Appt Scheduled')),
        metric_to_db_value(metrics.get('Appt Show Count')),
        metric_to_db_value(metrics.get('Total Tours')),
        metric_to_db_value(metrics.get('Walk-Ins')),
        metric_to_db_value(metrics.get('New Members')),
        metric_to_db_value(metrics.get('Downpayment Amount')),
        metric_to_db_value(metrics.get('Square DPs')),
        metric_to_db_value(metrics.get('FCs Booked @ POS')),
        metric_to_db_value(metrics.get('FCs Made')),
        metric_to_db_value(metrics.get('FCs Scheduled')),
        metric_to_db_value(metrics.get('FCs Shows')),
        metric_to_db_value(metrics.get('FCs Closes')),
        metric_to_db_value(metrics.get('New Deals')),
        metric_to_db_value(metrics.get('Locations'))
    ))
    conn.commit()
    conn.close()

def save_region_metrics(upload_id, record_date, month_year, territory_name, region_name, metrics):
    """Save region level metrics"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO region_metrics (
            upload_id, record_date, month_year, territory_name, region_name,
            member_net, lead_to_member_pct, lead_booked_pct, appt_show_pct, appt_close_pct,
            ob_phone_calls_day, downpayment_wo_tax, fc_booking_pct, show_pct, close_pct,
            avg_deal, avg_fcs_day, downpayments, downpayment_pct, tav, revenue,
            remaining_draft, projected_revenue, ob_phone_calls, new_leads, appt_scheduled,
            appt_show_count, total_tours, walk_ins, new_members, downpayment_amount,
            square_dps, fcs_booked_pos, fcs_made, fcs_scheduled, fcs_shows, fcs_closes,
            new_deals, locations
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        upload_id, record_date, month_year, territory_name, region_name,
        metric_to_db_value(metrics.get('Member Net')),
        metric_to_db_value(metrics.get('Lead to Member %')),
        metric_to_db_value(metrics.get('Lead Booked %')),
        metric_to_db_value(metrics.get('Appt Show %')),
        metric_to_db_value(metrics.get('Appt Close %')),
        metric_to_db_value(metrics.get('OB Phone Calls/Day')),
        metric_to_db_value(metrics.get('Downpayment (w/o Sales Tax)')),
        metric_to_db_value(metrics.get('FC Booking %')),
        metric_to_db_value(metrics.get('Show %')),
        metric_to_db_value(metrics.get('Close %')),
        metric_to_db_value(metrics.get('Avg Deal')),
        metric_to_db_value(metrics.get('Avg FCs/Day')),
        metric_to_db_value(metrics.get('Downpayments')),
        metric_to_db_value(metrics.get('Downpayment %')),
        metric_to_db_value(metrics.get('TAV')),
        metric_to_db_value(metrics.get('Revenue')),
        metric_to_db_value(metrics.get('Remaining Draft')),
        metric_to_db_value(metrics.get('Projected Revenue')),
        metric_to_db_value(metrics.get('OB Phone Calls')),
        metric_to_db_value(metrics.get('New Leads')),
        metric_to_db_value(metrics.get('Appt Scheduled')),
        metric_to_db_value(metrics.get('Appt Show Count')),
        metric_to_db_value(metrics.get('Total Tours')),
        metric_to_db_value(metrics.get('Walk-Ins')),
        metric_to_db_value(metrics.get('New Members')),
        metric_to_db_value(metrics.get('Downpayment Amount')),
        metric_to_db_value(metrics.get('Square DPs')),
        metric_to_db_value(metrics.get('FCs Booked @ POS')),
        metric_to_db_value(metrics.get('FCs Made')),
        metric_to_db_value(metrics.get('FCs Scheduled')),
        metric_to_db_value(metrics.get('FCs Shows')),
        metric_to_db_value(metrics.get('FCs Closes')),
        metric_to_db_value(metrics.get('New Deals')),
        metric_to_db_value(metrics.get('Locations'))
    ))
    conn.commit()
    conn.close()

def save_club_metrics(upload_id, record_date, month_year, territory_name, region_name, club_name, metrics):
    """Save club level metrics"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO club_metrics (
            upload_id, record_date, month_year, territory_name, region_name, club_name,
            member_net, lead_to_member_pct, lead_booked_pct, appt_show_pct, appt_close_pct,
            ob_phone_calls_day, downpayment_wo_tax, fc_booking_pct, show_pct, close_pct,
            avg_deal, avg_fcs_day, downpayments, downpayment_pct, tav, revenue,
            remaining_draft, projected_revenue, ob_phone_calls, new_leads, appt_scheduled,
            appt_show_count, total_tours, walk_ins, new_members, downpayment_amount,
            square_dps, fcs_booked_pos, fcs_made, fcs_scheduled, fcs_shows, fcs_closes,
            new_deals
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        upload_id, record_date, month_year, territory_name, region_name, club_name,
        metric_to_db_value(metrics.get('Member Net')),
        metric_to_db_value(metrics.get('Lead to Member %')),
        metric_to_db_value(metrics.get('Lead Booked %')),
        metric_to_db_value(metrics.get('Appt Show %')),
        metric_to_db_value(metrics.get('Appt Close %')),
        metric_to_db_value(metrics.get('OB Phone Calls/Day')),
        metric_to_db_value(metrics.get('Downpayment (w/o Sales Tax)')),
        metric_to_db_value(metrics.get('FC Booking %')),
        metric_to_db_value(metrics.get('Show %')),
        metric_to_db_value(metrics.get('Close %')),
        metric_to_db_value(metrics.get('Avg Deal')),
        metric_to_db_value(metrics.get('Avg FCs/Day')),
        metric_to_db_value(metrics.get('Downpayments')),
        metric_to_db_value(metrics.get('Downpayment %')),
        metric_to_db_value(metrics.get('TAV')),
        metric_to_db_value(metrics.get('Revenue')),
        metric_to_db_value(metrics.get('Remaining Draft')),
        metric_to_db_value(metrics.get('Projected Revenue')),
        metric_to_db_value(metrics.get('OB Phone Calls')),
        metric_to_db_value(metrics.get('New Leads')),
        metric_to_db_value(metrics.get('Appt Scheduled')),
        metric_to_db_value(metrics.get('Appt Show Count')),
        metric_to_db_value(metrics.get('Total Tours')),
        metric_to_db_value(metrics.get('Walk-Ins')),
        metric_to_db_value(metrics.get('New Members')),
        metric_to_db_value(metrics.get('Downpayment Amount')),
        metric_to_db_value(metrics.get('Square DPs')),
        metric_to_db_value(metrics.get('FCs Booked @ POS')),
        metric_to_db_value(metrics.get('FCs Made')),
        metric_to_db_value(metrics.get('FCs Scheduled')),
        metric_to_db_value(metrics.get('FCs Shows')),
        metric_to_db_value(metrics.get('FCs Closes')),
        metric_to_db_value(metrics.get('New Deals'))
    ))
    conn.commit()
    conn.close()

def get_historical_company_data(limit=30):
    """Get historical company metrics for trend analysis"""
    conn = get_connection()
    df = pd.read_sql_query('''
        SELECT * FROM company_metrics
        ORDER BY record_date DESC
        LIMIT ?
    ''', conn, params=(limit,))
    conn.close()
    return df

def get_historical_territory_data(territory_name, limit=30):
    """Get historical territory metrics"""
    conn = get_connection()
    df = pd.read_sql_query('''
        SELECT * FROM territory_metrics
        WHERE territory_name = ?
        ORDER BY record_date DESC
        LIMIT ?
    ''', conn, params=(territory_name, limit))
    conn.close()
    return df

def get_historical_region_data(region_name, limit=30):
    """Get historical region metrics"""
    conn = get_connection()
    df = pd.read_sql_query('''
        SELECT * FROM region_metrics
        WHERE region_name = ?
        ORDER BY record_date DESC
        LIMIT ?
    ''', conn, params=(region_name, limit))
    conn.close()
    return df

def get_historical_club_data(club_name, limit=30):
    """Get historical club metrics"""
    conn = get_connection()
    df = pd.read_sql_query('''
        SELECT * FROM club_metrics
        WHERE club_name = ?
        ORDER BY record_date DESC
        LIMIT ?
    ''', conn, params=(club_name, limit))
    conn.close()
    return df

def get_upload_history():
    """Get list of all uploads"""
    conn = get_connection()
    df = pd.read_sql_query('''
        SELECT * FROM uploads
        ORDER BY upload_date DESC
    ''', conn)
    conn.close()
    return df

def check_if_date_exists(record_date, month_year):
    """Check if data for this date already exists"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM company_metrics
        WHERE record_date = ? AND month_year = ?
    ''', (record_date, month_year))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

# Initialize database on import
init_database()
