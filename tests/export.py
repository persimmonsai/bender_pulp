#!/usr/bin/env python3
# This script was generated automatically by bender.

import os
import sys
import shutil
import argparse
import hashlib

def get_dir_hash(dir_path):
    hasher = hashlib.sha256()
    if not os.path.exists(dir_path):
        return hasher.hexdigest()
    for root, dirs, files in os.walk(dir_path, topdown=True):
        dirs.sort()
        for name in sorted(files):
            file_path = os.path.join(root, name)
            try:
                with open(file_path, "rb") as f:
                    rel_path = os.path.relpath(file_path, dir_path)
                    hasher.update(rel_path.encode('utf-8'))
                    hasher.update(f.read())
            except OSError:
                pass
    return hasher.hexdigest()

def get_file_hash(file_path):
    hasher = hashlib.sha256()
    if not os.path.exists(file_path):
        return hasher.hexdigest()
    try:
        with open(file_path, "rb") as f:
            hasher.update(f.read())
    except OSError:
        pass
    return hasher.hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Export sources and generate Synopsys TCL script.")
    parser.add_argument("--outdir", default="export", help="Output directory for the exported files")
    args = parser.parse_args()

    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    tcl_script_path = os.path.join(outdir, "synopsys_export.tcl")

    # Python representation of bender data
    verilog_args = []
    vhdl_args = []

    compilation_mode = "separate"


    groups = [

        {
            "metadata": "Package(dummy) Target(*)",
            "file_type": "verilog",
            "incdirs": [

            ],
            "defines": [

                ("TARGET_ALL", ""),

                ("TARGET_SYNOPSYS", ""),

                ("TARGET_SYNTHESIS", ""),

            ],
            "files": [

                ("/home/uge/Development/bender_pulp/tests/foo.v", ""),

            ],
        },

    ]


    file_map = {}
    incdir_map = {}

    with open(tcl_script_path, "w") as tcl:
        tcl.write("# This script was generated automatically by bender.\n")
        tcl.write("set search_path_initial $search_path\n")

        for group in groups:

            tcl.write("set search_path $search_path_initial\n")

            for incdir in group["incdirs"]:
                if incdir not in incdir_map:
                    new_incdir_name = get_dir_hash(incdir)[:16]
                    new_incdir_path = os.path.join(outdir, new_incdir_name)
                    if os.path.exists(incdir):
                        shutil.copytree(incdir, new_incdir_path)
                    else:
                        print(f"Warning: include dir {incdir} does not exist", file=sys.stderr)
                        os.makedirs(new_incdir_path, exist_ok=True)
                    incdir_map[incdir] = new_incdir_name

                tcl.write(f"lappend search_path [file join [file dirname [info script]] {incdir_map[incdir]}]\n")


            tcl.write("if {0 == [")

            
            if group["file_type"] == "verilog":
                tcl.write("analyze -format sv ")
                for arg in verilog_args:
                    tcl.write(f"{arg} ")
            elif group["file_type"] == "vhdl":
                tcl.write("analyze -format vhdl ")
                for arg in vhdl_args:
                    tcl.write(f"{arg} ")


            for k, v in group["defines"]:
                if v:
                    tcl.write(f"-define {{{k}={v}}} ")
                else:
                    tcl.write(f"-define {{{k}}} ")


            tcl.write("[list \\\n")

            for file_path, comment in group["files"]:

                if file_path not in file_map:
                    new_file_dir_name = get_file_hash(file_path)[:16]
                    new_file_dir_path = os.path.join(outdir, new_file_dir_name)
                    os.makedirs(new_file_dir_path, exist_ok=True)
                    basename = os.path.basename(file_path)
                    new_file_path = os.path.join(new_file_dir_path, basename)
                    if os.path.exists(file_path):
                        shutil.copy2(file_path, new_file_path)
                    else:
                        print(f"Warning: file {file_path} does not exist", file=sys.stderr)
                        # create an empty file just in case
                        open(new_file_path, "w").close()
                    file_map[file_path] = os.path.join(new_file_dir_name, basename)

                tcl.write(f"    [file join [file dirname [info script]] {file_map[file_path]}] \\\n")


            tcl.write("]]} {return 1}\n")


        if not groups:
            # If there's no files at all, still valid
            pass

        tcl.write("set search_path $search_path_initial\n")

if __name__ == "__main__":
    main()
