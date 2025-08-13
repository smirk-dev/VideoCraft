# Scripts Directory

This directory contains utility scripts for testing, setup, and maintenance of the VideoCraft project.

## 📁 Directory Structure

### `/setup/` - Setup and Configuration Scripts
- `setup_venv.ps1` - PowerShell script to set up virtual environment
- `check_deps.py` - Dependency checker and validator
- `fix_all_timestamp_access.py` - Utility to fix timestamp access patterns
- `fix_timestamp_access.py` - Timestamp access pattern fixer

### `/test_scripts/` - Test and Validation Scripts
- `test_all_fixes.py` - Comprehensive test suite for all fixes
- `test_complete_fix.py` - Complete integration testing
- `test_complete_slider_fix.py` - Slider component testing
- `test_content_analyzer.py` - Content analyzer testing
- `test_cut_suggestion.py` - Cut suggestion functionality testing
- `test_cut_suggestion_update.py` - Cut suggestion update testing
- `test_deployment.py` - Deployment validation testing
- `test_exact_error.py` - Specific error condition testing
- `test_final_fixes.py` - Final integration testing
- `test_final_integration.py` - Complete integration validation
- `test_offline.py` - Offline functionality testing
- `test_parsing.py` - Script parsing testing
- `test_professional_exporter_fix.py` - Professional export testing
- `test_subscriptable_fix.py` - Subscriptable type fixes testing
- `test_type_mismatch_fix.py` - Type mismatch resolution testing
- `quick_verification.py` - Quick project health check

## 🚀 Quick Usage

### Setup New Environment
```bash
# Windows
./scripts/setup/setup_venv.ps1

# Check dependencies
python scripts/setup/check_deps.py
```

### Run Tests
```bash
# Run all tests
python scripts/test_scripts/test_all_fixes.py

# Quick verification
python scripts/test_scripts/quick_verification.py

# Specific component tests
python scripts/test_scripts/test_content_analyzer.py
```

### Maintenance
```bash
# Fix timestamp access patterns
python scripts/setup/fix_all_timestamp_access.py
```

## 📋 Test Coverage

- ✅ Core functionality testing
- ✅ Integration testing  
- ✅ Error handling validation
- ✅ Offline functionality testing
- ✅ Export functionality testing
- ✅ UI component testing
- ✅ Performance validation

---

*All scripts are maintained and tested for the latest version of VideoCraft*
