import time
import os
import random
from rfid_reader import RFIDReader
from printer import ThermalPrinter

def mock_llm_generate(tags):
    """
    Mock LLM generation based on tags.
    """
    print(f"Generating text for tags: {tags}")
    time.sleep(1)
    return (
        "The spirits of the forest have gathered.\n"
        "Six ancient artifacts combined.\n"
        "A journey begins now."
    )

def main():
    # 1. Setup
    rfid = RFIDReader()
    # Try USB printer, will fallback to dummy if not found
    printer = ThermalPrinter(connection_type='usb') 

    try:
        rfid.connect()
        
        # 2. Loop / Wait for tags
        print("Waiting for items...")
        while True:
            tags = rfid.read_tags()
            if len(tags) == 6:
                print("All 6 items detected!")
                
                # 3. Generate Text
                story = mock_llm_generate(tags)
                
                # 4. Print Output
                print("Printing story...")
                
                # Print a random image from assets
                assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
                images = [f for f in os.listdir(assets_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                if images:
                    image_path = os.path.join(assets_dir, random.choice(images))
                    printer.print_image(image_path)
                
                printer.print_text(story)
                
                break # Exit after one successful run for this demo
            else:
                print(f"Detected {len(tags)} items. Waiting for 6...")
                time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        rfid.disconnect()

if __name__ == "__main__":
    main()
