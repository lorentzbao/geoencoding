#!/usr/bin/env python3
"""
Debug script to test ZENRIN Maps API connection and see request/response details
"""

import requests
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api():
    # Get configuration
    domain = os.getenv('ZENRIN_API_DOMAIN', 'web.zmaps-api.com')
    api_key = os.getenv('ZENRIN_API_KEY')
    auth_method = os.getenv('ZENRIN_AUTH_METHOD', 'ip')
    verify_ssl = os.getenv('ZENRIN_VERIFY_SSL', 'true').lower() != 'false'

    if not api_key:
        print("❌ Error: ZENRIN_API_KEY not found in .env file")
        sys.exit(1)

    # Build headers
    headers = {
        'x-api-key': api_key,
        'Authorization': auth_method
    }

    # Test address
    test_address = "東京都千代田区淡路町2-101"

    # Build parameters
    params = {
        'word': test_address,
        'enc': '0',  # UTF-8
        'datum': 'JGD'
    }

    # Endpoint
    endpoint = f"https://{domain}/data-coding/ac_standard"

    # Setup proxy
    proxies = {}
    if os.environ.get('http_proxy'):
        proxies['http'] = os.environ['http_proxy']
    if os.environ.get('https_proxy'):
        proxies['https'] = os.environ['https_proxy']

    print("=" * 70)
    print("🔍 ZENRIN Maps API Debug Test")
    print("=" * 70)
    print(f"\n📡 Endpoint: {endpoint}")
    print(f"🔐 Auth Method: {auth_method}")
    print(f"🔑 API Key: {api_key[:10]}..." if api_key else "🔑 API Key: None")
    print(f"🌐 SSL Verify: {verify_ssl}")
    print(f"🔄 Proxy: {proxies if proxies else 'None'}")
    print(f"\n📤 Request Headers:")
    for key, value in headers.items():
        if key == 'x-api-key':
            print(f"  {key}: {value[:10]}...")
        else:
            print(f"  {key}: {value}")
    print(f"\n📤 Request Parameters:")
    for key, value in params.items():
        print(f"  {key}: {value}")

    print(f"\n⏳ Sending request...")

    try:
        response = requests.post(
            endpoint,
            data=params,
            headers=headers,
            proxies=proxies if proxies else None,
            verify=verify_ssl,
            timeout=10
        )

        print(f"\n📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")

        print(f"\n📥 Response Body:")
        print(response.text)

        if response.status_code == 200:
            print("\n✅ Success! API is working correctly.")
            try:
                data = response.json()
                print(f"\n📊 Parsed JSON response:")
                import json
                print(json.dumps(data, ensure_ascii=False, indent=2))
            except:
                pass
        else:
            print(f"\n❌ Error: Received status code {response.status_code}")
            print("\nPossible issues:")
            if response.status_code == 400:
                print("  - Invalid request parameters")
                print("  - Incorrect parameter format")
                print("  - Missing required parameters")
            elif response.status_code == 401:
                print("  - Authentication failed")
                print("  - Invalid API key")
                print("  - IP address not whitelisted")
            elif response.status_code == 403:
                print("  - Access forbidden")
                print("  - Domain/Referer not whitelisted")

    except requests.exceptions.SSLError as e:
        print(f"\n❌ SSL Error: {e}")
        print("\nTry setting: ZENRIN_VERIFY_SSL=false in .env")
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print("\nCheck your internet connection and proxy settings")
    except Exception as e:
        print(f"\n❌ Error: {e}")

    print("\n" + "=" * 70)

if __name__ == '__main__':
    test_api()
