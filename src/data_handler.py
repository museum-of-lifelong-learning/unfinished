import logging
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List
"""
Data Handler - Reads and processes figurine data from Excel file.
"""

logger = logging.getLogger(__name__)

class FigurineDataHandler:
    """Handles reading and querying figurine data from Excel file."""
    
    def __init__(self, excel_path: str = "../assets/Unfinished_data_collection.xlsx"):
        """
        Initialize the data handler.
        
        Args:
            excel_path: Path to the Excel file containing figurine data
        """
        self.excel_path = Path(excel_path)
        self.answers_df = None
        self._load_data()
    
    def _load_data(self):
        """Load data from Excel file."""
        try:
            if not self.excel_path.exists():
                logger.error(f"Excel file not found: {self.excel_path}")
                return
            
            # Load the Answers sheet
            self.answers_df = pd.read_excel(self.excel_path, sheet_name='Antworten')
            logger.info(f"Loaded {len(self.answers_df)} answers from Excel file")
            logger.debug(f"Available columns: {list(self.answers_df.columns)}")
            
            # Show sample data for debugging
            if 'RFID_Tag_ID' in self.answers_df.columns:
                sample = self.answers_df['RFID_Tag_ID'].head(3).tolist()
                logger.debug(f"Sample RFID_Tag_ID values: {sample}")
            else:
                logger.warning(f"Column 'RFID_Tag_ID' not found! Available: {list(self.answers_df.columns)}")
            
        except Exception as e:
            logger.error(f"Failed to load Excel file: {e}")
            self.answers_df = None
    
    def find_answer_by_tags(self, tag_ids: List[str]) -> List[Dict]:
        """
        Find answers matching the given RFID tag IDs (one answer per tag).
        
        Args:
            tag_ids: List of RFID tag EPC strings
            
        Returns:
            List of dictionaries containing answer row data for each tag found
        """
        if self.answers_df is None:
            logger.error("No data loaded")
            return []
        
        try:
            # Normalize tag_ids to uppercase
            search_tags = [t.upper() for t in tag_ids]
            logger.debug(f"Searching for {len(search_tags)} individual tags")
            
            # Check if column exists
            if 'RFID_Tag_ID' not in self.answers_df.columns:
                logger.error(f"Column 'RFID_Tag_ID' not found! Available: {list(self.answers_df.columns)}")
                return []
            
            # Find matching rows for each tag
            results = []
            for tag in search_tags:
                found = False
                for idx, row in self.answers_df.iterrows():
                    row_tag = row['RFID_Tag_ID']
                    
                    # Skip NaN/None values
                    if pd.isna(row_tag):
                        continue
                    
                    # Normalize and compare
                    row_tag_normalized = str(row_tag).strip().upper()
                    
                    if row_tag_normalized == tag:
                        logger.debug(f"Tag {tag}: Found at row {idx}")
                        results.append(row.to_dict())
                        found = True
                        break
                
                if not found:
                    logger.warning(f"Tag {tag}: NOT FOUND in Excel")
            
            logger.info(f"Found {len(results)}/{len(search_tags)} answers")
            return results
            
        except Exception as e:
            logger.error(f"Error searching for answers: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
