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
  const bottomRef = useRef<HTMLDivElement>(null);

  const mutation = useMutation({
    mutationFn: queryDataset,
    onSuccess: (data) => {
      setMessages(prev => [...prev, {
        id: crypto.randomUUID(), role: 'assistant',
        content: data.answer, sources: data.sources,
        queryAnalysis: data.query_analysis, timestamp: new Date(),
      }]);
    },
    onError: (error: Error) => {
      setMessages(prev => [...prev, {
        id: crypto.randomUUID(), role: 'assistant',
        content: `Something went wrong: ${error.message}`, timestamp: new Date(),
      }]);
    },
  });

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const submit = (query: string) => {
    if (!query.trim() || mutation.isPending) return;
    setMessages(prev => [...prev, {
      id: crypto.randomUUID(), role: 'user', content: query.trim(), timestamp: new Date(),
    }]);
    setInput('');
    mutation.mutate({
      query: query.trim(),
      filters: Object.keys(filters).length > 0 ? filters : undefined,
    });
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-5">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full gap-4 -mt-8">
            <div className="text-center">
              <h2 className="text-base font-semibold mb-1 empty-title">What would you like to know?</h2>
              <p className="text-xs max-w-md empty-sub">
                Ask in plain English. The system searches 200 family offices across 45 fields,
                then synthesizes an answer from the most relevant matches.
              </p>
            </div>
            <ExampleQueries onSelect={submit} disabled={mutation.isPending} />
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] ${
              msg.role === 'user'
                ? 'rounded-2xl rounded-br-sm px-4 py-2.5 msg-user'
                : 'rounded-2xl rounded-bl-sm px-4 py-3 msg-bot'
            }`}>
              <div className="text-[13px] leading-relaxed whitespace-pre-wrap">
                {msg.content}
              </div>

              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 space-y-1.5">
                  <p className="text-[11px] font-medium uppercase tracking-wider msg-meta">
                    {msg.sources.length} sources
                  </p>
                  {msg.sources.map((source, i) => (
                    <ResultCard key={`${msg.id}-${i}`} result={source} index={i} />
                  ))}
                </div>
              )}

              {msg.queryAnalysis?.extracted_filters &&
                Object.keys(msg.queryAnalysis.extracted_filters).length > 0 && (
                <p className="mt-2 text-[10px] msg-meta">
                  Filters: {Object.entries(msg.queryAnalysis.extracted_filters)
                    .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
                    .join(' | ')}
                </p>
              )}
            </div>
          </div>
        ))}

        {mutation.isPending && (
          <div className="flex justify-start">
            <div className="rounded-2xl rounded-bl-sm px-4 py-3 msg-bot">
              <div className="flex items-center gap-2 text-xs">
                <span className="inline-block w-1.5 h-1.5 rounded-full animate-pulse loading-dot" />
                <span className="inline-block w-1.5 h-1.5 rounded-full animate-pulse loading-dot [animation-delay:150ms]" />
                <span className="inline-block w-1.5 h-1.5 rounded-full animate-pulse loading-dot [animation-delay:300ms]" />
                <span className="ml-1 loading-text">Searching...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t px-6 py-4 surface">
        {messages.length > 0 && (
          <div className="mb-3">
            <ExampleQueries onSelect={submit} disabled={mutation.isPending} />
          </div>
        )}
        <form onSubmit={(e) => { e.preventDefault(); submit(input); }} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about family offices..."
            disabled={mutation.isPending}
            className="flex-1 px-4 py-2.5 rounded-lg text-sm disabled:opacity-40 input-box"
          />
          <button
            type="submit"
            disabled={!input.trim() || mutation.isPending}
            className="px-5 py-2.5 rounded-lg text-sm font-medium transition-colors btn-send"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
