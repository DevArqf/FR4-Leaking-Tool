#!/usr/bin/env python3
"""
Test script to check Uptodown connection and version detection
"""
import asyncio
import aiohttp
import re
import sys

def compare_versions(version1, version2):
    """Compare two version strings. Returns 1 if v1 > v2, -1 if v1 < v2, 0 if equal"""
    v1_parts = [int(x) for x in version1.split('.')]
    v2_parts = [int(x) for x in version2.split('.')]
    
    # Pad shorter version with zeros
    max_len = max(len(v1_parts), len(v2_parts))
    v1_parts.extend([0] * (max_len - len(v1_parts)))
    v2_parts.extend([0] * (max_len - len(v2_parts)))
    
    for v1, v2 in zip(v1_parts, v2_parts):
        if v1 > v2:
            return 1
        elif v1 < v2:
            return -1
    return 0

async def test_uptodown_connection():
    """Test the Uptodown connection and version extraction"""
    print("[INFO] Testing Uptodown connection and version detection...")
    print()
    
    # Try multiple URLs to get the latest version
    urls_to_try = [
        'https://fun-run-4.en.uptodown.com/android/download',  # Download page often has latest version
        'https://fun-run-4.en.uptodown.com/android',           # Main page
    ]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    latest_version = None
    latest_version_source = None
    
    try:
        async with aiohttp.ClientSession() as session:
            for url in urls_to_try:
                print(f"[INFO] Connecting to: {url}")
                async with session.get(url, headers=headers) as response:
                    print(f"[INFO] Response status: {response.status}")
                    
                    if response.status != 200:
                        print(f"[WARNING] Failed to fetch from {url}. Status: {response.status}")
                        continue
                    
                    print(f"[INFO] Successfully fetched from: {url}")
                    content = await response.text()
                    print(f"[INFO] Page content length: {len(content)} characters")
                    
                    # Try multiple patterns for version extraction
                    version_patterns = [
                        r'Fun Run 4\s+([\d\.]+)',  # Common format on download pages
                        r'Version\s*([\d\.]+)',   # Direct version format
                        r'([\d]+\.[\d]+\.[\d]+)',  # Generic version pattern
                        r'Version\s*</span>\s*<span[^>]*>([^<]+)</span>',
                        r'<span[^>]*class="[^"]*version[^"]*"[^>]*>([^<]+)</span>',
                        r'"version":\s*"([^"]+)"',
                        r'Version\s+([\d\.]+)',
                        r'v([\d\.]+)',
                        r'Version:\s*([\d\.]+)',
                        r'<div[^>]*version[^>]*>([^<]+)</div>'
                    ]
                    
                    found_version = None
                    pattern_used = None
                    
                    for i, pattern in enumerate(version_patterns, 1):
                        print(f"[INFO] Trying pattern {i}: {pattern}")
                        version_match = re.search(pattern, content, re.IGNORECASE)
                        if version_match:
                            raw_version = version_match.group(1).strip()
                            print(f"[INFO] Raw match: '{raw_version}'")
                            
                            # Clean up version string
                            cleaned_version = re.sub(r'[^\d\.]', '', raw_version)
                            if cleaned_version and len(cleaned_version) > 0:
                                found_version = cleaned_version
                                pattern_used = i
                                print(f"[INFO] Cleaned version: '{found_version}'")
                                break
                        else:
                            print(f"[INFO] No match found")
                    
                    # Compare with current latest version
                    if found_version:
                        if latest_version is None or compare_versions(found_version, latest_version) > 0:
                            latest_version = found_version
                            latest_version_source = url
                            print(f"[INFO] New highest version found: {latest_version} from {url}")
                    
                    print()  # Add spacing between URLs
                    
            # After trying all URLs, check if we found any version
            if latest_version:
                print()
                print(f'[SUCCESS] Found Fun Run 4 version: {latest_version}')
                print(f'[SUCCESS] Best source: {latest_version_source}')
                print('[SUCCESS] Confirmed Fun Run 4 version detected')
                return True, latest_version
            else:
                print()
                print('[WARNING] Could not extract version information from any URL')
                return False, None
                    
    except Exception as e:
        print(f'[ERROR] Connection failed: {str(e)}')
        return False, None

def main():
    """Main function"""
    try:
        success, version = asyncio.run(test_uptodown_connection())
        
        print()
        print("=" * 50)
        if success:
            print("✅ UPDATE CHECK TEST PASSED")
            print(f"   Version detected: {version}")
            print("   The bot should work correctly!")
        else:
            print("❌ UPDATE CHECK TEST FAILED")
            print("   Version detection did not work")
            print("   Check the debug information above")
        print("=" * 50)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print()
        print("[INFO] Test cancelled by user")
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())