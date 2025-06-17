"""
Batch AMR Processor for Spreadsheet Data
Processes AMR graphs from columns M and N, outputs uncommon nodes/edges to column Q
"""

import pandas as pd
import json
import argparse
import os
import sys
from typing import Dict, List, Tuple, Any
import tempfile
import traceback
import subprocess

# Add src directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import your existing modules
try:
    from src.amrsummarizer.amr2nx import load_amr_graph
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'amrsummarizer'))
    from amr2nx import load_amr_graph


def create_temp_amr_file(amr_content: str) -> str:
    """Create temporary AMR file and return path"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.amr', delete=False, encoding='utf-8') as f:
        f.write(amr_content.strip())
        return f.name


def call_smatch_ext(amr1_file: str, amr2_file: str, alignment_file: str) -> bool:
    """
    Call smatch_ext.py script to generate alignment JSON
    Uses subprocess to call the existing script
    """
    try:
        # Build command to call smatch_ext.py
        script_path = os.path.join(os.path.dirname(__file__), 'src', 'amrsummarizer', 'smatch_ext.py')
        
        cmd = [
            'python', script_path,
            '--amr1', amr1_file,
            '--amr2', amr2_file, 
            '--output', alignment_file
        ]
        
        print(f"  Calling: python {script_path} --amr1 {os.path.basename(amr1_file)} --amr2 {os.path.basename(amr2_file)} --output {os.path.basename(alignment_file)}")
        
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print(f"  ✓ smatch_ext.py completed successfully")
            return True
        else:
            print(f"  ✗ smatch_ext.py failed with return code {result.returncode}")
            print(f"  STDOUT: {result.stdout}")
            print(f"  STDERR: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ✗ Error calling smatch_ext.py: {e}")
        return False


def process_amr_pair(amr1_content: str, amr2_content: str) -> Dict[str, Any]:
    """
    Process a pair of AMR graphs and return uncommon nodes/edges
    
    Args:
        amr1_content: AMR graph 1 content (column M)
        amr2_content: AMR graph 2 content (column N)
        
    Returns:
        Dict containing uncommon_nodes and uncommon_edges analysis
    """
    temp_files = []
    
    try:
        # Create temporary files
        amr1_file = create_temp_amr_file(amr1_content)
        amr2_file = create_temp_amr_file(amr2_content)
        temp_files.extend([amr1_file, amr2_file])
        
        # Create temporary alignment file
        alignment_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
        alignment_file.close()
        temp_files.append(alignment_file.name)
        
        print(f"Processing AMR pair...")
        print(f"  AMR1 preview: {amr1_content[:100]}...")
        print(f"  AMR2 preview: {amr2_content[:100]}...")
        
        # Call smatch_ext.py using subprocess (same as your manual command)
        success = call_smatch_ext(amr1_file, amr2_file, alignment_file.name)
        
        if not success:
            raise Exception("smatch_ext.py failed to generate alignment")
        
        # Load the alignment result
        with open(alignment_file.name, 'r', encoding='utf-8') as f:
            alignment_data = json.load(f)
        
        # Extract only the uncommon data (what you need for column Q)
        result = {
            "uncommon_nodes": alignment_data.get("uncommon_nodes", {}),
            "uncommon_edges": alignment_data.get("uncommon_edges", {}),
            "statistics": {
                "amr1_uncommon_nodes": len(alignment_data.get("uncommon_nodes", {}).get("amr1_only", [])),
                "amr2_uncommon_nodes": len(alignment_data.get("uncommon_nodes", {}).get("amr2_only", [])),
                "amr1_uncommon_edges": len(alignment_data.get("uncommon_edges", {}).get("amr1_only", [])),
                "amr2_uncommon_edges": len(alignment_data.get("uncommon_edges", {}).get("amr2_only", []))
            }
        }
        
        print(f"  Result: {result['statistics']}")
        return result
        
    except Exception as e:
        print(f"Error processing AMR pair: {e}")
        traceback.print_exc()
        return {
            "error": str(e),
            "uncommon_nodes": {"amr1_only": [], "amr2_only": []},
            "uncommon_edges": {"amr1_only": [], "amr2_only": []},
            "statistics": {"error": True}
        }
    
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass


def process_spreadsheet(input_file: str, output_file: str, sheet_name: str = None) -> None:
    """
    Process entire spreadsheet with AMR comparisons
    
    Args:
        input_file: Path to input Excel file
        output_file: Path to output Excel file  
        sheet_name: Sheet name to process (default: first sheet)
    """
    print(f"Loading spreadsheet: {input_file}")
    
    # Load the spreadsheet
    try:
        if sheet_name:
            data = pd.read_excel(input_file, sheet_name=sheet_name)
        else:
            data = pd.read_excel(input_file, sheet_name=None)
        
        # Handle dict (multiple sheets) vs DataFrame (single sheet)
        if isinstance(data, dict):
            print(f"Multiple sheets detected: {list(data.keys())}")
            
            # Use specified sheet or first available
            if sheet_name and sheet_name in data:
                df = data[sheet_name]
                print(f"Using specified sheet: {sheet_name}")
            else:
                first_sheet = list(data.keys())[0]
                df = data[first_sheet]
                print(f"Using first sheet: {first_sheet}")
                sheet_name = first_sheet
        else:
            df = data
            print("Single sheet detected")
            
        print(f"Loaded {len(df)} rows")
    except Exception as e:
        print(f"Error loading spreadsheet: {e}")
        return
    
    # Check for AMR columns - support both M/N format and amr_article/amr_summary format
    amr1_col = None
    amr2_col = None
    result_col = None
    
    if 'M' in df.columns and 'N' in df.columns:
        amr1_col, amr2_col, result_col = 'M', 'N', 'Q'
        print("Using M/N column format")
    elif 'amr_article' in df.columns and 'amr_summary' in df.columns:
        amr1_col, amr2_col, result_col = 'amr_article', 'amr_summary', 'amr_diff'
        print("Using amr_article/amr_summary column format")
    else:
        print(f"Error: Could not find AMR columns. Available columns: {list(df.columns)}")
        print("Expected either: ['M', 'N'] or ['amr_article', 'amr_summary']")
        return
    
    # Initialize results column
    results = []
    
    # Process each row
    for idx, row in df.iterrows():
        print(f"\nProcessing row {idx + 1}/{len(df)}")
        
        amr1_content = row[amr1_col]
        amr2_content = row[amr2_col]
        
        # Skip empty rows
        if pd.isna(amr1_content) or pd.isna(amr2_content):
            print(f"  Skipping row {idx + 1}: Empty AMR content")
            results.append("")
            continue
        
        if not str(amr1_content).strip() or not str(amr2_content).strip():
            print(f"  Skipping row {idx + 1}: Empty AMR content after strip")
            results.append("")
            continue
        
        # Process the AMR pair
        try:
            result = process_amr_pair(str(amr1_content), str(amr2_content))
            
            # Convert result to JSON string for Excel cell
            result_json = json.dumps(result, indent=2, ensure_ascii=False)
            results.append(result_json)
            
            print(f"  ✓ Success: Found {result['statistics'].get('amr1_uncommon_nodes', 0)} + {result['statistics'].get('amr2_uncommon_nodes', 0)} uncommon nodes")
            
        except Exception as e:
            print(f"  ✗ Error processing row {idx + 1}: {e}")
            error_result = {"error": str(e), "uncommon_nodes": {"amr1_only": [], "amr2_only": []}, "uncommon_edges": {"amr1_only": [], "amr2_only": []}}
            results.append(json.dumps(error_result, ensure_ascii=False))
    
    # Add results to dataframe
    df[result_col] = results
    
    # Save the results
    print(f"\nSaving results to: {output_file}")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory: {output_dir}")
    
    try:
        # Preserve original formatting by using openpyxl
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name or 'Sheet1', index=False)
        
        print(f"✓ Successfully saved {len(results)} results to column {result_col}")
        
        # Print summary
        successful_results = [r for r in results if r and not r.startswith('{"error"')]
        print(f"\nSummary:")
        print(f"  Total rows processed: {len(results)}")
        print(f"  Successful analyses: {len(successful_results)}")
        print(f"  Errors/Empty: {len(results) - len(successful_results)}")
        
    except Exception as e:
        print(f"Error saving results: {e}")
        # Fallback: save as CSV
        csv_file = output_file.replace('.xlsx', '.csv').replace('.xls', '.csv')
        
        # Ensure CSV output directory exists too
        csv_dir = os.path.dirname(csv_file)
        if csv_dir and not os.path.exists(csv_dir):
            os.makedirs(csv_dir, exist_ok=True)
            
        df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"Saved as CSV instead: {csv_file}")


def preview_spreadsheet(input_file: str, sheet_name: str = None, max_rows: int = 5) -> None:
    """Preview spreadsheet content for verification"""
    print(f"Previewing spreadsheet: {input_file}")
    
    try:
        # First, check what pandas returns
        if sheet_name:
            data = pd.read_excel(input_file, sheet_name=sheet_name)
        else:
            data = pd.read_excel(input_file, sheet_name=None)  # Get all sheets info
        
        print(f"Data type returned: {type(data)}")
        
        # Handle dict (multiple sheets) vs DataFrame (single sheet)
        if isinstance(data, dict):
            print(f"Multiple sheets detected: {list(data.keys())}")
            
            # Use first sheet for preview or specified sheet
            if sheet_name and sheet_name in data:
                df = data[sheet_name]
                print(f"Using specified sheet: {sheet_name}")
            else:
                first_sheet = list(data.keys())[0]
                df = data[first_sheet]
                print(f"Using first sheet: {first_sheet}")
        else:
            df = data
            print("Single sheet detected")
        
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Check for AMR columns - support multiple formats
        if 'M' in df.columns and 'N' in df.columns:
            amr1_col, amr2_col = 'M', 'N'
            print(f"\n✓ Found AMR columns M and N")
        elif 'amr_article' in df.columns and 'amr_summary' in df.columns:
            amr1_col, amr2_col = 'amr_article', 'amr_summary'
            print(f"\n✓ Found AMR columns amr_article and amr_summary")
        else:
            print(f"\n✗ Missing AMR columns")
            print(f"Expected either: ['M', 'N'] or ['amr_article', 'amr_summary']")
            print(f"Available columns: {list(df.columns)}")
            return
        
        print(f"Non-empty {amr1_col} values: {df[amr1_col].notna().sum()}")
        print(f"Non-empty {amr2_col} values: {df[amr2_col].notna().sum()}")
        
        # Show preview of AMR content
        for i in range(min(max_rows, len(df))):
            if pd.notna(df.iloc[i][amr1_col]) and pd.notna(df.iloc[i][amr2_col]):
                print(f"\nRow {i+1} AMR preview:")
                print(f"  {amr1_col}: {str(df.iloc[i][amr1_col])[:100]}...")
                print(f"  {amr2_col}: {str(df.iloc[i][amr2_col])[:100]}...")
                break
            
    except Exception as e:
        print(f"Error previewing spreadsheet: {e}")
        traceback.print_exc()


def process_spreadsheet_limited(df: pd.DataFrame, output_file: str, sheet_name: str = None) -> None:
    """Process limited dataframe for testing"""
    print(f"Processing limited dataset with {len(df)} rows")
    
    # Check for AMR columns - support both M/N format and amr_article/amr_summary format
    amr1_col = None
    amr2_col = None
    result_col = None
    
    if 'M' in df.columns and 'N' in df.columns:
        amr1_col, amr2_col, result_col = 'M', 'N', 'Q'
        print("Using M/N column format")
    elif 'amr_article' in df.columns and 'amr_summary' in df.columns:
        amr1_col, amr2_col, result_col = 'amr_article', 'amr_summary', 'amr_diff'
        print("Using amr_article/amr_summary column format")
    else:
        print(f"Error: Could not find AMR columns. Available columns: {list(df.columns)}")
        print("Expected either: ['M', 'N'] or ['amr_article', 'amr_summary']")
        return
    
    results = []
    
    for idx, row in df.iterrows():
        print(f"\nProcessing row {idx + 1}/{len(df)}")
        
        amr1_content = row[amr1_col]
        amr2_content = row[amr2_col]
        
        # Skip empty rows
        if pd.isna(amr1_content) or pd.isna(amr2_content):
            print(f"  Skipping row {idx + 1}: Empty AMR content")
            results.append("")
            continue
            
        if not str(amr1_content).strip() or not str(amr2_content).strip():
            print(f"  Skipping row {idx + 1}: Empty AMR content after strip")
            results.append("")
            continue
            
        # Process the AMR pair
        try:
            result = process_amr_pair(str(amr1_content), str(amr2_content))
            
            # Convert result to JSON string for Excel cell
            result_json = json.dumps(result, indent=2, ensure_ascii=False)
            results.append(result_json)
            
            print(f"  ✓ Success: Found {result['statistics'].get('amr1_uncommon_nodes', 0)} + {result['statistics'].get('amr2_uncommon_nodes', 0)} uncommon nodes")
            
        except Exception as e:
            print(f"  ✗ Error processing row {idx + 1}: {e}")
            error_result = {"error": str(e), "uncommon_nodes": {"amr1_only": [], "amr2_only": []}, "uncommon_edges": {"amr1_only": [], "amr2_only": []}}
            results.append(json.dumps(error_result, ensure_ascii=False))
    
    # Add results to dataframe
    df[result_col] = results
    
    # Save the results
    print(f"\nSaving results to: {output_file}")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory: {output_dir}")
    
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name or 'Sheet1', index=False)
        
        print(f"✓ Successfully saved {len(results)} results to column {result_col}")
        
        # Print summary
        successful_results = [r for r in results if r and not r.startswith('{"error"')]
        print(f"\nSummary:")
        print(f"  Total rows processed: {len(results)}")
        print(f"  Successful analyses: {len(successful_results)}")
        print(f"  Errors/Empty: {len(results) - len(successful_results)}")
        
    except Exception as e:
        print(f"Error saving results: {e}")
        # Fallback: save as CSV
        csv_file = output_file.replace('.xlsx', '.csv').replace('.xls', '.csv')
        
        # Ensure CSV output directory exists too
        csv_dir = os.path.dirname(csv_file)
        if csv_dir and not os.path.exists(csv_dir):
            os.makedirs(csv_dir, exist_ok=True)
            
        df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"Saved as CSV instead: {csv_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Batch process AMR graphs from spreadsheet columns M and N"
    )
    parser.add_argument("input_file", help="Input Excel file path")
    parser.add_argument("--output", "-o", help="Output Excel file path (default: input_file with _results suffix)")
    parser.add_argument("--sheet", "-s", help="Sheet name to process (default: first sheet)")
    parser.add_argument("--preview", "-p", action="store_true", help="Preview spreadsheet without processing")
    parser.add_argument("--max-rows", type=int, help="Maximum rows to process (for testing)")
    
    args = parser.parse_args()
    
    # Check input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found: {args.input_file}")
        return 1
    
    # Preview mode
    if args.preview:
        preview_spreadsheet(args.input_file, args.sheet)
        return 0
    
    # Set output file
    if args.output:
        output_file = args.output
    else:
        base_name = os.path.splitext(args.input_file)[0]
        ext = os.path.splitext(args.input_file)[1]
        output_file = f"{base_name}_results{ext}"
    
    # Process the spreadsheet
    try:
        if args.max_rows:
            print(f"Processing only first {args.max_rows} rows (test mode)")
            # Load with row limit for testing
            data = pd.read_excel(args.input_file, sheet_name=args.sheet, nrows=args.max_rows)
            
            # Handle dict (multiple sheets) vs DataFrame (single sheet)
            if isinstance(data, dict):
                print(f"Multiple sheets detected: {list(data.keys())}")
                
                # Use specified sheet or first available
                if args.sheet and args.sheet in data:
                    df = data[args.sheet]
                    print(f"Using specified sheet: {args.sheet}")
                else:
                    first_sheet = list(data.keys())[0]
                    df = data[first_sheet]
                    print(f"Using first sheet: {first_sheet}")
                    args.sheet = first_sheet  # Update sheet name for output
            else:
                df = data
                print("Single sheet detected")
            
            # Process limited dataset
            process_spreadsheet_limited(df, output_file, args.sheet)
        else:
            process_spreadsheet(args.input_file, output_file, args.sheet)
        
        print(f"\n🎉 Processing complete!")
        print(f"Results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error during processing: {e}")
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())