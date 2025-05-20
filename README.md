# Automated Markdown Module Extractor

## Description
The Automated Markdown Module Extractor is a Python-based tool designed to streamline the processing of markdown course content. It scans multiple .md files, extracts learning modules and their titles, injects relevant resources, cleans up undesired trailing content, and generates clean, well-structured module files in sequential order.

This tool ensures:

- Each module is saved as a separate markdown file.

- Files are named using a consistent numbering format (1-title.md, 2-title.md, etc.) to preserve learning flow.
- Unwanted content after the "Expected Learning Outcome" section is removed.
- A standardized footer (copyright notice) is added.

## Features

- Asynchronous I/O operations for improved performance.

- DRY (Don't Repeat Yourself) code principles.
-Automatic resource injection into each module.
- Built-in cleanup of source and temporary files.
