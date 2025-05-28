'use client';

import React, { useState } from 'react';

interface SearchResult {
  count: number;
  query: string;
  results: string[];
}

function Index() {
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [luckyIndex, setLuckyIndex] = useState(0);

  const luckyQueries = [
    'cristina lopes',
    'machine learning', 
    'ACM',
    'master of software engineering'
  ];

  const search = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8080/api/search?query=${encodeURIComponent(query)}`);
      const data = await response.json();
      setSearchResults(data);
      setHasSearched(true);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      search();
    }
  };

  const extractDomain = (url: string) => {
    try {
      return new URL(url).hostname;
    } catch {
      return url;
    }
  };

  const formatTitle = (url: string) => {
    try {
      const urlObj = new URL(url);
      const path = urlObj.pathname;
      
      if (path && path !== '/') {
        const pathSegments = path.split('/').filter(Boolean);
        const lastSegment = pathSegments[pathSegments.length - 1];
        
        if (lastSegment) {
          return lastSegment
            .split('-')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');
        }
      }
      
      return urlObj.hostname;
    } catch {
      return url;
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className={`${hasSearched ? 'border-b border-gray-200' : ''}`}>
        <div className={`max-w-6xl mx-auto px-4 ${hasSearched ? 'py-4' : 'pt-32'}`}>
          {/* Logo/Title */}
          <div className={`text-center ${hasSearched ? 'hidden' : 'mb-8'}`}>
            <h1 className="text-8xl font-semibold text-gray-700 mb-8">
              <span className="text-blue-500">O</span>
              <span className="text-red-500">o</span>
              <span className="text-yellow-500">g</span>
              <span className="text-blue-500">l</span>
              <span className="text-green-500">e</span>
              <span className="text-red-500">g</span>
            </h1>
          </div>

          {/* Search Bar */}
          <div className={`flex ${hasSearched ? 'items-center' : 'justify-center'} ${hasSearched ? '' : 'mb-8'}`}>
            {hasSearched && (
              <button
                onClick={() => {
                  setHasSearched(false);
                  setSearchResults(null);
                  setQuery('');
                }}
                className="text-5xl font-semibold text-blue-500 hover:text-blue-600 transition-colors duration-200 mr-6 absolute left-6"
              >
                O
              </button>
            )}
            <div className="relative w-full max-w-3xl">
              <div className="flex items-center border border-gray-300 rounded-full hover:shadow-md focus-within:shadow-md transition-shadow duration-200">
                <div className="pl-4 pr-2">
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <input
                  className="flex-1 py-3 px-2 text-lg outline-none"
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Search the web..."
                  autoComplete="off"
                />
                {query && (
                  <button
                    onClick={() => setQuery('')}
                    className="p-2 hover:bg-gray-100 rounded-full mr-2"
                  >
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                )}
              </div>
              
              {!hasSearched && (
                <div className="flex justify-center mt-8 space-x-4">
                  <button
                    className="bg-gray-50 hover:bg-gray-100 border border-gray-200 text-gray-700 px-6 py-2 rounded text-sm"
                    onClick={search}
                    disabled={loading}
                  >
                    {loading ? 'Searching...' : 'Search'}
                  </button>
                  <button
                    className="bg-gray-50 hover:bg-gray-100 border border-gray-200 text-gray-700 px-6 py-2 rounded text-sm"
                    onClick={() => {
                      setQuery(luckyQueries[luckyIndex]);
                      setLuckyIndex((luckyIndex + 1) % luckyQueries.length);
                    }}
                  >
                    I'm Feeling Lucky
                  </button>
                </div>
              )}
            </div>
            
            {hasSearched && (
              <button
                className="ml-4 bg-blue-500 hover:bg-blue-600 text-white px-6 py-4 rounded-lg text-sm font-medium font-semibold"
                onClick={search}
                disabled={loading}
              >
                Search
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Results */}
      {hasSearched && (
        <div className="max-w-6xl mx-auto px-4 py-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              <span className="ml-2 text-gray-600">Searching...</span>
            </div>
          ) : searchResults ? (
            <>
              {/* Results count */}
              <div className="text-sm text-gray-600 mb-6">
                About {searchResults.count.toLocaleString()} results for "{searchResults.query}"
              </div>

              {/* Results list */}
              <div className="space-y-6">
                {searchResults.results.map((url, index) => (
                  <div key={index} className="max-w-2xl">
                    <div className="group">
                      {/* URL breadcrumb */}
                      <div className="text-sm text-green-700 mb-1">
                        {extractDomain(url)} › {url.length > 60 ? url.substring(0, 60) + '...' : url}
                      </div>
                      
                      {/* Title */}
                      <h3 className="text-xl text-blue-600 hover:underline cursor-pointer mb-1">
                        <a href={url} target="_blank" rel="noopener noreferrer">
                          {formatTitle(url)}
                        </a>
                      </h3>
                      
                      {/* Description */}
                      <p className="text-sm text-gray-600 leading-relaxed">
                        Relevant content found for your search query. Click to explore more information.
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-600">No results found. Try a different search term.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Index;