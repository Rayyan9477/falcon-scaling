import { useState, useRef, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { queryDatasetStream, getHistory } from '../services/api';
import type { ChatMessage, FilterParams, FamilyOfficeResult, QueryAnalysis } from '../types';
import ResultCard from './ResultCard';
import ExampleQueries from './ExampleQueries';
import QueryHistory from './QueryHistory';

/** Markdown → HTML for LLM responses */
function renderMarkdown(text: string): string {
  // Escape HTML entities first
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Bold: **text**
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong class="text-slate-900 font-semibold">$1</strong>');

  // Process line by line
  const lines = html.split('\n');
  const processed: string[] = [];
  let inList = false;

  for (const line of lines) {
    const trimmed = line.trim();

    // Numbered list: "1. content" or "1) content"
    const numMatch = trimmed.match(/^(\d+)[.)]\s+(.+)/);
    if (numMatch) {
      if (!inList) { processed.push('<div class="mt-3 space-y-2">'); inList = true; }
      processed.push(
        `<div class="flex gap-2 items-start pl-1">` +
        `<span class="text-blue-600 font-bold text-xs mt-0.5 shrink-0">${numMatch[1]}.</span>` +
        `<div class="flex-1">${numMatch[2]}</div>` +
        `</div>`
      );
      continue;
    }

    // Bullet list: "- content" or "• content"
    const bulletMatch = trimmed.match(/^[-•]\s+(.+)/);
    if (bulletMatch) {
      processed.push(
        `<div class="flex gap-2 items-start pl-5">` +
        `<span class="text-blue-400 mt-0.5 shrink-0">&#8226;</span>` +
        `<div class="flex-1 text-slate-600">${bulletMatch[1]}</div>` +
        `</div>`
      );
      continue;
    }

    // Empty line closes list and adds spacing
    if (!trimmed) {
      if (inList) { processed.push('</div>'); inList = false; }
      processed.push('<div class="h-2"></div>');
      continue;
    }

    // Regular paragraph
    if (inList) { processed.push('</div>'); inList = false; }
    processed.push(`<p class="mb-2">${trimmed}</p>`);
  }
  if (inList) processed.push('</div>');

  return processed.join('\n');
}

interface Props {
  filters: FilterParams;
}

export default function ChatInterface({ filters }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Fetch query history
  const { data: history, refetch: refetchHistory } = useQuery({
    queryKey: ['history'],
    queryFn: () => getHistory(50),
    staleTime: 30_000,
  });

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const submit = useCallback(async (query: string) => {
    if (!query.trim() || isStreaming) return;

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(), role: 'user', content: query.trim(), timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsStreaming(true);

    // Create a placeholder assistant message for streaming
    const assistantId = crypto.randomUUID();
    const assistantMsg: ChatMessage = {
      id: assistantId, role: 'assistant', content: '', timestamp: new Date(),
    };
    setMessages(prev => [...prev, assistantMsg]);

    try {
      await queryDatasetStream(
        {
          query: query.trim(),
          filters: Object.keys(filters).length > 0 ? filters : undefined,
        },
        {
          onToken: (token) => {
            setMessages(prev => prev.map(m =>
              m.id === assistantId ? { ...m, content: m.content + token } : m
            ));
          },
          onSources: (sources: FamilyOfficeResult[], _totalMatches: number) => {
            setMessages(prev => prev.map(m =>
              m.id === assistantId ? { ...m, sources } : m
            ));
          },
          onDone: (analysis: QueryAnalysis) => {
            setMessages(prev => prev.map(m =>
              m.id === assistantId ? { ...m, queryAnalysis: analysis } : m
            ));
            refetchHistory();
          },
          onError: (error: string) => {
            setMessages(prev => prev.map(m =>
              m.id === assistantId
                ? { ...m, content: `Something went wrong: ${error}` }
                : m
            ));
          },
        },
      );
    } catch (error) {
      setMessages(prev => prev.map(m =>
        m.id === assistantId
          ? { ...m, content: `Connection error: ${error instanceof Error ? error.message : 'Unknown error'}` }
          : m
      ));
    } finally {
      setIsStreaming(false);
    }
  }, [filters, isStreaming, refetchHistory]);

  const loadFromHistory = useCallback((query: string, answer: string, sources?: FamilyOfficeResult[]) => {
    setMessages(prev => [
      ...prev,
      { id: crypto.randomUUID(), role: 'user', content: query, timestamp: new Date() },
      { id: crypto.randomUUID(), role: 'assistant', content: answer, sources, timestamp: new Date() },
    ]);
    setShowHistory(false);
  }, []);

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-5">
        {messages.length === 0 && !showHistory && (
          <div className="flex flex-col items-center justify-center h-full gap-4 -mt-8">
            <div className="text-center">
              <h2 className="text-base font-semibold mb-1 empty-title">What would you like to know?</h2>
              <p className="text-xs max-w-md empty-sub">
                Ask in plain English. The system searches 200 family offices across 45 fields,
                then streams a synthesized answer from the most relevant matches.
              </p>
            </div>
            <ExampleQueries onSelect={submit} disabled={isStreaming} />
            {history && history.length > 0 && (
              <button
                type="button"
                onClick={() => setShowHistory(true)}
                className="text-[11px] px-3 py-1.5 rounded-md transition-colors pill mt-2"
              >
                View Query History ({history.length})
              </button>
            )}
          </div>
        )}

        {showHistory && (
          <QueryHistory
            history={history || []}
            onSelect={loadFromHistory}
            onClose={() => setShowHistory(false)}
          />
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] ${
              msg.role === 'user'
                ? 'rounded-2xl rounded-br-sm px-4 py-2.5 msg-user'
                : 'rounded-2xl rounded-bl-sm px-4 py-3 msg-bot'
            }`}>
              <div className="text-[13px] leading-relaxed">
                {msg.role === 'user' ? (
                  <span>{msg.content}</span>
                ) : (
                  <div
                    className="prose-sm"
                    dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }}
                  />
                )}
                {isStreaming && msg.role === 'assistant' && msg === messages[messages.length - 1] && msg.content && (
                  <span className="inline-block w-1.5 h-4 ml-0.5 animate-pulse loading-dot" />
                )}
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

        {isStreaming && messages.length > 0 && !messages[messages.length - 1]?.content && (
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
          <div className="mb-3 flex items-center gap-2">
            <ExampleQueries onSelect={submit} disabled={isStreaming} />
            {history && history.length > 0 && (
              <button
                type="button"
                onClick={() => setShowHistory(!showHistory)}
                className="text-[11px] px-2 py-1 rounded transition-colors pill shrink-0"
                title="Query History"
              >
                History
              </button>
            )}
          </div>
        )}
        <form onSubmit={(e) => { e.preventDefault(); submit(input); }} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about family offices..."
            disabled={isStreaming}
            className="flex-1 px-4 py-2.5 rounded-lg text-sm disabled:opacity-40 input-box"
          />
          <button
            type="submit"
            disabled={!input.trim() || isStreaming}
            className="px-5 py-2.5 rounded-lg text-sm font-medium transition-colors btn-send"
          >
            {isStreaming ? 'Streaming...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
}
