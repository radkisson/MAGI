# Python Support in n8n Workflows

RIN's n8n instance includes **full Python 3.12 support** via the `hank033/n8n-python` Docker image. This guide provides examples and best practices for using Python in your workflows.

## ⚠️ Security & Maintenance Considerations

**Docker Image Source**: This feature uses a community-maintained Docker image (`hank033/n8n-python:latest`):
- The image is built on top of the official n8n image with Python 3.12 added
- Community images may not receive security updates as quickly as official images
- For production deployments with strict security requirements, consider:
  - Building a custom Docker image from the official `n8nio/n8n` base
  - Pinning to a specific version digest instead of using the `latest` tag
  - Regularly reviewing and updating the base image

**Package Persistence**: Python packages installed via `pip install`:
- Are available in the current container session
- **May not persist** across container restarts
- For production, implement one of these strategies:
  - Create a startup workflow that automatically reinstalls required packages
  - Build a custom Docker image with pre-installed packages
  - Configure Docker volumes to persist Python's site-packages directory

## Overview

The Python-enabled n8n image allows you to:
- Write Python code directly in Code nodes alongside JavaScript
- Use Python's extensive standard library
- Install and use external Python packages
- Process data with Python's powerful data manipulation capabilities
- Leverage Python for machine learning, data science, and scientific computing

## Using Python in Code Nodes

### Basic Example

When creating a Code node in n8n:

1. Add a **Code** node to your workflow
2. Select **Python** as the language from the dropdown
3. Write your Python code

```python
# Access input items from the previous node
items = _input.all()

# Process each item
results = []
for item in items:
    data = item['json']
    
    # Your Python logic here
    processed = {
        'original_text': data.get('text', ''),
        'uppercase': str(data.get('text', '')).upper(),
        'word_count': len(str(data.get('text', '')).split()),
        'char_count': len(str(data.get('text', '')))
    }
    
    results.append({'json': processed})

# Return processed items
return results
```

### Data Transformation Example

```python
import json
from datetime import datetime

items = _input.all()
results = []

for item in items:
    data = item['json']
    
    # Complex data transformation
    transformed = {
        'timestamp': datetime.now().isoformat(),
        'processed_data': {
            'title': data.get('title', '').title(),
            'summary': data.get('description', '')[:200],
            'tags': [tag.strip().lower() for tag in data.get('tags', '').split(',')],
            'metrics': {
                'length': len(data.get('description', '')),
                'has_url': 'http' in data.get('description', '').lower()
            }
        }
    }
    
    results.append({'json': transformed})

return results
```

### Text Analysis Example

```python
import re
from collections import Counter

items = _input.all()
results = []

for item in items:
    text = item['json'].get('text', '')
    
    # Text analysis
    words = re.findall(r'\b\w+\b', text.lower())
    word_freq = Counter(words)
    
    analysis = {
        'text': text,
        'total_words': len(words),
        'unique_words': len(set(words)),
        'most_common': word_freq.most_common(10),
        'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
        'contains_urls': bool(re.search(r'https?://', text))
    }
    
    results.append({'json': analysis})

return results
```

## Installing Python Packages

To use external Python packages in your workflows:

**⚠️ Important**: Packages installed via `pip` are stored in the container and may not persist across container restarts. For production use:
- Use Method 2 (startup workflow) to automatically reinstall packages on container restart
- Build a custom Docker image with pre-installed packages
- Configure Docker volumes for Python's site-packages directory

### Method 1: Execute Command Node

1. Add an **Execute Command** node before your Python Code node
2. Set the command to install packages:
   ```bash
   pip install requests pandas numpy scikit-learn
   ```
3. The packages will be available to all subsequent Python Code nodes in the current container session

### Method 2: Startup Installation (Recommended for Production)

For packages you always need, create a workflow that runs on startup to ensure packages are available after restarts:

1. Create a workflow with a **Schedule Trigger** set to run once on startup
2. Add an **Execute Command** node to install packages:
   ```bash
   pip install -q requests beautifulsoup4 pandas
   ```
3. This ensures packages are automatically reinstalled whenever the container restarts

### Example with External Packages

Once packages are installed, use them in your Code nodes:

```python
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse

items = _input.all()
results = []

for item in items:
    url = item['json'].get('url', '')
    
    # Validate URL
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            results.append({'json': {'url': url, 'error': 'Invalid URL scheme. Only http and https are allowed.'}})
            continue
    except Exception as e:
        results.append({'json': {'url': url, 'error': f'Invalid URL: {str(e)}'}})
        continue
    
    try:
        # Fetch and parse HTML with security best practices
        headers = {
            'User-Agent': 'n8n-workflow/1.0 (RIN Automation)'
        }
        response = requests.get(
            url, 
            timeout=10, 
            verify=True,  # Verify SSL certificates
            headers=headers
        )
        response.raise_for_status()  # Raise exception for bad status codes
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract data
        extracted = {
            'url': url,
            'title': soup.find('title').text if soup.find('title') else '',
            'headings': [h.text for h in soup.find_all(['h1', 'h2'])[:5]],
            'links': len(soup.find_all('a')),
            'status_code': response.status_code
        }
        
        results.append({'json': extracted})
    except requests.exceptions.SSLError as e:
        results.append({'json': {'url': url, 'error': f'SSL verification failed: {str(e)}'}})
    except requests.exceptions.RequestException as e:
        results.append({'json': {'url': url, 'error': f'Request failed: {str(e)}'}})
    except Exception as e:
        results.append({'json': {'url': url, 'error': str(e)}})

return results
```

## Data Science Example with Pandas

```python
import pandas as pd
from datetime import datetime

items = _input.all()

# Convert items to pandas DataFrame
data = [item['json'] for item in items]
df = pd.DataFrame(data)

# Data analysis
stats = {
    'summary': {
        'total_records': len(df),
        'columns': list(df.columns),
        'missing_values': df.isnull().sum().to_dict()
    },
    'analysis': {}
}

# Numeric analysis
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
for col in numeric_cols:
    stats['analysis'][col] = {
        'mean': float(df[col].mean()),
        'median': float(df[col].median()),
        'std': float(df[col].std()),
        'min': float(df[col].min()),
        'max': float(df[col].max())
    }

# Return single result with statistics
return [{'json': stats}]
```

## API Integration Example

```python
import requests
import json
import os

items = _input.all()
results = []

for item in items:
    query = item['json'].get('query', '')
    
    # Call an external API
    try:
        # SECURITY: Use environment variables for API keys
        # Set these in n8n: Settings → Environments → Variables
        api_key = os.environ.get('API_KEY')
        if not api_key:
            raise ValueError('API_KEY environment variable not set')
        
        response = requests.post(
            'https://api.example.com/v1/process',
            json={'query': query, 'mode': 'advanced'},
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=30,
            verify=True  # Verify SSL certificates
        )
        response.raise_for_status()  # Raise exception for bad status codes
        
        api_result = response.json()
        
        processed = {
            'query': query,
            'result': api_result.get('data', {}),
            'success': response.status_code == 200,
            'timestamp': response.headers.get('Date', '')
        }
        
        results.append({'json': processed})
        
    except ValueError as e:
        results.append({'json': {'query': query, 'error': str(e), 'success': False}})
    except requests.exceptions.RequestException as e:
        results.append({'json': {'query': query, 'error': f'Request failed: {str(e)}', 'success': False}})
    except Exception as e:
        results.append({'json': {'query': query, 'error': str(e), 'success': False}})

return results
```

**Note**: Store API keys securely using n8n environment variables or credentials, never hardcode them in workflows.

## Error Handling Best Practices

Always include proper error handling in your Python code:

```python
import traceback

# Define helper functions before the main code
def perform_complex_operation(data):
    """Your custom operation logic here"""
    # Example: validate and transform data
    if not data:
        raise ValueError("Data cannot be empty")
    return data

# Main processing code
items = _input.all()
results = []

for item in items:
    try:
        data = item['json']
        
        # Your risky operation here
        result = perform_complex_operation(data)
        
        results.append({
            'json': {
                'success': True,
                'result': result,
                'input': data
            }
        })
        
    except ValueError as e:
        results.append({
            'json': {
                'success': False,
                'error': f'Value Error: {str(e)}',
                'input': item['json']
            }
        })
    except Exception as e:
        results.append({
            'json': {
                'success': False,
                'error': f'Unexpected Error: {str(e)}',
                'traceback': traceback.format_exc(),
                'input': item['json']
            }
        })

return results
```

## Python vs JavaScript: When to Use Each

### Use Python When:
- Processing large datasets (pandas, numpy)
- Performing statistical analysis or machine learning
- Complex mathematical operations
- Working with scientific libraries
- Text processing with advanced NLP
- Data science workflows

### Use JavaScript When:
- Simple JSON manipulation
- Working with n8n's native operations
- Quick data transformations
- Interacting with n8n's built-in functions
- When performance is critical for simple operations

## Tips and Best Practices

1. **Import at the Top**: Always import libraries at the beginning of your code
2. **Handle Errors**: Always include try/except blocks for robust workflows
3. **Return Proper Format**: Always return a list of dictionaries with 'json' key
4. **Test Incrementally**: Test your Python code with small datasets first
5. **Document Your Code**: Add comments to explain complex logic
6. **Check Package Availability**: Verify packages are installed before using them
7. **Use Virtual Environments**: The n8n-python image handles this automatically

## Accessing Input Data

The input data from previous nodes is available via `_input`:

```python
# Get all items
items = _input.all()

# Get first item
first_item = _input.first()

# Iterate through items
for item in items:
    data = item['json']  # Access the JSON data
    # Process data...
```

## Available Python Version

- **Python Version**: 3.12.12
- **Standard Library**: Full Python 3.12 standard library available
- **Package Manager**: pip (use Execute Command node to install packages)

## Common Packages for Workflows

These packages are commonly useful in n8n workflows:

- **requests**: HTTP requests and API calls
- **beautifulsoup4**: HTML parsing and web scraping
- **pandas**: Data analysis and manipulation
- **numpy**: Numerical computing
- **scikit-learn**: Machine learning
- **pillow**: Image processing
- **openpyxl**: Excel file handling
- **python-dateutil**: Date parsing and manipulation
- **jsonschema**: JSON schema validation

Install with:
```bash
pip install requests beautifulsoup4 pandas numpy scikit-learn pillow openpyxl python-dateutil jsonschema
```

## Troubleshooting

### Package Not Found
If you get "ModuleNotFoundError", install the package first:
```bash
pip install <package-name>
```

### Permission Errors
The n8n-python image runs as the `node` user with proper permissions. If you encounter permission issues, check your volume mounts.

### Performance Issues
For heavy computations, consider:
- Processing items in batches
- Using more efficient algorithms
- Caching results when possible
- Moving complex operations to a separate Python service

## Example Workflows

### Data Enrichment Pipeline

1. **Webhook Trigger**: Receive data via webhook
2. **Python Code**: Clean and validate data
3. **Python Code**: Call external APIs for enrichment
4. **Python Code**: Aggregate and analyze results
5. **HTTP Request**: Send processed data to destination

### Text Analysis Workflow

1. **Schedule Trigger**: Run daily at specific time
2. **HTTP Request**: Fetch documents from API
3. **Python Code**: Extract text and perform NLP
4. **Python Code**: Generate summaries and insights
5. **Email**: Send analysis report

### Data Science Pipeline

1. **Database**: Fetch data from database
2. **Python Code**: Load into pandas DataFrame
3. **Python Code**: Clean and transform data
4. **Python Code**: Perform statistical analysis
5. **Python Code**: Generate visualizations (as JSON)
6. **HTTP Request**: Upload results to dashboard

## Additional Resources

- [n8n Documentation](https://docs.n8n.io/)
- [Python 3.12 Documentation](https://docs.python.org/3.12/)
- [hank033/n8n-python Docker Image](https://hub.docker.com/r/hank033/n8n-python)
- RIN Workflows: See other workflow examples in this directory

## Support

If you encounter issues with Python support:
1. Check that you're using the correct Python syntax for version 3.12
2. Verify packages are installed using Execute Command node
3. Review error messages in the n8n execution logs
4. Test your Python code outside n8n first if possible

For RIN-specific issues, see the main README or open an issue on GitHub.
