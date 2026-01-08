import logging
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List
from collections import Counter
"""
Data Handler - Reads and processes figurine data from Excel file.

The DataService class provides functionality to:
- Query answers by RFID tag IDs
- Query resources by category with weighted matching on:
  * Mindsets (from all answers)
  * F05 answer (Bedürfnisse/Needs)
  * F06 answer (Situation)
- Calculate unique answer set IDs
- Retrieve random title words by category
- Calculate prevalent mindset from answers
- Get complete prompt template text for content generation
"""

logger = logging.getLogger(__name__)


def get_prevalent_mindset(answers):
    """Calculate the most prevalent mindset from answers."""
    all_mindsets = []
    if not answers:
        return None
    for ans in answers:
        # Check for 'Mindsets' key (case sensitive matching Excel column)
        m_str = ans.get('Mindsets')
        if m_str and isinstance(m_str, str):
            # Split by comma and strip whitespace
            parts = [m.strip() for m in m_str.split(',')]
            all_mindsets.extend(parts)
            
    if not all_mindsets:
        return None
        
    # specific logic: if multiple mindsets have same count, pick one? most_common handles it (picks first)
    counts = Counter(all_mindsets)
    if not counts:
        return None
    return counts.most_common(1)[0][0]

class DataService:
    """Handles reading and querying figurine data from Excel file."""
    
    def __init__(self, excel_path: str = None):
        """
        Initialize the data handler.
        
        Args:
            excel_path: Path to the Excel file containing figurine data.
                       If None, automatically finds the file relative to project root.
        """
        if excel_path is None:
            # Auto-detect: try multiple possible locations
            current_file = Path(__file__)
            project_root = current_file.parent.parent  # Go up from src/ to project root
            excel_path = project_root / "assets" / "Unfinished_data_collection.xlsx"
        
        self.excel_path = Path(excel_path)
        self.answers_df = None
        self.titles_df = None
        self.resources_df = None
        self.prompt_df = None
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

            # Load the Resources sheet
            try:
                self.resources_df = pd.read_excel(self.excel_path, sheet_name='Ressourcen')
                logger.info(f"Loaded {len(self.resources_df)} resources from Excel file")
            except Exception as e:
                logger.warning(f"Could not load 'Ressourcen' sheet: {e}")
            
            # Load the Prompt sheet
            try:
                self.prompt_df = pd.read_excel(self.excel_path, sheet_name='Prompt')
                logger.info(f"Loaded {len(self.prompt_df)} prompt rows from Excel file")
            except Exception as e:
                logger.warning(f"Could not load 'Prompt' sheet: {e}")
                self.prompt_df = None

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
        
    def _parse_comma_separated_list(self, value: str) -> List[str]:
        """
        Parse a comma-separated string into a list of stripped items.
        
        Args:
            value: Comma-separated string
            
        Returns:
            List of stripped string items
        """
        if pd.isna(value) or not value:
            return []
        return [item.strip() for item in str(value).split(',')]
    
    def _calculate_mindsets_score(self, resource_mindsets: str, answer_mindsets: List[str]) -> float:
        """
        Calculate matching score between resource mindsets and answer mindsets.
        
        Args:
            resource_mindsets: Comma-separated mindsets from resource row
            answer_mindsets: List of mindsets from answers
            
        Returns:
            Score between 0 and 1 (percentage of matching mindsets)
        """
        if not answer_mindsets:
            return 0.0
        
        resource_set = set(self._parse_comma_separated_list(resource_mindsets))
        answer_set = set(answer_mindsets)
        
        if not resource_set or not answer_set:
            return 0.0
        
        # Calculate Jaccard similarity (intersection / union)
        intersection = len(resource_set & answer_set)
        union = len(resource_set | answer_set)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_match_score(self, resource_value: str, target_value: str) -> float:
        """
        Calculate matching score for a single attribute (F05 or F06).
        
        Args:
            resource_value: Comma-separated values from resource row
            target_value: Target value to match
            
        Returns:
            1.0 if target is in resource values, 0.0 otherwise
        """
        if not target_value or pd.isna(resource_value):
            return 0.0
        
        resource_list = self._parse_comma_separated_list(resource_value)
        return 1.0 if target_value in resource_list else 0.0
    
    def find_best_resource(
        self,
        kategorie: str,
        answers: List[Dict],
        mindset_weight: float = 1.0,
        f05_weight: float = 1.0,
        f06_weight: float = 1.0
    ) -> Optional[Dict]:
        """
        Find the best matching resource from the Ressourcen sheet based on kategorie
        and matching mindsets, F05 answer (Bedürfnisse), and F06 answer (Situation).
        
        Args:
            kategorie: The category to filter resources by (e.g., 'Tools & Inspiration')
            answers: List of answer dictionaries (as returned by find_answer_by_tags)
            mindset_weight: Weight for mindset matching (default 1.0)
            f05_weight: Weight for F05 (Bedürfnisse) matching (default 1.0)
            f06_weight: Weight for F06 (Situation) matching (default 1.0)
            
        Returns:
            Dictionary containing the best matching resource row, or None if no resources found
        """
        if self.resources_df is None:
            logger.error("No resources data loaded")
            return None
        
        if not answers:
            logger.error("No answers provided")
            return None
        
        try:
            # Filter resources by kategorie
            filtered_resources = self.resources_df[
                self.resources_df['Kategorie'].str.strip().str.lower() == kategorie.strip().lower()
            ]
            
            if filtered_resources.empty:
                logger.warning(f"No resources found for kategorie: {kategorie}")
                return None
            
            logger.info(f"Found {len(filtered_resources)} resources in kategorie '{kategorie}'")
            
            # Extract mindsets from all answers
            answer_mindsets = []
            for answer in answers:
                mindsets = answer.get('Mindsets')
                if mindsets and not pd.isna(mindsets):
                    answer_mindsets.extend(self._parse_comma_separated_list(mindsets))
            
            # Remove duplicates
            answer_mindsets = list(set(answer_mindsets))
            logger.debug(f"Collected mindsets from answers: {answer_mindsets}")
            
            # Find F05 and F06 answers
            f05_answer = None
            f06_answer = None
            
            for answer in answers:
                frage_id = answer.get('Frage_ID')
                antwort = answer.get('Antwort')
                
                if frage_id == 'F05':
                    f05_answer = antwort
                elif frage_id == 'F06':
                    f06_answer = antwort
            
            logger.debug(f"F05 answer (Bedürfnisse): {f05_answer}")
            logger.debug(f"F06 answer (Situation): {f06_answer}")
            
            # Calculate scores for each resource
            best_score = -1
            best_resource = None
            scores = []
            
            for idx, resource in filtered_resources.iterrows():
                # Calculate individual scores
                mindset_score = self._calculate_mindsets_score(
                    resource.get('Mindsets', ''),
                    answer_mindsets
                )
                
                f05_score = self._calculate_match_score(
                    resource.get('Bedürfnisse', ''),
                    f05_answer
                ) if f05_answer else 0.0
                
                f06_score = self._calculate_match_score(
                    resource.get('Situation', ''),
                    f06_answer
                ) if f06_answer else 0.0
                
                # Calculate weighted total score
                total_weight = mindset_weight + f05_weight + f06_weight
                weighted_score = (
                    mindset_score * mindset_weight +
                    f05_score * f05_weight +
                    f06_score * f06_weight
                ) / total_weight if total_weight > 0 else 0.0
                
                scores.append({
                    'index': idx,
                    'item': resource.get('Item', ''),
                    'mindset_score': mindset_score,
                    'f05_score': f05_score,
                    'f06_score': f06_score,
                    'total_score': weighted_score
                })
                
                logger.debug(
                    f"Resource '{resource.get('Item', '')}': "
                    f"mindset={mindset_score:.2f}, f05={f05_score:.2f}, "
                    f"f06={f06_score:.2f}, total={weighted_score:.2f}"
                )
                
                # Track best score
                if weighted_score > best_score:
                    best_score = weighted_score
                    best_resource = resource
            
            # If no clear winner (all scores equal), pick the first one
            if best_resource is None and not filtered_resources.empty:
                best_resource = filtered_resources.iloc[0]
                logger.info("All resources scored equally, selecting first resource")
            
            if best_resource is not None:
                logger.info(
                    f"Selected resource: '{best_resource.get('Item', '')}' "
                    f"with score {best_score:.2f}"
                )
                return best_resource.to_dict()
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding best resource: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def get_prompt(self) -> str:
        """
        Get the complete prompt template text from the Prompt sheet.
        
        All rows from the 'Prompt' column are concatenated with double newlines
        to form a single prompt template string.
        
        Returns:
            Complete prompt template as a single string, or empty string if not loaded
        """
        if self.prompt_df is None:
            logger.error("No prompt data loaded")
            return ""
        
        try:
            if 'Prompt' not in self.prompt_df.columns:
                logger.error("'Prompt' column not found in Prompt sheet")
                return ""
            
            # Get all non-null values from the Prompt column
            prompt_parts = []
            for value in self.prompt_df['Prompt']:
                if pd.notna(value):
                    prompt_parts.append(str(value).strip())
            
            # Join with double newlines for readability
            prompt_text = '\n\n'.join(prompt_parts)
            
            logger.info(f"Loaded prompt template with {len(prompt_parts)} sections, {len(prompt_text)} characters")
            return prompt_text
            
        except Exception as e:
            logger.error(f"Error getting prompt template: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return ""