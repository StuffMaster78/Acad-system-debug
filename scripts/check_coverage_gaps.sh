#!/bin/bash

# Coverage Gap Analysis Script
# Identifies files with low coverage to prioritize testing

set -e

echo "🔍 Analyzing Coverage Gaps"
echo "============================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check backend coverage
if [ -f "backend/coverage.xml" ]; then
    echo -e "${YELLOW}📊 Backend Coverage Analysis${NC}"
    echo ""
    
    # Extract files with coverage < 95%
    python3 << 'EOF'
import xml.etree.ElementTree as ET
import sys

try:
    tree = ET.parse('backend/coverage.xml')
    root = tree.getroot()
    
    low_coverage_files = []
    
    for package in root.findall('.//package'):
        for class_elem in package.findall('.//class'):
            filename = class_elem.get('filename', '')
            line_rate = float(class_elem.get('line-rate', 0))
            
            if line_rate < 0.95 and filename:
                low_coverage_files.append({
                    'file': filename,
                    'coverage': line_rate * 100
                })
    
    if low_coverage_files:
        print("Files with coverage < 95%:")
        print("-" * 60)
        for item in sorted(low_coverage_files, key=lambda x: x['coverage']):
            print(f"{item['file']:50} {item['coverage']:5.1f}%")
        print(f"\nTotal: {len(low_coverage_files)} files need more tests")
    else:
        print("✅ All files have 95%+ coverage!")
        
except FileNotFoundError:
    print("❌ Coverage report not found. Run tests first:")
    print("   make test-coverage-backend")
except Exception as e:
    print(f"Error: {e}")
EOF
else
    echo -e "${RED}❌ Backend coverage report not found${NC}"
    echo "Run: make test-coverage-backend"
fi

echo ""
echo "============================"
echo ""

# Check frontend coverage
if [ -f "frontend/coverage/coverage-final.json" ]; then
    echo -e "${YELLOW}📊 Frontend Coverage Analysis${NC}"
    echo ""
    
    node << 'EOF'
const fs = require('fs');
const path = require('path');

try {
    const coverage = JSON.parse(
        fs.readFileSync('frontend/coverage/coverage-final.json', 'utf8')
    );
    
    const lowCoverageFiles = [];
    
    for (const [file, data] of Object.entries(coverage)) {
        const statements = data.s || {};
        const covered = Object.values(statements).filter(s => s > 0).length;
        const total = Object.keys(statements).length;
        const coverage = total > 0 ? (covered / total) * 100 : 0;
        
        if (coverage < 95 && !file.includes('node_modules')) {
            lowCoverageFiles.push({
                file: file.replace(process.cwd() + '/', ''),
                coverage: coverage.toFixed(1)
            });
        }
    }
    
    if (lowCoverageFiles.length > 0) {
        console.log('Files with coverage < 95%:');
        console.log('-'.repeat(60));
        lowCoverageFiles
            .sort((a, b) => parseFloat(a.coverage) - parseFloat(b.coverage))
            .slice(0, 20)
            .forEach(item => {
                console.log(`${item.file.padEnd(50)} ${item.coverage.padStart(5)}%`);
            });
        console.log(`\nTotal: ${lowCoverageFiles.length} files need more tests`);
    } else {
        console.log('✅ All files have 95%+ coverage!');
    }
} catch (error) {
    console.error('❌ Coverage report not found. Run tests first:');
    console.error('   make test-coverage-frontend');
}
EOF
else
    echo -e "${RED}❌ Frontend coverage report not found${NC}"
    echo "Run: make test-coverage-frontend"
fi

echo ""
echo "============================"
echo ""
echo "💡 Tip: Focus on files with lowest coverage first"
echo ""

