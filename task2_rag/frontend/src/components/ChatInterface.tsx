import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { queryDataset } from '../services/api';
import type { ChatMessage, FilterParams } from '../types';
import ResultCard from './ResultCard';
import ExampleQueries from './ExampleQueries';

interface Props {
  filters: FilterParams;
}

export default function ChatInterface({ filters }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const mutation = useMutation({
    mutationFn: queryDataset,
    onSuccess: (data) => {
      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        queryAnalysis: data.query_analysis,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMsg]);
    },
    onError: (error: Error) => {
      const errorMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `Error: ${error.message}. Please check that the backend is running.`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMsg]);
    },
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (query: string) => {
    if (!query.trim() || mutation.isPending) return;

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: query.trim(),
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');

    mutation.mutate({
      query: query.trim(),
      filters: Object.keys(filters).length > 0 ? filters : undefined,
    });
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <h2 className="text-lg font-semibold text-gray-700 mb-2">
              Ask anything about family offices
            </h2>
            <p className="text-sm text-gray-500 mb-6">
              Query 200 family offices across 45 intelligence fields using natural language
            </p>
            <ExampleQueries onSelect={handleSubmit} disabled={mutation.isPending} />
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] ${
              msg.role === 'user'
                ? 'bg-blue-600 text-white rounded-2xl rounded-br-md px-4 py-2'
                : 'bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3'
            }`}>
              <div className={`text-sm whitespace-pre-wrap ${msg.role === 'user' ? '' : 'text-gray-800'}`}>
                {msg.content}
              </div>

              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 space-y-2">
                  <p className="text-xs font-medium text-gray-500">
                    Sources ({msg.sources.length} matches):
                  </p>
                  {msg.sources.map((source, i) => (
                    <ResultCard key={`${msg.id}-${i}`} result={source} index={i} />
                  ))}
                </div>
              )}

              {msg.queryAnalysis && (
                <div className="mt-2 text-xs text-gray-400">
                  {msg.queryAnalysis.extracted_filters && Object.keys(msg.queryAnalysis.extracted_filters).length > 0 && (
                    <span>Filters: {JSON.stringify(msg.queryAnalysis.extracted_filters)}</span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {mutation.isPending && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3">
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <div className="animate-spin h-4 w-4 border-2 border-blue-500 [border-top-color:transparent] rounded-full" />
                Analyzing query and retrieving results...
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-gray-200 p-4 bg-white">
        {messages.length > 0 && (
          <div className="mb-3">
            <ExampleQueries onSelect={handleSubmit} disabled={mutation.isPending} />
          </div>
        )}
        <form
          onSubmit={(e) => { e.preventDefault(); handleSubmit(input); }}
          className="flex gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about family offices... e.g. 'Which FOs in Asia focus on AI?'"
            disabled={mutation.isPending}
            className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                       disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || mutation.isPending}
            className="px-5 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium
                       hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed
                       transition-colors"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
