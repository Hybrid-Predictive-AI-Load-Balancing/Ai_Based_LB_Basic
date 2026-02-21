#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        AI Load Balancer - Quick Test Launcher                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the ai_load_balancer_test directory."
    exit 1
fi

# Show options
echo "Select test mode:"
echo ""
echo "1) Run ALL tests (comprehensive suite - takes time)"
echo "2) Run SINGLE test (choose from list)"
echo "3) Run QUICK test (sudden_spike - fast demo)"
echo "4) Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Running all tests..."
        python main.py
        ;;
    2)
        echo ""
        echo "Available tests:"
        echo ""
        ls -1 test_cases/*.csv | nl -w2 -s') '
        echo ""
        read -p "Enter test number: " testnum
        testfile=$(ls -1 test_cases/*.csv | sed -n "${testnum}p")
        if [ -n "$testfile" ]; then
            echo ""
            echo "🚀 Running: $testfile"
            python main.py "$testfile"
        else
            echo "❌ Invalid selection"
            exit 1
        fi
        ;;
    3)
        echo ""
        echo "🚀 Running quick demo (sudden_spike)..."
        python main.py test_cases/sudden_spike.csv
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Test completed! Check the results/ directory for outputs."
