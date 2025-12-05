#!/usr/bin/env python3
"""
Japanese Address Geocoding Program
Uses ZENRIN Maps API to convert Japanese addresses to coordinates
"""

import requests
import json
import sys
import os
import argparse
import warnings
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv
from urllib3.exceptions import InsecureRequestWarning


class ZenrinGeocoder:
    """Geocoder for Japanese addresses using ZENRIN Maps API"""

    def __init__(self,
                 api_domain: str,
                 api_key: Optional[str] = None,
                 auth_method: str = "ip",
                 referer: Optional[str] = None,
                 token: Optional[str] = None,
                 verify_ssl: bool = True):
        """
        Initialize the geocoder

        Args:
            api_domain: API domain (e.g., 'web.zmaps-api.com')
            api_key: API key (sent via x-api-key header)
            auth_method: Authentication method ('ip', 'referer', or 'bearer')
            referer: Referer URL (required when auth_method='referer')
            token: OAuth 2.0 token (required when auth_method='bearer')
            verify_ssl: Verify SSL certificates (default: True)
        """
        self.api_domain = api_domain
        self.api_key = api_key
        self.auth_method = auth_method
        self.referer = referer
        self.token = token
        self.verify_ssl = verify_ssl
        self.endpoint = f"https://{api_domain}/data-coding/ac_standard"

        # Suppress SSL warnings if verification is disabled
        if not self.verify_ssl:
            warnings.simplefilter('ignore', InsecureRequestWarning)

        # Setup proxy configuration from environment variables
        self.proxies = {}
        if os.environ.get('http_proxy'):
            self.proxies['http'] = os.environ['http_proxy']
        if os.environ.get('https_proxy'):
            self.proxies['https'] = os.environ['https_proxy']

    def _get_headers(self) -> Dict[str, str]:
        """Build authentication headers based on auth method"""
        headers = {}

        if self.api_key:
            headers['x-api-key'] = self.api_key

        if self.auth_method == 'ip':
            headers['Authorization'] = 'ip'
        elif self.auth_method == 'referer':
            headers['Authorization'] = 'referer'
            if self.referer:
                headers['Referer'] = self.referer
        elif self.auth_method == 'bearer':
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'

        return headers

    def geocode(self,
                address: str,
                enc: int = 0,
                use_kana: bool = False,
                use_multi_addr: bool = False,
                match_level: Optional[str] = None,
                datum: str = "JGD") -> Dict:
        """
        Geocode a Japanese address

        Args:
            address: Japanese address string
            enc: Character encoding (0=UTF-8, 1=EUC-JP, 2=Shift-JIS)
            use_kana: Enable kana address matching
            use_multi_addr: Enable duplicate address output
            match_level: Minimum matching hierarchy (TOD/SHK/OAZ/AZC/GIK/TBN)
            datum: Geodetic system (JGD, TOKYO, TOKYO_NAVI)

        Returns:
            Dictionary containing geocoding results
        """
        params = {
            'word': address,
            'enc': str(enc),
            'datum': datum
        }

        # Add optional boolean parameters (convert Python bool to API format)
        if use_kana:
            params['use_kana'] = 'true'
        if use_multi_addr:
            params['use_multi_addr'] = 'true'
        if match_level:
            params['match_level'] = match_level

        headers = self._get_headers()

        try:
            response = requests.post(self.endpoint, data=params, headers=headers,
                                   proxies=self.proxies if self.proxies else None,
                                   verify=self.verify_ssl, timeout=10)
            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            # Extract items from ZENRIN API response structure
            # Response format: {"status": "...", "result": {"info": {...}, "item": [...]}}
            if 'result' in data and 'item' in data['result']:
                items = data['result']['item']
                # Return first item for single address geocoding
                if items and len(items) > 0:
                    return items[0]
                else:
                    return {'error': 'No results found'}
            else:
                # If response structure is different, return as-is
                return data

        except requests.exceptions.HTTPError as e:
            # Return detailed error information
            error_detail = {
                'error': str(e),
                'status_code': response.status_code,
                'response_text': response.text[:500] if hasattr(response, 'text') else None
            }
            return error_detail
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def geocode_batch(self, addresses: List[str], **kwargs) -> List[Dict]:
        """
        Geocode multiple addresses (up to 100)

        Args:
            addresses: List of Japanese address strings
            **kwargs: Additional parameters for geocode()

        Returns:
            List of dictionaries containing geocoding results
        """
        if len(addresses) > 100:
            raise ValueError("Maximum 100 addresses per batch")

        params = {
            'word': ','.join(addresses),
            'enc': str(kwargs.get('enc', 0)),
            'datum': kwargs.get('datum', 'JGD')
        }

        # Add optional boolean parameters
        if kwargs.get('use_kana'):
            params['use_kana'] = 'true'
        if kwargs.get('use_multi_addr'):
            params['use_multi_addr'] = 'true'
        if 'match_level' in kwargs:
            params['match_level'] = kwargs['match_level']

        headers = self._get_headers()

        try:
            response = requests.post(self.endpoint, data=params, headers=headers,
                                   proxies=self.proxies if self.proxies else None,
                                   verify=self.verify_ssl, timeout=30)
            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            # Extract items from ZENRIN API response structure
            # Response format: {"status": "...", "result": {"info": {...}, "item": [...]}}
            if 'result' in data and 'item' in data['result']:
                return data['result']['item']
            else:
                # If response structure is different, return as-is
                return [data]

        except requests.exceptions.HTTPError as e:
            # Return detailed error information
            error_detail = {
                'error': str(e),
                'status_code': response.status_code,
                'response_text': response.text[:500] if hasattr(response, 'text') else None
            }
            return [error_detail]
        except requests.exceptions.RequestException as e:
            return [{'error': str(e)}]


def format_result(result: Dict) -> str:
    """Format geocoding result for display"""
    if 'error' in result:
        error_msg = f"エラー: {result['error']}"
        if 'status_code' in result:
            error_msg += f"\nステータスコード: {result['status_code']}"
        if 'response_text' in result and result['response_text']:
            error_msg += f"\nレスポンス: {result['response_text']}"
        return error_msg

    output = []
    output.append("=" * 60)

    if 'results' in result:
        for idx, item in enumerate(result['results'], 1):
            if idx > 1:
                output.append("-" * 60)
            output.append(format_single_result(item))
    else:
        output.append(format_single_result(result))

    output.append("=" * 60)
    return "\n".join(output)


def format_single_result(item: Dict) -> str:
    """Format a single result item"""
    output = []

    # Full address
    if 'address' in item:
        output.append(f"住所: {item['address']}")

    # Coordinates (API uses match_position array)
    if 'match_position' in item and item['match_position']:
        coords = item['match_position']
        output.append(f"経度: {coords[0]}")
        output.append(f"緯度: {coords[1]}")

    # Match level
    if 'match_level' in item:
        output.append(f"マッチレベル: {item['match_level']}")

    # Postal code (API uses post_code)
    if 'post_code' in item:
        output.append(f"郵便番号: {item['post_code']}")

    # Prefecture (API uses address2)
    if 'address2' in item:
        output.append(f"都道府県: {item['address2']}")

    # Municipality (API uses address3)
    if 'address3' in item:
        output.append(f"市区町村: {item['address3']}")

    # District (API uses address4)
    if 'address4' in item:
        output.append(f"町域: {item['address4']}")

    # Building ZID (nested in building_info)
    if 'building_info' in item and item['building_info']:
        building = item['building_info']
        if 'zid' in building:
            output.append(f"ZID: {building['zid']}")

    return "\n".join(output)


def main():
    # Load environment variables from .env file
    load_dotenv()

    parser = argparse.ArgumentParser(
        description='Japanese Address Geocoding using ZENRIN Maps API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using .env file (recommended)
  %(prog)s --address "東京都千代田区淡路町2-101"

  # IP-based authentication
  %(prog)s --domain web.zmaps-api.com --key YOUR_API_KEY --auth-method ip --address "東京都千代田区淡路町2-101"

  # Referer-based authentication
  %(prog)s --domain web.zmaps-api.com --key YOUR_API_KEY --auth-method referer --referer "https://example.com" --address "東京都千代田区淡路町2-101"

  # OAuth 2.0 authentication
  %(prog)s --domain web.zmaps-api.com --key YOUR_API_KEY --auth-method bearer --token YOUR_TOKEN --address "東京都千代田区淡路町2-101"

  # Batch processing
  %(prog)s --batch addresses.txt --output results.json

  # Interactive mode
  %(prog)s --interactive
        """
    )

    parser.add_argument('--domain', help='API domain (e.g., web.zmaps-api.com) [env: ZENRIN_API_DOMAIN]')
    parser.add_argument('--key', help='API key (sent via x-api-key header) [env: ZENRIN_API_KEY]')
    parser.add_argument('--auth-method', choices=['ip', 'referer', 'bearer'],
                        help='Authentication method [env: ZENRIN_AUTH_METHOD]')
    parser.add_argument('--referer', help='Referer URL (required for referer auth) [env: ZENRIN_REFERER]')
    parser.add_argument('--token', help='OAuth 2.0 token (required for bearer auth) [env: ZENRIN_TOKEN]')
    parser.add_argument('--address', help='Single address to geocode')
    parser.add_argument('--batch', help='File containing addresses (one per line)')
    parser.add_argument('--output', help='Output file for JSON results')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--datum', choices=['JGD', 'TOKYO', 'TOKYO_NAVI'],
                        help='Geodetic system [env: ZENRIN_DATUM]')
    parser.add_argument('--match-level', choices=['TOD', 'SHK', 'OAZ', 'AZC', 'GIK', 'TBN'],
                        help='Minimum matching hierarchy [env: ZENRIN_MATCH_LEVEL]')
    parser.add_argument('--no-verify-ssl', action='store_true',
                        help='Disable SSL certificate verification (not recommended) [env: ZENRIN_VERIFY_SSL]')

    args = parser.parse_args()

    # Get configuration from environment variables with command-line override
    domain = args.domain or os.getenv('ZENRIN_API_DOMAIN')
    api_key = args.key or os.getenv('ZENRIN_API_KEY')
    auth_method = args.auth_method or os.getenv('ZENRIN_AUTH_METHOD', 'ip')
    referer = args.referer or os.getenv('ZENRIN_REFERER')
    token = args.token or os.getenv('ZENRIN_TOKEN')
    datum = args.datum or os.getenv('ZENRIN_DATUM', 'JGD')
    match_level = args.match_level or os.getenv('ZENRIN_MATCH_LEVEL')

    # Handle SSL verification (command line flag or env var)
    verify_ssl = not args.no_verify_ssl
    if os.getenv('ZENRIN_VERIFY_SSL', '').lower() == 'false':
        verify_ssl = False

    # Validate required parameters
    if not domain:
        parser.error("--domain is required (or set ZENRIN_API_DOMAIN in .env)")
    if not api_key:
        parser.error("--key is required (or set ZENRIN_API_KEY in .env)")

    # Validate authentication parameters
    if auth_method == 'referer' and not referer:
        parser.error("--referer is required when using referer authentication (or set ZENRIN_REFERER in .env)")
    if auth_method == 'bearer' and not token:
        parser.error("--token is required when using bearer authentication (or set ZENRIN_TOKEN in .env)")

    geocoder = ZenrinGeocoder(
        api_domain=domain,
        api_key=api_key,
        auth_method=auth_method,
        referer=referer,
        token=token,
        verify_ssl=verify_ssl
    )

    # Interactive mode
    if args.interactive:
        print("インタラクティブモード (終了するには 'quit' または 'exit' を入力)")
        print("-" * 60)
        while True:
            try:
                address = input("\n住所を入力してください: ").strip()
                if address.lower() in ['quit', 'exit', 'q']:
                    break
                if not address:
                    continue

                result = geocoder.geocode(address, datum=datum,
                                         match_level=match_level)
                print(format_result(result))
            except KeyboardInterrupt:
                print("\n終了します")
                break
            except Exception as e:
                print(f"エラー: {e}")

    # Single address mode
    elif args.address:
        result = geocoder.geocode(args.address, datum=datum,
                                 match_level=match_level)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"結果を {args.output} に保存しました")
        else:
            print(format_result(result))

    # Batch mode
    elif args.batch:
        try:
            with open(args.batch, 'r', encoding='utf-8') as f:
                addresses = [line.strip() for line in f if line.strip()]

            print(f"{len(addresses)} 件の住所を処理中...")

            results = geocoder.geocode_batch(addresses, datum=datum,
                                            match_level=match_level)

            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"結果を {args.output} に保存しました")
            else:
                if isinstance(results, list):
                    for result in results:
                        print(format_result(result))
                else:
                    print(format_result(results))

        except FileNotFoundError:
            print(f"エラー: ファイル '{args.batch}' が見つかりません")
            sys.exit(1)
        except Exception as e:
            print(f"エラー: {e}")
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
