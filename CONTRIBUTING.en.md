# Contributing Guide

Thank you for your interest in contributing to this project! This repository provides an open-source AI toolkit for Amazon cross-border e-commerce sellers.

## Core Principles

1. **Target This Fork Only**: Pull requests, pushes, and releases must strictly target `SanHsien/amazon-sorftime-research-MCP-skill`. Upstream PRs are strictly prohibited unless explicitly authorized.
2. **Windows-first Development**: All scripts and tools must be verified on Windows 11 + PowerShell.
3. **Pre-commit Gate**: All changes must pass the local dev check gate prior to commit:
   ```powershell
   pwsh -NoProfile -File tools/dev_check.ps1 -Quick
   ```

## Development Workflow

1. Fork this repository to your own account.
2. Clone locally and install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Create a feature branch for your changes.
4. Add or update tests where appropriate.
5. Run `pwsh -NoProfile -File tools/dev_check.ps1` to ensure all checks are green.
6. Open a Pull Request targeting `SanHsien/amazon-sorftime-research-MCP-skill:main`.

