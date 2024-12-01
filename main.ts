import * as path from "jsr:@std/path";

import {
    compress,
    decompress
  } from "https://deno.land/x/zip@v1.2.5/mod.ts";
  import { assert } from "https://deno.land/std@0.133.0/_util/assert.ts";

const GRADING_PATH = Deno.env.get("GRADING_PATH");
const EVALUATION_ZIP_PATH = Deno.env.get("EVALUATION_ZIP_PATH");

const usage = `
usage: GRADING_PATH EVALUATION_ZIP_PATH <command>
`;

if (Deno.args.includes("-h")) {
    console.log(usage);
    Deno.exit(0);
}

if (GRADING_PATH == undefined) {
    console.error("error: GRADING_PATH env variable is required");
    console.log(usage);
    Deno.exit(1);
}

if (EVALUATION_ZIP_PATH == undefined) {
    console.error("error: EVALUATION_ZIP_PATH env variable is required");
    console.log(usage);
    Deno.exit(1);
}

function getDirectoryPath(parent: string, startsWith: string): string {
    let directory: Deno.DirEntry | undefined;
    for (const entry of Deno.readDirSync(parent)) {
        if (entry.isDirectory && 
            entry.name.startsWith(startsWith)
        ) {
            directory = entry;
            break;
        }
    }

    if (directory == undefined) {
        console.log("Couldn't set grading folder");
        Deno.exit(1);
    }

    return Deno.realPathSync(path.join(parent, directory.name));
}

const submissionsPath = getDirectoryPath(getDirectoryPath(GRADING_PATH, "Exercise Sheet"), "Submissions");

if (submissionsPath == undefined) {
    console.error(`Expected a subfolder under: '${GRADING_PATH}'`);
    Deno.exit(1);
}

console.log(`submissions directory: ${submissionsPath}`);

/* for (const submission of Deno.readDirSync(submissionsPath)) {
    console.log(`submission: ${submission.name}`);
} */

// Extract zip file, the file's path is given by the EVALUATION_ZIP_PATH env variable

const EVALUATION_DIR_PATH = await decompress(EVALUATION_ZIP_PATH, await Deno.makeTempDir());

if (EVALUATION_DIR_PATH === false) {
    console.error("failed to decompress zip file");
    Deno.exit(1);
}

console.log(`evaluation directory: ${EVALUATION_DIR_PATH}`);

const evaluationFeedbackDirPath = getDirectoryPath(EVALUATION_DIR_PATH, "multi_feedback_Exercise_Sheet");

// Iterate submissionsPath and export pdf for each submission then put it in the corresponding folder in EVALUATION_DIR_PATH
for (const submission of Deno.readDirSync(submissionsPath)) {
    console.log(`submission: ${submission.name}`);

    for (const evaluationDir of Deno.readDirSync(evaluationFeedbackDirPath)) {
        if (evaluationDir.name === submission.name) {
            const pdfPath = path.join(evaluationFeedbackDirPath, evaluationDir.name, "feedback.pdf");
            /* const exportCommand = new Deno.Command(
                "echo",
                { args: [`echo: ${submission.name}\n`], stdout: "inherit" },
            ) */
            const exportCommand = new Deno.Command(
                "xournalpp", 
                { args: [`--create-pdf=${pdfPath}`], stdout: "inherit" },
            );
            const exportCommandResult = exportCommand.outputSync();
            assert(exportCommandResult.success);
            console.log(`exported ${submission.name}`);
            break;
        }
    }
}