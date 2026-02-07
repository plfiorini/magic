#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moxfield_to_forge.py
Convert Moxfield deck files to Forge format.
Supports both text and JSON formats from Moxfield.
Handles Commander/EDH decks (100 cards) and regular decks.
"""
import json
import re
import argparse
import sys
from typing import Dict, List, Any

def parse_moxfield_deck(moxfield_data: str) -> Dict[str, Any]:
    """Parse Moxfield deck data (JSON format)"""
    try:
        return json.loads(moxfield_data)
    except json.JSONDecodeError:
        # If it's a text format, parse it differently
        return parse_moxfield_text(moxfield_data)

def parse_moxfield_text(deck_text: str) -> Dict[str, Any]:
    """Parse Moxfield deck in text format"""
    lines = deck_text.strip().split('\n')
    deck = {'mainboard': {}, 'sideboard': {}}
    current_section = 'mainboard'
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('//'):
            continue
        if line.lower() in ['sideboard', 'side board']:
            current_section = 'sideboard'
            continue
            
        # Parse card line (format: "1 Kaalia of the Vast (MH3) 290" or "1 Luxury Suite (PCLB) 355s *F*")
        match = re.match(r'^(\d+)\s+(.+?)\s*\(([^)]+)\)\s*(\S*)\s*(.*?)$', line)
        if match:
            quantity = int(match.group(1))
            card_name = match.group(2).strip()
            set_code = match.group(3).strip()
            collector_info = match.group(4).strip() if match.group(4) else ""
            special_markers = match.group(5).strip() if match.group(5) else ""
            
            # If the card already exists, add to its quantity instead of overwriting
            if card_name in deck[current_section]:
                deck[current_section][card_name]['quantity'] += quantity
                # Keep the first occurrence's set info (or we could merge them)
            else:
                deck[current_section][card_name] = {
                    'quantity': quantity,
                    'set': set_code,
                    'collector_number': collector_info,
                    'special_markers': special_markers
                }
        else:
            # Fallback for cards without set info (format: "4 Lightning Bolt")
            fallback_match = re.match(r'^(\d+)\s+(.+)$', line)
            if fallback_match:
                quantity = int(fallback_match.group(1))
                card_name = fallback_match.group(2).strip()
                
                # If the card already exists, add to its quantity instead of overwriting
                if card_name in deck[current_section]:
                    deck[current_section][card_name]['quantity'] += quantity
                else:
                    deck[current_section][card_name] = {'quantity': quantity}
    
    return deck

def normalize_set_code_for_forge(set_code: str) -> str:
    """Convert promo set codes to regular set codes for Forge compatibility"""
    if len(set_code) == 4 and set_code.startswith('P'):
        # Remove 'P' prefix from promo sets (e.g., PMKM -> MKM)
        return set_code[1:]
    return set_code

def is_basic_land(card_name: str) -> bool:
    """Check if a card is a basic land"""
    basic_lands = {'Plains', 'Island', 'Swamp', 'Mountain', 'Forest'}
    return card_name in basic_lands

def convert_to_forge_format(moxfield_deck: Dict[str, Any]) -> str:
    """Convert parsed Moxfield deck to Forge format"""
    forge_deck = []
    
    # Add metadata
    deck_name = moxfield_deck.get('name', 'Converted Deck')
    forge_deck.append(f"[metadata]")
    forge_deck.append(f"Name={deck_name}")
    
    # Check if this is a Commander deck (exactly 100 cards)
    mainboard = moxfield_deck.get('mainboard', {})
    sideboard = moxfield_deck.get('sideboard', {})
    
    total_mainboard_cards = sum(card['quantity'] for card in mainboard.values())
    total_sideboard_cards = sum(card['quantity'] for card in sideboard.values())
    total_cards = total_mainboard_cards + total_sideboard_cards
    
    # For Commander deck detection, check if we have exactly 100 cards total
    # and verify singleton rule (except for basic lands)
    is_commander_deck = False
    if total_cards == 100:
        # Check singleton rule (except basic lands)
        singleton_violation = False
        for card_name, card_data in mainboard.items():
            if card_data.get('quantity', 1) > 1 and not is_basic_land(card_name):
                singleton_violation = True
                break
        is_commander_deck = not singleton_violation
    
    # Convert mainboard cards to list for easier manipulation
    mainboard_cards = []
    for card_name, card_data in mainboard.items():
        name = re.sub(r' \/ .+$', '', card_name)
        quantity = card_data.get('quantity', 1)
        set_code = card_data.get('set', '')
        collector_number = card_data.get('collector_number', '')
        special_markers = card_data.get('special_markers', '')
 
        # Format the card line with set information if available
        card_line = f"{quantity} {name}"
        if set_code:
            # Normalize set code for Forge (remove P prefix from promo sets)
            normalized_set_code = normalize_set_code_for_forge(set_code)
            card_line += f"|{normalized_set_code}"
            if collector_number:
                card_line += f"|[{collector_number}]"
        if special_markers:
            card_line += f" {special_markers}"
        
        mainboard_cards.append(card_line)
    
    # Handle Commander deck format
    if is_commander_deck and mainboard_cards:
        # First card is the commander
        forge_deck.append(f"[Commander]")
        forge_deck.append(mainboard_cards[0])
        
        # Remaining cards go in Main section
        forge_deck.append(f"[Main]")
        for card_line in mainboard_cards[1:]:
            forge_deck.append(card_line)
    else:
        # Regular deck format
        forge_deck.append(f"[Main]")
        for card_line in mainboard_cards:
            forge_deck.append(card_line)
    
    # Add sideboard if present
    sideboard = moxfield_deck.get('sideboard', {})
    if sideboard:
        forge_deck.append(f"[Sideboard]")
        for card_name, card_data in sideboard.items():
            quantity = card_data.get('quantity', 1)
            set_code = card_data.get('set', '')
            collector_number = card_data.get('collector_number', '')
            special_markers = card_data.get('special_markers', '')
            
            # Format the card line with set information if available
            card_line = f"{quantity} {card_name}"
            if set_code:
                # Normalize set code for Forge (remove P prefix from promo sets)
                normalized_set_code = normalize_set_code_for_forge(set_code)
                card_line += f"|{normalized_set_code}"
                if collector_number:
                    card_line += f"|[{collector_number}]"
            if special_markers:
                card_line += f" {special_markers}"
            
            forge_deck.append(card_line)
    
    return '\n'.join(forge_deck)

def convert_moxfield_to_forge(input_file: str, output_file: str):
    """Main conversion function"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            moxfield_data = f.read()
        
        # Parse the Moxfield deck
        deck = parse_moxfield_deck(moxfield_data)
        
        # Convert to Forge format
        forge_deck = convert_to_forge_format(deck)
        
        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(forge_deck)
        
        print(f"Successfully converted deck to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
    except Exception as e:
        print(f"Error during conversion: {str(e)}")

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description='Convert Moxfield deck files to Forge format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.txt output.dck
  %(prog)s --input moxfield_deck.txt --output forge_deck.dck
  %(prog)s -i deck.json -o converted.dck --name "My Awesome Deck"
  %(prog)s --demo  # Run with sample deck
        """
    )
    
    parser.add_argument(
        'input_file',
        nargs='?',
        help='Input Moxfield deck file (.txt or .json)'
    )
    
    parser.add_argument(
        'output_file',
        nargs='?',
        help='Output Forge deck file (.dck)'
    )
    
    parser.add_argument(
        '-i', '--input',
        dest='input_file_alt',
        help='Input Moxfield deck file (.txt or .json)'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output_file_alt',
        help='Output Forge deck file (.dck)'
    )
    
    parser.add_argument(
        '-n', '--name',
        help='Override deck name in the output file'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run with sample deck data and display output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Handle demo mode
    if args.demo:
        print("Running demo with sample Moxfield deck...")
        sample_moxfield = """
1 Kaalia of the Vast (MH3) 290
1 Akroma's Will (CMR) 3
1 Lightning Greaves (C15) 257
1 Sol Ring (MIC) 162
1 Command Tower (LCC) 325
        """
        deck = parse_moxfield_text(sample_moxfield)
        if args.name:
            deck['name'] = args.name
        forge_output = convert_to_forge_format(deck)
        print("\nConverted deck:")
        print(forge_output)
        return
    
    # Determine input and output files
    input_file = args.input_file or args.input_file_alt
    output_file = args.output_file or args.output_file_alt
    
    # Validate arguments
    if not input_file:
        parser.error("Input file is required. Use -h for help.")
    
    if not output_file:
        # Auto-generate output filename based on input
        if input_file.endswith('.txt'):
            output_file = input_file.replace('.txt', '.dck')
        elif input_file.endswith('.json'):
            output_file = input_file.replace('.json', '.dck')
        else:
            output_file = input_file + '.dck'
        print(f"No output file specified, using: {output_file}")
    
    try:
        # Read and parse input file
        with open(input_file, 'r', encoding='utf-8') as f:
            moxfield_data = f.read()
        
        deck = parse_moxfield_deck(moxfield_data)
        
        # Override deck name if specified
        if args.name:
            deck['name'] = args.name
        
        # Convert to Forge format
        forge_deck = convert_to_forge_format(deck)
        
        # Write output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(forge_deck)
        
        print(f"Successfully converted '{input_file}' to '{output_file}'")
        
        # Show some stats
        mainboard_count = sum(card['quantity'] for card in deck.get('mainboard', {}).values())
        sideboard_count = sum(card['quantity'] for card in deck.get('sideboard', {}).values())
        total_cards = mainboard_count + sideboard_count
        
        print(f"Deck statistics:")
        if total_cards == 100:
            # Check if it's actually a Commander deck (singleton except basic lands)
            singleton_violation = False
            for card_name, card_data in deck.get('mainboard', {}).items():
                if card_data.get('quantity', 1) > 1 and not is_basic_land(card_name):
                    singleton_violation = True
                    break
            
            if not singleton_violation:
                print(f"  Format: Commander/EDH deck (100 cards)")
                print(f"  Commander: 1 card")
                print(f"  Main deck: {len(deck.get('mainboard', {})) - 1} unique cards, {mainboard_count - 1} total cards")
            else:
                print(f"  Mainboard: {len(deck.get('mainboard', {}))} unique cards, {mainboard_count} total cards")
        else:
            print(f"  Mainboard: {len(deck.get('mainboard', {}))} unique cards, {mainboard_count} total cards")
        
        if deck.get('sideboard'):
            print(f"  Sideboard: {len(deck.get('sideboard', {}))} unique cards, {sideboard_count} total cards")
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during conversion: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
