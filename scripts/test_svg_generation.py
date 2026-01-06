import sys
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_service import DataService
from generate_figurine import generate_figurine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    answer_ids = ['A01', 'A07', 'A12', 'A17', 'A23', 'A29']
    logger.info(f"Testing generation for answers: {answer_ids}")
    
    handler = DataService(excel_path="assets/Unfinished_data_collection.xlsx")
    if handler.answers_df is None:
        logger.error("Failed to load data")
        return

    svg_list = []
    for aid in answer_ids:
        # Find row with Antwort_ID == aid
        row = handler.answers_df[handler.answers_df['Antwort_ID'] == aid]
        if not row.empty:
            svg_val = row.iloc[0]['svg']
            if isinstance(svg_val, str):
                svg_list.append(svg_val)
                logger.info(f"Found SVG for {aid}")
            else:
                logger.warning(f"SVG for {aid} is not a string: {svg_val}")
        else:
            logger.warning(f"Answer {aid} not found")
            
    if not svg_list:
        logger.error("No SVGs found")
        return
        
    output_path = "test_figurine_svg.png"
    generate_figurine(svg_list, output_path, "testing\nSVG generation.")
    logger.info(f"Output saved to {output_path}")

if __name__ == "__main__":
    main()
