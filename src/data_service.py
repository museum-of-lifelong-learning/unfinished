import logging
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List
"""
Data Handler - Reads and processes figurine data from Excel file.
"""

logger = logging.getLogger(__name__)

class DataService:
    """Handles reading and querying figurine data from Excel file."""
    
    def __init__(self, excel_path: str = "../assets/Unfinished_data_collection.xlsx"):
        """
        Initialize the data handler.
        
        Args:
            excel_path: Path to the Excel file containing figurine data
        """
        self.excel_path = Path(excel_path)
        self.answers_df = None
        self.titles_df = None
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
            
            # Load the Titles sheet
            try:
                self.titles_df = pd.read_excel(self.excel_path, sheet_name='Titel')
                logger.info(f"Loaded {len(self.titles_df)} titles from Excel file")
            except Exception as e:
                logger.warning(f"Could not load 'Titel' sheet: {e}")
                # Try fallback name just in case
                try:
                    self.titles_df = pd.read_excel(self.excel_path, sheet_name='Beleg_TItel')
                    logger.info(f"Loaded {len(self.titles_df)} titles from 'Beleg_TItel' sheet")
                except:
                    pass

            logger.debug(f"Available columns: {list(self.answers_df.columns)}")
            
            # Show sample data for debugging
            if 'RFID_Tag_ID' in self.answers_df.columns:
                sample = self.answers_df['RFID_Tag_ID'].head(3).tolist()
                logger.debug(f"Sample RFID_Tag_ID values: {sample}")
            else:
                logger.warning(f"Column 'RFID_Tag_ID' not found! Available: {list(self.answers_df.columns)}")

            if 'svg' in self.answers_df.columns:
                logger.debug("Column 'svg' found.")
            else:
                logger.warning(f"Column 'svg' not found! Available: {list(self.answers_df.columns)}")
            
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

    def get_random_title_word(self, category: str) -> str:
        """
        Get a random adjective from the titles sheet for a specific category.
        
        Args:
            category: The category to search for (case-insensitive)
            
        Returns:
            A random adjective string, or "Unknown" if not found
        """
        if self.titles_df is None:
            logger.error("No title data loaded")
            return "Unknown"
        
        try:
            # Normalize category
            category = category.lower().strip()
            
            # Filter by category (safely)
            # Assuming columns are 'adjektiv' and 'category'
            if 'category' not in self.titles_df.columns or 'adjektiv' not in self.titles_df.columns:
                logger.error("Required columns 'category' or 'adjektiv' missing in Titles sheet")
                return "Unknown"
                
            filtered = self.titles_df[self.titles_df['category'].str.lower().str.strip() == category]
            
            if filtered.empty:
                logger.warning(f"No titles found for category: {category}")
                return "Unknown"
                
            # Pick random
            word = filtered['adjektiv'].sample(n=1).iloc[0]
            return str(word).strip()
            
        except Exception as e:
            logger.error(f"Error getting title word for {category}: {e}")
            return "Error"
    
    def get_answers_per_question(self) -> List[int]:
        """
        Calculate the number of possible answers for each question from the loaded data.
        
        Returns:
            List of integers representing answer counts per question (e.g., [6, 5, 5, 6, 6, 5])
        """
        if self.answers_df is None:
            logger.error("No data loaded")
            return []
        
        try:
            # Group by Frage_ID and count unique Antwort_IDs
            question_counts = self.answers_df.groupby('Frage_ID')['Antwort_ID'].count().to_dict()
            
            # Sort by question ID to ensure correct order (F01, F02, ...)
            sorted_questions = sorted(question_counts.keys())
            counts = [question_counts[q] for q in sorted_questions]
            
            logger.info(f"Answers per question: {dict(zip(sorted_questions, counts))}")
            return counts
            
        except Exception as e:
            logger.error(f"Error calculating answers per question: {e}")
            return []
    
    def get_total_unique_ids(self) -> int:
        """
        Calculate the total number of unique answer set IDs possible.
        
        Returns:
            Total number of unique combinations
        """
        counts = self.get_answers_per_question()
        if not counts:
            return 0
        
        total = 1
        for count in counts:
            total *= count
        
        logger.info(f"Total unique answer set IDs: {total}")
        return total
    
    def calculate_answer_set_id(self, answers: List[Dict]) -> Optional[int]:
        """
        Calculate unique ID from a set of answers using mixed-radix system.
        
        Args:
            answers: List of answer dictionaries (as returned by find_answer_by_tags)
        
        Returns:
            Unique ID from 1 to total_unique_ids, or None if calculation fails
        """
        if not answers or len(answers) != 6:
            logger.error(f"Expected 6 answers, got {len(answers) if answers else 0}")
            return None
        
        if self.answers_df is None:
            logger.error("No data loaded")
            return None
        
        try:
            # Get the number of answers per question
            answers_per_question = self.get_answers_per_question()
            if len(answers_per_question) != 6:
                logger.error(f"Expected 6 questions, got {len(answers_per_question)}")
                return None
            
            # For each answer, determine its index within its question
            answer_indices = []
            
            for answer in answers:
                question_id = answer.get('Frage_ID')
                answer_id = answer.get('Antwort_ID')
                
                if not question_id or not answer_id:
                    logger.error(f"Missing Frage_ID or Antwort_ID in answer: {answer}")
                    return None
                
                # Get all answers for this question
                question_answers = self.answers_df[self.answers_df['Frage_ID'] == question_id]['Antwort_ID'].tolist()
                
                # Find the index of this answer
                try:
                    index = question_answers.index(answer_id)
                    answer_indices.append(index)
                    logger.debug(f"{answer_id} ({question_id}): index {index}")
                except ValueError:
                    logger.error(f"Answer {answer_id} not found in {question_id}")
                    return None
            
            # Calculate unique ID using mixed-radix system
            result = 0
            multiplier = 1
            
            for i in range(5, -1, -1):  # Right to left
                result += answer_indices[i] * multiplier
                if i > 0:
                    multiplier *= answers_per_question[i]
            
            # Return 1-indexed
            unique_id = result + 1
            logger.info(f"Answer set ID: {unique_id} (indices: {answer_indices})")
            return unique_id
            
        except Exception as e:
            logger.error(f"Error calculating answer set ID: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
