#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/notofonts/noto-cjk.git"
DIR="noto-cjk"
SPARSE_PATH="Sans/Variable/TTF/Subset Serif/Variable/TTF/Subset"

if [ -d "$DIR/.git" ]; then
	echo "Updating existing clone..."
	cd "$DIR"
	git fetch --depth=1 --filter=blob:none origin
	git sparse-checkout set $SPARSE_PATH
	git merge --ff-only origin/HEAD
else
	echo "Cloning repo..."
	git clone --depth 1 \
		--filter=blob:none \
		--sparse \
		"$REPO_URL" \
		"$DIR"
	cd "$DIR"
	git sparse-checkout set $SPARSE_PATH
fi

echo "Done."
