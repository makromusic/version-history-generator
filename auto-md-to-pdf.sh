#!/bin/bash

# Access the first command-line argument
filename=$1

# Convert it to html format using md-to-pfd tool
md-to-pdf $filename --as-html --stylesheet ./style.css
