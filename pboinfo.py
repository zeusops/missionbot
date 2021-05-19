#!/usr/bin/env python3
import os
import subprocess
import json
import sys
import argparse
from packaging import version
import urllib.request
import re
from datetime import datetime


def get_info(filename):
    try:
        with urllib.request.urlopen(
                'https://raw.githubusercontent.com/zeusops/mission-templates/'
                'master/Zeus_yymmdd_Template.Stratis/'
                'template_version.txt') as f:
            data = f.read().decode('utf-8')
        latest_version = version.parse(data)
    except urllib.error.HTTPError:
        latest_version = None

    home = os.environ['HOME']

    match = re.search("^Zeus_(\\d\\d\\d\\d\\d\\d)_",
                      os.path.basename(filename))
    if match:
        date_string = match.group(1)
        try:
            filename_date = datetime.strptime(date_string, '%y%m%d') \
                          .date().isoformat()
        except ValueError:
            # Couldn't find a date in filename, this is not necessarily an
            # error
            filename_date = "INVALID FORMAT"
    else:
        filename_date = "INVALID FORMAT"

    # TODO: Make path more portable
    try:
        output = subprocess.check_output([f"{home}/files/bin/pboinfo", "-j",
                                          filename], timeout=10)
    except subprocess.CalledProcessError as e:
        print("Call to pboinfo failed:")
        print(e.output.decode('utf-8'))
        return False
    info = json.loads(output)
    if info['version'] != 'NOTFOUND':
        if latest_version:
            pbo_version = version.parse(info['version'])
            if pbo_version < latest_version:
                version_info = (f"PBO uses an outdated template version: "
                                f"{pbo_version}, latest version: "
                                f"{latest_version}")
            else:
                version_info = ("PBO template version is up to date "
                                f"({pbo_version})")
        else:
            version_info = "Couldn't check latest template version"
    else:
        version_info = "No template version found"

    return (f"PBO information:\n"
            f"\n"
            f"Date from filename: {filename_date}\n"
            f"Operation name: {info['operation']}\n"
            f"Author: {info['author']}\n"
            f"Faction: {info['faction']}\n"
            f"{version_info}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse pbo info")
    parser.add_argument('filename', metavar='FILE', help="PBO file to check")
    args = parser.parse_args()

    ret = get_info(args.filename)
    if not ret:
        sys.exit(1)
    else:
        print(ret)
