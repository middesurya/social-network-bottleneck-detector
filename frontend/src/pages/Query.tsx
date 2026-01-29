import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { MessageSquare, Code, Lightbulb, AlertCircle } from 'lucide-react';
import { NaturalLanguageInput } from '../components/NaturalLanguageInput';
import { nlqApi } from '../services/api';
import type { NLQResponse } from '../types';

export function Query() {
  const [results, setResults] = useState<NLQResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { data: examples } = useQuery({
    queryKey: ['nlqExamples'],
    queryFn: nlqApi.getExamples,
  });

  const queryMutation = useMutation({
    mutationFn: (query: string) => nlqApi.query(query),
    onSuccess: (data) => {
      setResults(data);
      setError(null);
    },
    onError: (err: Error) => {
      setError(err.message);
      setResults(null);
    },
  });

  const handleQuery = (query: string) => {
    queryMutation.mutate(query);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <MessageSquare className="w-8 h-8 text-blue-500" />
          <h1 className="text-3xl font-bold text-white">Natural Language Query</h1>
        </div>
        <p className="text-slate-400">
          Ask questions about your network in plain English. The system will convert your
          question to a Cypher query and return the results.
        </p>
      </div>

      {/* Input */}
      <div className="mb-8">
        <NaturalLanguageInput
          onSubmit={handleQuery}
          isLoading={queryMutation.isPending}
          suggestions={examples?.examples?.map((e: { query: string }) => e.query) || []}
        />
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 bg-red-500/10 border border-red-500/30 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-red-400 font-medium">Query Failed</p>
              <p className="text-red-300/70 text-sm mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {results && (
        <div className="space-y-6">
          {/* Query Info */}
          <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
            <div className="px-4 py-3 border-b border-slate-700 flex items-center justify-between">
              <span className="text-sm font-medium text-slate-400">Query Details</span>
              {results.confidence && (
                <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">
                  {(results.confidence * 100).toFixed(0)}% confidence
                </span>
              )}
            </div>
            <div className="p-4 space-y-4">
              <div>
                <p className="text-xs text-slate-500 mb-1">Your Question</p>
                <p className="text-white">{results.query}</p>
              </div>
              {results.explanation && (
                <div>
                  <p className="text-xs text-slate-500 mb-1">Interpretation</p>
                  <p className="text-slate-300">{results.explanation}</p>
                </div>
              )}
            </div>
          </div>

          {/* Generated Cypher */}
          <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
            <div className="px-4 py-3 border-b border-slate-700 flex items-center gap-2">
              <Code className="w-4 h-4 text-slate-400" />
              <span className="text-sm font-medium text-slate-400">Generated Cypher</span>
            </div>
            <pre className="p-4 overflow-x-auto">
              <code className="text-sm text-green-400 font-mono">{results.generated_cypher}</code>
            </pre>
          </div>

          {/* Results Table */}
          <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
            <div className="px-4 py-3 border-b border-slate-700 flex items-center justify-between">
              <span className="text-sm font-medium text-slate-400">Results</span>
              <span className="text-xs text-slate-500">{results.results.length} rows</span>
            </div>
            {results.results.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-700">
                      {Object.keys(results.results[0]).map((key) => (
                        <th
                          key={key}
                          className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider"
                        >
                          {key}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700">
                    {results.results.slice(0, 50).map((row, i) => (
                      <tr key={i} className="hover:bg-slate-700/50">
                        {Object.values(row).map((value, j) => (
                          <td key={j} className="px-4 py-3 text-slate-300">
                            {typeof value === 'object'
                              ? JSON.stringify(value, null, 2)
                              : String(value)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
                {results.results.length > 50 && (
                  <div className="px-4 py-3 text-center text-sm text-slate-500 border-t border-slate-700">
                    Showing first 50 of {results.results.length} results
                  </div>
                )}
              </div>
            ) : (
              <div className="p-8 text-center text-slate-400">No results found</div>
            )}
          </div>
        </div>
      )}

      {/* Examples */}
      {!results && !error && (
        <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Lightbulb className="w-5 h-5 text-yellow-500" />
            <h3 className="font-semibold text-white">Example Questions</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {examples?.examples?.map(
              (example: { query: string; description: string }, index: number) => (
                <button
                  key={index}
                  onClick={() => handleQuery(example.query)}
                  className="text-left p-4 bg-slate-700/50 rounded-lg hover:bg-slate-700 transition-colors group"
                >
                  <p className="text-white group-hover:text-blue-400 transition-colors">
                    {example.query}
                  </p>
                  <p className="text-sm text-slate-500 mt-1">{example.description}</p>
                </button>
              )
            ) || (
              <>
                <div className="p-4 bg-slate-700/50 rounded-lg">
                  <p className="text-white">Who are the most influential users?</p>
                  <p className="text-sm text-slate-500 mt-1">Find users with highest PageRank</p>
                </div>
                <div className="p-4 bg-slate-700/50 rounded-lg">
                  <p className="text-white">Show me the top bottlenecks</p>
                  <p className="text-sm text-slate-500 mt-1">Find critical network nodes</p>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
