#!/bin/bash
set -e

INSTALL_DIR="$HOME/.local/bin"
GO_VERSION="1.23.5"
LEAN_VERSION="v4.25.0"

mkdir -p "$INSTALL_DIR"

# Check for Go
if ! command -v go &> /dev/null; then
    echo "Error: Go not found. Please install Go ${GO_VERSION} or later."
    echo "Download from: https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz"
    exit 1
fi

# Install landrun
echo "Installing landrun..."
GOBIN="$INSTALL_DIR" go install github.com/zouuup/landrun/cmd/landrun@latest

# Build lean4export
echo "Building lean4export..."
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
git clone --quiet https://github.com/leanprover/lean4export.git "$TMPDIR/lean4export"
cd "$TMPDIR/lean4export"
echo "leanprover/lean4:${LEAN_VERSION}" > lean-toolchain
lake build > /dev/null
cp .lake/build/bin/lean4export "$INSTALL_DIR/"

# Build comparator
echo "Building comparator..."
git clone --quiet https://github.com/leanprover/comparator.git "$TMPDIR/comparator"
cd "$TMPDIR/comparator"
lake build > /dev/null
cp .lake/build/bin/comparator "$INSTALL_DIR/"

# Verify
if [ -f "$INSTALL_DIR/landrun" ] && \
   [ -f "$INSTALL_DIR/lean4export" ] && \
   [ -f "$INSTALL_DIR/comparator" ]; then
    echo "Installation complete: $INSTALL_DIR"
    if ! echo "$PATH" | grep -q "$INSTALL_DIR"; then
        echo "Note: Add to PATH: export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
else
    echo "Installation failed"
    exit 1
fi
