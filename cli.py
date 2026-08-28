import argparse
import sys
import os
import logging
from adlib_core import convert_adlib_to_atom

def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    parser = argparse.ArgumentParser(description="Convert Axiell Adlib XML to AtoM ISAD(G) CSV.")
    parser.add_argument("input_xml", help="Path to the source Adlib XML file")
    parser.add_argument("output_csv", help="Path to the destination CSV file")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_mapping = os.path.join(script_dir, "default_mapping.json")
    
    parser.add_argument("--mapping", default=default_mapping, help="Path to custom JSON mapping profile")
    parser.add_argument("--repository", required=True, help="AtoM authorized repository name (Mandatory)")
    parser.add_argument("--culture", default="en", help="AtoM culture code (default: en)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_xml):
        logging.error(f"Input file {args.input_xml} not found.")
        sys.exit(1)
        
    if not os.path.exists(args.mapping):
        logging.error(f"Mapping file {args.mapping} not found.")
        sys.exit(1)
        
    try:
        convert_adlib_to_atom(args.input_xml, args.output_csv, args.mapping, args.repository, args.culture)
    except Exception as e:
        logging.error(f"Fatal error during conversion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
