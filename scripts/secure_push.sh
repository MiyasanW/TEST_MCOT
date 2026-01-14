#!/bin/bash

# Secure GitHub Push Script
# This script asks for your Token securely and pushes the code.

echo "=========================================="
echo "🚀 Secure GitHub Push Helper"
echo "=========================================="

# 1. Ask for Username (default to MiyasanW)
read -p "Enter GitHub Username [default: MiyasanW]: " USERNAME
USERNAME=${USERNAME:-MiyasanW}

# 2. Ask for Token (Visible Input - easier to check paste)
echo -n "🔑 Enter your Personal Access Token (Paste it here): "
read TOKEN
echo ""

if [ -z "$TOKEN" ]; then
    echo "❌ Error: Token cannot be empty."
    exit 1
fi

# 3. Configure Remote URL with Credentials
# Note: This saves the token in .git/config locally on your machine only.
echo "⚙️ Configuring git remote..."
git remote set-url origin "https://$USERNAME:$TOKEN@github.com/MiyasanW/TEST_MCOT.git"

# 4. Push to GitHub
echo "📦 Pushing Code to GitHub..."
git push origin main

# 5. Check result
if [ $? -eq 0 ]; then
    echo "✅ Success! Code has been pushed to GitHub."
else
    echo "❌ Push Failed. Please check your Token and permissions."
fi
