#!/usr/bin/env python3
"""
Example usage of the OpenAlex MCP Server tools.

This script demonstrates how to use the OpenAlex MCP tools programmatically.
In practice, these tools would be called through the MCP protocol.
"""

import asyncio
import json
from src.openalex_mcp.client import OpenAlexClient
from src.openalex_mcp.tools import (
    search_works,
    search_authors,
    search_institutions,
    get_work_details,
    get_author_profile,
    get_citations,
)


async def example_search_works():
    """Example: Search for machine learning papers from 2023."""
    print("=== Searching for Machine Learning Works from 2023 ===")
    
    client = OpenAlexClient(email="example@test.com")
    
    arguments = {
        "query": "machine learning",
        "year_from": 2023,
        "sort": "cited_by_count",
        "limit": 5
    }
    
    async with client:
        results = await search_works(client, arguments)
        for result in results:
            print(result.text)
            print("-" * 80)


async def example_search_authors():
    """Example: Search for AI researchers at Stanford."""
    print("\n=== Searching for AI Researchers ===")
    
    client = OpenAlexClient(email="example@test.com")
    
    arguments = {
        "query": "artificial intelligence",
        "institution": "Stanford University",
        "sort": "h_index",
        "limit": 3
    }
    
    async with client:
        results = await search_authors(client, arguments)
        for result in results:
            print(result.text)
            print("-" * 80)


async def example_search_institutions():
    """Example: Search for top computer science institutions."""
    print("\n=== Searching for Computer Science Institutions ===")
    
    client = OpenAlexClient(email="example@test.com")
    
    arguments = {
        "query": "computer science",
        "country": "US",
        "sort": "works_count",
        "limit": 3
    }
    
    async with client:
        results = await search_institutions(client, arguments)
        for result in results:
            print(result.text)
            print("-" * 80)


async def example_get_work_details():
    """Example: Get details for a specific work."""
    print("\n=== Getting Work Details ===")
    
    client = OpenAlexClient(email="example@test.com")
    
    # This is a famous paper - "Attention Is All You Need"
    arguments = {
        "work_id": "W2741809807"
    }
    
    async with client:
        results = await get_work_details(client, arguments)
        for result in results:
            print(result.text)
            print("-" * 80)


async def example_get_citations():
    """Example: Get citations for a specific work."""
    print("\n=== Getting Citations ===")
    
    client = OpenAlexClient(email="example@test.com")
    
    # Get papers that cite "Attention Is All You Need"
    arguments = {
        "work_id": "W2741809807",
        "sort": "cited_by_count",
        "limit": 3
    }
    
    async with client:
        results = await get_citations(client, arguments)
        for result in results:
            print(result.text)
            print("-" * 80)


async def main():
    """Run all examples."""
    examples = [
        example_search_works,
        example_search_authors,
        example_search_institutions,
        example_get_work_details,
        example_get_citations,
    ]
    
    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"Error in {example.__name__}: {e}")
        
        # Small delay between examples
        await asyncio.sleep(1)


if __name__ == "__main__":
    # Set up basic logging
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("OpenAlex MCP Server - Example Usage")
    print("=" * 50)
    print("Note: These examples demonstrate the MCP tools.")
    print("In practice, these would be called through the MCP protocol.\n")
    
    # Run examples
    asyncio.run(main())