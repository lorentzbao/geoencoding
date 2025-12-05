# Japanese Address Geocoding

Japanese address geocoding program using ZENRIN Maps API. Converts Japanese addresses to coordinates (経度/緯度).

## Features

- Single address geocoding
- Batch geocoding (up to 100 addresses)
- Interactive mode
- JSON output support
- Multiple authentication methods (IP, Referer, OAuth 2.0)
- Proxy support (HTTP/HTTPS)
- SSL certificate verification (can be disabled for corporate environments)
- Returns coordinates (経度, 緯度), match level, and other address information
- Environment variable configuration via `.env` file

## Quick Start

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` with your API credentials**:
   ```bash
   ZENRIN_API_DOMAIN=web.zmaps-api.com
   ZENRIN_API_KEY=your_api_key_here
   ZENRIN_AUTH_METHOD=ip
   ```

4. **Run**:
   ```bash
   # Single address
   uv run python geocoding.py --address "東京都千代田区淡路町2-101"

   # Interactive mode
   uv run python geocoding.py --interactive
   ```

## Installation

Using `uv`:

```bash
uv sync
```

Or install dependencies manually:

```bash
uv pip install requests python-dotenv
```

## Configuration

### Using .env File (Recommended)

Create a `.env` file in the project root directory to store your API credentials:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# API Configuration (required)
# Production: web.zmaps-api.com | Testing: test-web.zmaps-api.com
ZENRIN_API_DOMAIN=web.zmaps-api.com
ZENRIN_API_KEY=your_api_key_here

# Authentication Method (default: ip)
ZENRIN_AUTH_METHOD=ip

# Optional: Referer URL (required only for referer auth)
# ZENRIN_REFERER=https://example.com

# Optional: OAuth 2.0 Token (required only for bearer auth)
# ZENRIN_TOKEN=your_oauth_token_here

# Proxy Configuration (optional)
# http_proxy=http://proxy.example.com:8080
# https_proxy=http://proxy.example.com:8080

# SSL Verification (optional)
# Set to false to disable SSL certificate verification (not recommended for production)
# ZENRIN_VERIFY_SSL=false

# Optional Settings
ZENRIN_DATUM=JGD
# ZENRIN_MATCH_LEVEL=TBN
```

With a `.env` file configured, you can run the program with simplified commands:

```bash
# Simple usage - credentials loaded from .env
uv run python geocoding.py --address "東京都千代田区淡路町2-101"

# Interactive mode
uv run python geocoding.py --interactive

# Batch processing
uv run python geocoding.py --batch addresses.txt --output results.json
```

**Note**: Command-line arguments override `.env` settings.

## Authentication

The ZENRIN Maps API requires authentication via headers. The API key is sent through the `x-api-key` header, and supports three authentication methods.

**Important**: Before using the API, you must configure your authentication method in the ZENRIN console under "Channel Settings" > "Channel List" > "Channel Details".

### 1. IP Address Restriction (Default)

Authenticates requests based on IP address. Configure allowed IPs in the ZENRIN console settings.

**Headers sent:**
- `x-api-key: YOUR_API_KEY`
- `Authorization: ip`

```bash
uv run python geocoding.py --domain web.zmaps-api.com --key YOUR_API_KEY --auth-method ip --address "東京都千代田区淡路町2-101"
```

### 2. Referer Restriction

Authenticates requests based on the Referer header. Configure allowed referrers in the ZENRIN console settings.

**Headers sent:**
- `x-api-key: YOUR_API_KEY`
- `Authorization: referer`
- `Referer: https://example.com`

```bash
uv run python geocoding.py --domain web.zmaps-api.com --key YOUR_API_KEY --auth-method referer --referer "https://example.com" --address "東京都千代田区淡路町2-101"
```

### 3. OAuth 2.0

Authenticates using OAuth 2.0 bearer token. Configure OAuth 2.0 in the ZENRIN console settings.

**Headers sent:**
- `x-api-key: YOUR_API_KEY`
- `Authorization: Bearer YOUR_OAUTH_TOKEN`

```bash
uv run python geocoding.py --domain web.zmaps-api.com --key YOUR_API_KEY --auth-method bearer --token YOUR_OAUTH_TOKEN --address "東京都千代田区淡路町2-101"
```

## Proxy Configuration

If you need to use an HTTP or HTTPS proxy, you can configure it in your `.env` file:

```bash
# Proxy Configuration
http_proxy=http://proxy.example.com:8080
https_proxy=http://proxy.example.com:8080
```

The program reads the `http_proxy` and `https_proxy` environment variables via `os.environ['http_proxy']` and `os.environ['https_proxy']`, and automatically applies them to all API requests.

**Supported proxy formats:**
- `http://proxy.example.com:8080`
- `http://username:password@proxy.example.com:8080`
- `https://proxy.example.com:8443`

**Note**: Both HTTP and HTTPS APIs typically use the `http://` proxy protocol, even for HTTPS traffic. Check your proxy server documentation for the correct configuration.

## SSL Certificate Verification

By default, the program verifies SSL certificates. If you encounter SSL certificate errors (common in corporate environments with proxy servers or self-signed certificates), you can disable SSL verification:

### Option 1: Using `.env` file

```bash
# Disable SSL verification
ZENRIN_VERIFY_SSL=false
```

### Option 2: Using command line

```bash
python geocoding.py --no-verify-ssl --address "東京都千代田区淡路町2-101"
```

**⚠️ Security Warning**: Disabling SSL verification is not recommended for production environments as it makes your connection vulnerable to man-in-the-middle attacks. Only use this option if:
- You're in a development/testing environment
- You're behind a corporate proxy with SSL inspection
- You understand the security implications

**Better alternatives:**
1. Install your corporate proxy's CA certificate on your system
2. Use Python's `certifi` package and update your certificate bundle
3. Contact your IT department to obtain the proper certificates

## Usage

### Interactive Mode

```bash
uv run python geocoding.py --domain web.zmaps-api.com --key YOUR_API_KEY --interactive
```

### Single Address

```bash
uv run python geocoding.py --domain web.zmaps-api.com --key YOUR_API_KEY --address "東京都千代田区淡路町2-101"
```

### Batch Processing

Create a text file with addresses (one per line):

```bash
# addresses.txt
東京都千代田区淡路町2-101
大阪府大阪市北区梅田1-1
```

Run batch geocoding:

```bash
uv run python geocoding.py --domain web.zmaps-api.com --key YOUR_API_KEY --batch addresses.txt
```

### Save Results to JSON

```bash
uv run python geocoding.py --domain web.zmaps-api.com --key YOUR_API_KEY --address "東京都千代田区淡路町2-101" --output result.json
```

## Command Line Options

All options can be set via command-line arguments or in the `.env` file. Command-line arguments take precedence over `.env` settings.

- `--domain`: API domain (required, e.g., `web.zmaps-api.com`)
  - **Env**: `ZENRIN_API_DOMAIN`
  - Production: `web.zmaps-api.com` | Testing: `test-web.zmaps-api.com`
- `--key`: API key (required, sent via `x-api-key` header)
  - **Env**: `ZENRIN_API_KEY`
- `--auth-method`: Authentication method - `ip` (default), `referer`, or `bearer`
  - **Env**: `ZENRIN_AUTH_METHOD`
- `--referer`: Referer URL (required when using `referer` auth)
  - **Env**: `ZENRIN_REFERER`
- `--token`: OAuth 2.0 token (required when using `bearer` auth)
  - **Env**: `ZENRIN_TOKEN`
- `--address`: Single address to geocode
- `--batch`: File containing addresses (one per line)
- `--output`: Output file for JSON results
- `--interactive`: Interactive mode
- `--datum`: Geodetic system (JGD, TOKYO, TOKYO_NAVI) - default: JGD
  - **Env**: `ZENRIN_DATUM`
- `--match-level`: Minimum matching hierarchy (TOD/SHK/OAZ/AZC/GIK/TBN)
  - **Env**: `ZENRIN_MATCH_LEVEL`
- `--no-verify-ssl`: Disable SSL certificate verification (not recommended)
  - **Env**: `ZENRIN_VERIFY_SSL=false`

## Output Format

The program outputs:

- **住所**: Normalized address
- **経度**: Longitude
- **緯度**: Latitude
- **マッチレベル**: Match level (NOM through TBN1)
- **郵便番号**: Postal code
- **都道府県**: Prefecture
- **市区町村**: Municipality
- **ZID**: Building identification data

## Example Output

```
============================================================
住所: 東京都千代田区淡路町2丁目101
経度: 139.767126193576
緯度: 35.6975523546007
マッチレベル: TBN1
郵便番号: 101-0063
都道府県: 東京都
市区町村: 千代田区
============================================================
```

## Match Levels

- **TOD**: Prefecture level (都道府県)
- **SHK**: Municipality level (市区町村)
- **OAZ**: District level (大字・丁目)
- **AZC**: Block level (小字)
- **GIK**: Street level (街区)
- **TBN**: Lot number level (地番)
- **TBN1**: Most precise match

## Requirements

- Python 3.8+
- requests library

## License

MIT
