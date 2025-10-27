#!/bin/bash

# Rift Rewind Frontend - Development Server Startup Script
# This script sets up the environment and starts the Vite development server

set -e  # Exit on error

echo "🎮 Rift Rewind Frontend - Starting Production Preview Server"
echo "=================================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed!"
    echo "📥 Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo ""
    echo "📦 node_modules not found. Installing dependencies..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  Warning: .env file not found!"
    
    if [ -f ".env.example" ]; then
        echo "📝 Creating .env from .env.example..."
        cp .env.example .env
        echo ""
        echo "⚠️  IMPORTANT: Please edit .env with your Supabase credentials!"
        echo ""
        echo "Required configuration:"
        echo "  1. VITE_SUPABASE_URL - Your Supabase project URL"
        echo "  2. VITE_SUPABASE_ANON_KEY - Your Supabase anon/public key"
        echo "  3. VITE_API_BASE_URL - Backend API URL (default: http://localhost:8000)"
        echo ""
        echo "Get your Supabase credentials from:"
        echo "  https://supabase.com → Your Project → Settings → API"
        echo ""
        read -p "Press Enter to continue after editing .env, or Ctrl+C to exit..."
    else
        echo "❌ Error: .env.example not found!"
        exit 1
    fi
else
    echo "✅ .env file found"
fi

# Validate .env has required variables
if grep -q "your-project.supabase.co" .env 2>/dev/null || grep -q "your-supabase-anon-key" .env 2>/dev/null; then
    echo ""
    echo "⚠️  WARNING: .env contains placeholder values!"
    echo "Please update your .env file with real Supabase credentials."
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Startup cancelled. Please configure .env first."
        exit 1
    fi
fi

echo ""
echo "🚀 Building and starting production preview server..."
echo "=================================================="
echo ""

# Build for production
echo "📦 Building production bundle..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo ""
echo "✅ Build complete!"
echo ""
echo "📱 Frontend will be available at: http://localhost:4173"
echo "🏭 Production mode (no HMR)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the production preview server
npm run preview
