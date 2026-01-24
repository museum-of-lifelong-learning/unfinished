"""
Google Sheets Upload Module
Uploads slip data to Google Sheets using a service account.
"""

import logging
import uuid
import os
from typing import Dict, Any, Optional

import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

# Google Sheets configuration
SPREADSHEET_ID = "16Ww-LsbFi6SqtoJglpMt0UxJ1uaPNXRcYCo1aTuIYLE"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Column mapping for the Google Sheet
# Columns: data_id, figure_id, title, Paragraph1, Paragraph2, Resource_ToolsInspiration, Resource_Anlaufstellen, Resource_Programm
COLUMN_ORDER = [
    'data_id',
    'figure_id', 
    'title',
    'Paragraph1',
    'Paragraph2',
    'Resource_ToolsInspiration',
    'Resource_Anlaufstellen',
    'Resource_Programm'
]


def format_resource_with_link(item: str, link: Optional[str]) -> str:
    """
    Format resource with link as HTML if link exists.
    The text before the first "." becomes the link text, rest is normal text.
    
    Example:
        item: "Lernwerkstatt. Ein Ort zum Experimentieren und Lernen."
        link: "https://example.com"
        result: '<a href="https://example.com">Lernwerkstatt</a>. Ein Ort zum Experimentieren und Lernen.'
    
    Args:
        item: The resource item text
        link: Optional URL link for the resource
        
    Returns:
        Formatted string (HTML if link exists, plain text otherwise)
    """
    if not link or not isinstance(link, str) or link.strip() == '':
        return item
    
    # Find first period to split link text from rest
    dot_index = item.find('.')
    
    if dot_index == -1:
        # No period found, entire text becomes link
        return f'<a href="{link}">{item}</a>'
    
    link_text = item[:dot_index]
    rest_text = item[dot_index:]
    
    return f'<a href="{link}">{link_text}</a>{rest_text}'


def get_sheets_client() -> Optional[gspread.Client]:
    """
    Create and return a Google Sheets client using service account credentials.
    
    Credentials can be provided via:
    1. GOOGLE_SERVICE_ACCOUNT_FILE env var pointing to a JSON key file
    2. Individual env vars: GOOGLE_PROJECT_ID, GOOGLE_PRIVATE_KEY_ID, 
       GOOGLE_PRIVATE_KEY, GOOGLE_CLIENT_EMAIL, GOOGLE_CLIENT_ID
       
    Returns:
        gspread.Client or None if authentication fails
    """
    try:
        # Try to load from service account file first
        service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        
        if service_account_file and os.path.exists(service_account_file):
            logger.info(f"Using service account file: {service_account_file}")
            credentials = Credentials.from_service_account_file(
                service_account_file,
                scopes=SCOPES
            )
        else:
            # Build credentials from individual env vars
            logger.info("Building credentials from environment variables")
            
            private_key = os.getenv('GOOGLE_PRIVATE_KEY')
            if private_key:
                # Handle escaped newlines in the private key
                private_key = private_key.replace('\\n', '\n')
            
            credentials_info = {
                "type": "service_account",
                "project_id": os.getenv('GOOGLE_PROJECT_ID'),
                "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
                "private_key": private_key,
                "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('GOOGLE_CLIENT_EMAIL', '').replace('@', '%40')}"
            }
            
            # Validate required fields
            required_fields = ['project_id', 'private_key', 'client_email']
            missing = [f for f in required_fields if not credentials_info.get(f)]
            if missing:
                logger.error(f"Missing required credentials: {missing}")
                return None
            
            credentials = Credentials.from_service_account_info(
                credentials_info,
                scopes=SCOPES
            )
        
        client = gspread.authorize(credentials)
        logger.info("Successfully authenticated with Google Sheets")
        return client
        
    except Exception as e:
        logger.error(f"Failed to authenticate with Google Sheets: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def upload_slip_data(slip_data: Dict[str, Any]) -> Optional[str]:
    """
    Upload slip data to Google Sheets and return generated data_id.
    
    Args:
        slip_data: Dictionary containing:
            - figurine_id: int
            - title_text: str (two lines separated by newline)
            - content: dict with 'paragraph1', 'paragraph2'
            - resources: dict with 'tool', 'location', 'program' items and optional links
            
    Returns:
        Generated UUID (data_id) if successful, None otherwise
    """
    # Generate unique data_id
    data_id = str(uuid.uuid4())
    logger.info(f"[UPLOAD] Generated data_id: {data_id}")
    
    try:
        client = get_sheets_client()
        if not client:
            logger.error("[UPLOAD] Could not get Google Sheets client")
            return None
        
        # Open the spreadsheet
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.sheet1  # Use first sheet
        
        # Prepare row data
        figurine_id = slip_data.get('figurine_id', 0)
        title_text = slip_data.get('title_text', '')
        if title_text:
            # Convert newline-separated title to single line with space
            title_text = title_text.replace('\n', ' ')
        
        content = slip_data.get('content', {})
        resources = slip_data.get('resources', {})
        
        # Format resources with links if available
        tool_item = resources.get('tool', '')
        tool_link = resources.get('tool_link')
        tool_formatted = format_resource_with_link(tool_item, tool_link)
        
        location_item = resources.get('location', '')
        location_link = resources.get('location_link')
        location_formatted = format_resource_with_link(location_item, location_link)
        
        program_item = resources.get('program', '')
        program_link = resources.get('program_link')
        program_formatted = format_resource_with_link(program_item, program_link)
        
        row_data = [
            data_id,
            figurine_id,
            title_text,
            content.get('paragraph1', ''),
            content.get('paragraph2', ''),
            tool_formatted,
            location_formatted,
            program_formatted
        ]
        
        # Append to next free row
        worksheet.append_row(row_data, value_input_option='RAW')
        
        logger.info(f"[UPLOAD] Successfully uploaded data for figurine #{figurine_id} with data_id: {data_id}")
        return data_id
        
    except Exception as e:
        logger.error(f"[UPLOAD] Failed to upload slip data: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def build_qr_url(data_id: str, figure_id: int) -> str:
    """
    Build the QR code URL with data_id and figure_id parameters.
    
    Args:
        data_id: The UUID for this slip data
        figure_id: The figurine ID
        
    Returns:
        Full URL for the QR code
    """
    base_url = "https://museum-of-lifelong-learning.github.io/unfinished/"
    return f"{base_url}?data_id={data_id}&figure_id={figure_id}"
