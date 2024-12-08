import zipfile
import subprocess
import argparse
import re
from pathlib import Path

def main():
    args = get_args()

    Path(args.out_dir).mkdir(exist_ok=True)

    # Unzip evaluation
    with zipfile.ZipFile(args.multi_feedback_zip_path, 'r') as zip_ref:
        zip_ref.extractall(args.out_dir)
        multi_feedback_dir_name = Path(args.multi_feedback_zip_path).with_suffix('').name
        out_dir = Path(args.out_dir, multi_feedback_dir_name)

    # Iterate through submissions
    submissions_dir = Path(args.submissions_path)
    submissions_dir = next(f for f in Path(args.submissions_path).iterdir() if re.match("Exercise Sheet *", f.name))
    submissions_dir = next(f for f in submissions_dir.iterdir() if re.match("Submissions", f.name))
    for submission_dir in submissions_dir.iterdir():
        print(f"Exporting submission for: {submission_dir.name}")
        
        # Find first .xopp file in submission directory
        try:
            xournalpp_file = next(f for f in submission_dir.iterdir() if Path(f).suffix == ".xopp")
        except StopIteration:
            print("Warning: No Xournal++ file found, skipping")
            continue
                    
        print(f"Xournal++ file found: {xournalpp_file}")

        # Find the corresponding feedback directory
        try:
            feedback_dir = next(f for f in out_dir.iterdir() if f.name == submission_dir.name)
        except StopIteration:
            print("Error: couldn't find evaluation folder for the submission, skipping")
            continue
        
        # Export pdf using Xournal++
        pdf_path = feedback_dir.joinpath("feedback.pdf")
        print(f"Exporting pdf to: {pdf_path}")
        subprocess.run(["xournalpp", xournalpp_file, "-p", pdf_path])

    print("Finished exporting")
    print(f"Multi feedback directory can be found in: {out_dir}")

def find_first(items, pred):
    for item in items:
        if pred(item):
            return item
    raise ValueError("No matching item found for the given predicate")

def get_args():
    parser = argparse.ArgumentParser(
        prog="export-pdfs",
        description="Export PDFs from Xournal++ submissions and put them into ILIAS multi feedback zip",
    )
    parser.add_argument("submissions_path", help="Path to the submissions directory containing evaluations")
    parser.add_argument("multi_feedback_zip_path", help="Path to the multi feedback zip file downloaded from ILIAS")
    parser.add_argument("out_dir", help="The output directory. The command will output a multi feedback directory under this directory. You can zip it and upload to ILIAS for multiple evaluation.")

    return parser.parse_args()

def get_first_matching(items, pattern):
    for child in items:
        if re.match(pattern, child):
            return child
    return None

main()
