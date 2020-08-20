#!/usr/bin/env python3

import argparse
import subprocess
import os
import re

def get_manifest(platform_dir):
	dirname = os.path.dirname(__file__)
	manifest_path = os.path.join(dirname, "../" + platform_dir + "/manifest")

	with open(manifest_path, 'r') as manifest_file:
		manifest_content = manifest_file.read()

	manifest = {}
	for line in manifest_content.split('\n'):
		match = re.match("^(\S+)\s*:\s*(.*)$", line)
		if match:
			manifest[match.groups()[0]] = match.groups()[1]

	return manifest

def build(platform, project_dir, skip, device_id, target):
	if not skip:
		try:
			manifest = get_manifest(platform)

			dirname = os.path.dirname(__file__)
			subprocess.check_output(["appc", "run", "-d", os.path.join(dirname, "../" + platform), "-p", platform, "--build-only"])
			zip_platform = "iphone" if platform == "ios" else "android"
			subprocess.check_output(["unzip", "-o", os.path.join(dirname, "../" + platform + "/dist/" + manifest["moduleid"] + "-" + zip_platform + "-" + manifest["version"] + ".zip"), "-d", project_dir])
		except subprocess.CalledProcessError as e:
			raise Exception("failed to create module")

	command = ["appc", "run", "-d", project_dir, "-p", platform, "-T", target]
	if device_id:
		command.append("-C")
		command.append(device_id)

	subprocess.call(command)

if __name__ == '__main__':

	parser = argparse.ArgumentParser()

	parser.add_argument("-d", "--project-dir",  required=True)
	parser.add_argument('--skip-build', action='store_true')
	parser.add_argument("-p", "--platform",  choices=['ios', 'iphone', 'android'], default='ios')
	parser.add_argument("-T", "--target",  choices=['emulator', 'device'], default='emulator')
	parser.add_argument("-C", "--device-id")

	args = parser.parse_args()

	if args.target == 'emulator' and args.platform == 'ios':
		args.target = 'simulator';

	build(args.platform, args.project_dir, args.skip_build, args.device_id, args.target)