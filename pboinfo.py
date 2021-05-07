#!/usr/bin/env python
import subprocess
import pathlib
import json
import sys
import argparse
from packaging import version
import urllib.request
import re
from datetime import datetime

platform="wsl"

try:
    with urllib.request.urlopen(
            'https://raw.githubusercontent.com/zeusops/mission-templates/'
            'master/Zeus_yymmdd_Template.Stratis/template_version.txt') as f:
        data = f.read().decode('utf-8')
    latest_version=version.parse(data)
except urllib.error.HTTPError:
    latest_version=None

parser = argparse.ArgumentParser(description="Parse pbo info")
parser.add_argument('filename', metavar='FILE', help="PBO file to check")
args = parser.parse_args()

if platform=="windows":
    missionpath="C:\server\link\mpmissions"
elif platform=="wsl":
    missionpath="/mnt/c/server/link/mpmissions"
else:
    missionpath="/home/zeusops/link/mpmissions"

missions=pathlib.Path(missionpath)

#filename="Zeus_190920_Petterson.vt7.pbo"
filename=args.filename

match=re.search("^Zeus_(\d\d\d\d\d\d)_", filename)
if match:
    date_string=match.group(1)
    try:
        filename_date=datetime.strptime(date_string, '%y%m%d') \
                      .date().isoformat()
    except ValueError:
        # Couldn't find a date in filename, this is not necessarily an error
        filename_date="INVALID FORMAT"
else:
    filename_date="INVALID FORMAT"

# TODO: Make path portable
try:
    output=subprocess.check_output(["/home/zeusops/files/bin/pboinfo", "-j",
                                   str(missions / filename)], timeout=10)
except subprocess.CalledProcessError as e:
    print("Call to pboinfo failed:")
    print(e.output.decode('utf-8'))
    sys.exit(1)
info=json.loads(output)
#print(info)
if info['version'] != 'NOTFOUND':
    if latest_version:
        pbo_version=version.parse(info['version'])
        if pbo_version < latest_version:
            version_info="PBO uses an outdated template version: {}, latest version: {}" \
                        .format(pbo_version, latest_version)
        else:
            version_info="PBO template version is up to date ({})".format(pbo_version)
    else:
        version_info="Couldn't check latest template version"
else:
    version_info="No template version found"

print("""PBO information:

Date from filename: {}
Operation name: {}
Author: {}
Faction: {}
{}""".format(filename_date, info['operation'], info['author'], info['faction'], version_info))
