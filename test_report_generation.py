#!/usr/bin/env python3
"""
Test script to verify that reports are being generated in the correct location
"""

import os
import tempfile
import shutil
from gemini_client import ReportGenerator

def test_report_generation_path():
    """Test that reports are generated in files/reports directory"""
    print("Testing report generation path...")
    
    # Create a temporary test analysis
    test_analysis = {
        'article_title': 'Test Bitcoin Mining Article',
        'article_url': 'https://example.com/test-article',
        'analysis_text': 'This is a test analysis of a Bitcoin mining article.',
        'analysis_timestamp': '2025-09-20T16:59:00Z',
        'model_used': 'gemini-1.5-flash'
    }
    
    # Use a temp directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_reports_dir = os.path.join(temp_dir, "files", "reports")
        
        # Initialize ReportGenerator with test directory
        report_gen = ReportGenerator(reports_dir=test_reports_dir)
        
        # Generate report
        report_path = report_gen.save_analysis_report(test_analysis)
        
        # Verify report was created in correct location
        assert report_path is not None, "Report path should not be None"
        assert os.path.exists(report_path), f"Report file should exist at {report_path}"
        assert "files/reports" in report_path, f"Report path should contain 'files/reports': {report_path}"
        
        # Verify content
        with open(report_path, 'r') as f:
            content = f.read()
            assert "Test Bitcoin Mining Article" in content, "Report should contain article title"
            assert "This is a test analysis" in content, "Report should contain analysis text"
            assert "gemini-1.5-flash" in content, "Report should contain model info"
        
        print(f"✅ Report generated successfully at: {report_path}")
        print(f"✅ Report path contains 'files/reports': {'files/reports' in report_path}")
        
    return True

def test_default_path():
    """Test that default path is files/reports"""
    print("Testing default report path...")
    
    report_gen = ReportGenerator()
    assert report_gen.reports_dir == "files/reports", f"Default path should be 'files/reports', got '{report_gen.reports_dir}'"
    
    print("✅ Default path is correctly set to 'files/reports'")
    return True

if __name__ == "__main__":
    success = True
    success &= test_default_path()
    success &= test_report_generation_path()
    
    if success:
        print("\n✅ All report generation tests passed!")
        print("✅ Reports will be saved to files/reports directory")
        print("✅ GitHub Actions will commit these reports when GEMINI_API_KEY is configured")
    else:
        print("\n❌ Some tests failed!")
        exit(1)