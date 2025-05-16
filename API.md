# Finance News API Documentation

## Overview
The Finance News API provides comprehensive financial news and market data aggregation with sentiment analysis. This API requires authentication using API keys.

## Base URL
```
http://localhost:8000
```

## Authentication
All endpoints require API key authentication. Include your API key in the `X-API-Key` header with every request.

Example:
```python
import requests

headers = {
    "X-API-Key": "your_api_key_here"
}

response = requests.get("http://localhost:8000/api/news/AAPL", headers=headers)
```

## News Endpoints

### GET /api/news/{ticker}
Get news and analysis for a specific stock ticker.

#### Parameters
- ticker (path): Stock symbol (e.g., AAPL, MSFT)
- include_company_info (query): Include detailed company information (default: true)
- sentiment_threshold (query): Filter by minimum sentiment score (-1 to 1)
- time_range_hours (query): Filter news from last N hours
- sources (query): List of news sources to include

#### Example Request
```python
import requests

headers = {
    "X-API-Key": "your_api_key_here"
}

response = requests.get(
    "http://localhost:8000/api/news/AAPL",
    params={
        "sentiment_threshold": 0.2,
        "time_range_hours": 24,
        "sources": ["reuters", "bloomberg"]
    },
    headers=headers
)
```

## Error Handling
The API uses standard HTTP status codes and returns detailed error messages:

- 400: Bad Request - Invalid input parameters
- 401: Unauthorized - Missing API key
- 403: Forbidden - Invalid API key
- 404: Not Found - Resource not found
- 500: Internal Server Error - Server-side error

## Rate Limiting
Currently, there are no rate limits implemented. This will be added in future updates.

## Best Practices
1. Keep your API key secure and never share it
2. Use HTTPS for all API requests
3. Implement proper error handling in your applications
4. Monitor your API usage
5. Contact support if you need a new API key or have issues with existing ones

## Support
For support or to request a new API key, please contact:
- Email: pratyushkhanal95@gmail.com
- GitHub: https://github.com/pratyushkhanal

## Versioning
The API is currently at version 1.0.0. All future updates will maintain backward compatibility.

## License
This API is licensed under the Apache 2.0 License. 