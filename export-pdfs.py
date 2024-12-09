import asyncio
import zipfile
import subprocess
import argparse
import re
import concurrent.futures
from pathlib import Path

def main():
    args = get_args()
    out_dir = Path(args.out_dir)

    out_dir.mkdir(exist_ok=True)

    # Unzip evaluation
    with zipfile.ZipFile(args.multi_feedback_zip_path, 'r') as zip_ref:
        zip_ref.extractall(args.out_dir)
        multi_feedback_dir_name = Path(args.multi_feedback_zip_path).with_suffix('').name
        out_dir = Path(args.out_dir, multi_feedback_dir_name)

    # Iterate through submissions
    submissions_dir = Path(args.submissions_path)

    asyncio.run(handle_submissions(submissions_dir, out_dir))

    print("Finished exporting")
    print(f"Multi feedback directory can be found in: {out_dir}")

async def handle_submissions(submissions_path: Path, out_dir: Path):
    submissions_dir = next(f for f in submissions_path.iterdir() if re.match("Exercise Sheet *", f.name))
    submissions_dir = next(f for f in submissions_dir.iterdir() if re.match("Submissions", f.name))

    tasks = []
    for submission_dir in submissions_dir.iterdir():
        task = asyncio.create_task(handle_submision(submission_dir, out_dir))
        tasks.append(task)
    
    await asyncio.wait(tasks)    

async def handle_submision(submission_dir: Path, out_dir: Path):
    print(f"Exporting submission for: {submission_dir.name}")
        
    # Find first .xopp file in submission directory
    try:
        xournalpp_file = next(f for f in submission_dir.iterdir() if Path(f).suffix == ".xopp")
    except StopIteration:
        print("Warning: No Xournal++ file found, skipping")
        return
                
    print(f"Xournal++ file found: {xournalpp_file}")

    # Find the corresponding feedback directory
    try:
        feedback_dir = next(f for f in out_dir.iterdir() if f.name == submission_dir.name)
    except StopIteration:
        print("Error: couldn't find evaluation folder for the submission, skipping")
        return
    
    # Export pdf using Xournal++
    pdf_path = feedback_dir.joinpath("feedback.pdf")
    print(f"Exporting pdf to: {pdf_path}")

    # Nonblocking call to Xournal++
    process = await asyncio.create_subprocess_exec("xournalpp", str(xournalpp_file), "-p", str(pdf_path))
    await process.wait()

def get_args():
    parser = argparse.ArgumentParser(
        prog="export-pdfs",
        description="Export PDFs from Xournal++ submissions and put them into ILIAS multi feedback zip",
    )
    parser.add_argument("submissions_path", help="Path to the submissions directory containing evaluations")
    parser.add_argument("multi_feedback_zip_path", help="Path to the multi feedback zip file downloaded from ILIAS")
    parser.add_argument("out_dir", help="The output directory. The command will output a multi feedback directory under this directory. You can zip it and upload to ILIAS for multiple evaluation.")

    return parser.parse_args()

main()
