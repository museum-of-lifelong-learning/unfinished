"""
Supabase Upload Module
Uploads slip data to Supabase database.
Replaces the previous Google Sheets integration.
"""

import logging
import uuid
import os
from typing import Dict, Any, Optional

from supabase import create_client, Client
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')  # Use service key for server-side uploads
TABLE_NAME = 'slips'


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


def get_supabase_client() -> Optional[Client]:
    """
    Create and return a Supabase client using service key credentials.
    
    The service key is used for server-side operations (insert/update/delete).
    This key should NEVER be exposed in client-side code.
       
    Returns:
        Supabase Client or None if authentication fails
    """
    try:
        if not SUPABASE_URL:
            logger.error("SUPABASE_URL environment variable is not set")
            return None
            
        if not SUPABASE_SERVICE_KEY:
            logger.error("SUPABASE_SERVICE_KEY environment variable is not set")
            return None
        
        client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        logger.info("Successfully created Supabase client")
        return client
        
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def upload_slip_data(slip_data: Dict[str, Any]) -> Optional[str]:
    """
    Upload slip data to Supabase and return generated data_id.
    
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
        client = get_supabase_client()
        if not client:
            logger.error("[UPLOAD] Could not get Supabase client")
            return None
        
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
        
        # Build the record to insert
        record = {
            'data_id': data_id,
            'figure_id': figurine_id,
            'title': title_text,
            'paragraph1': content.get('paragraph1', ''),
            'paragraph2': content.get('paragraph2', ''),
            'resource_tools_inspiration': tool_formatted,
            'resource_anlaufstellen': location_formatted,
            'resource_programm': program_formatted
        }
        
        # Insert into Supabase
        result = client.table(TABLE_NAME).insert(record).execute()
        
        if result.data:
            logger.info(f"[UPLOAD] Successfully uploaded data for figurine #{figurine_id} with data_id: {data_id}")
            return data_id
        else:
            logger.error(f"[UPLOAD] Insert returned no data")
            return None
        
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
