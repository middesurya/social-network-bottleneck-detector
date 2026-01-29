import { useState } from 'react';
import { Search, Loader2, Sparkles } from 'lucide-react';

interface NaturalLanguageInputProps {
  onSubmit: (query: string) => void;
  isLoading?: boolean;
  placeholder?: string;
  suggestions?: string[];
}

export function NaturalLanguageInput({
  onSubmit,
  isLoading = false,
  placeholder = "Ask a question about the network...",
  suggestions = [
    "Who are the most influential users?",
    "Show me the top bottlenecks",
    "Which users bridge multiple communities?",
    "What is the largest community?",
  ],
}: NaturalLanguageInputProps) {
  const [query, setQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSubmit(query.trim());
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    setShowSuggestions(false);
    onSubmit(suggestion);
  };

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            {isLoading ? (
              <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
            ) : (
              <Sparkles className="w-5 h-5 text-slate-400" />
            )}
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            placeholder={placeholder}
            disabled={isLoading}
            className="w-full pl-12 pr-12 py-4 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!query.trim() || isLoading}
            className="absolute inset-y-0 right-0 pr-4 flex items-center"
          >
            <div
              className={`p-1.5 rounded-lg transition-colors ${
                query.trim() && !isLoading
                  ? 'bg-blue-600 hover:bg-blue-500'
                  : 'bg-slate-700'
              }`}
            >
              <Search className="w-4 h-4 text-white" />
            </div>
          </button>
        </div>

        {/* Suggestions dropdown */}
        {showSuggestions && suggestions.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-slate-800 border border-slate-700 rounded-xl overflow-hidden shadow-xl z-10">
            <div className="px-4 py-2 border-b border-slate-700">
              <span className="text-xs text-slate-400">Suggested queries</span>
            </div>
            <ul>
              {suggestions.map((suggestion, index) => (
                <li key={index}>
                  <button
                    type="button"
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="w-full px-4 py-3 text-left text-slate-300 hover:bg-slate-700 transition-colors flex items-center gap-3"
                  >
                    <Search className="w-4 h-4 text-slate-500" />
                    <span>{suggestion}</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </form>
    </div>
  );
}
