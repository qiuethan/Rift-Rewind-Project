import { useState, useEffect } from 'react';
import { chat, checkHealth, ChatResponse } from '@/api/llm';
import './TestChatPage.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  metadata?: {
    model_used?: string;
    complexity?: string;
    contexts_used?: string[];
  };
  timestamp: Date;
}

export default function TestChatPage() {
  const [prompt, setPrompt] = useState('');
  const [matchId, setMatchId] = useState('');
  const [championId, setChampionId] = useState('');
  const [pageContext, setPageContext] = useState('test_page');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [llmStatus, setLlmStatus] = useState<'checking' | 'healthy' | 'unavailable'>('checking');

  // Check LLM health on mount
  useEffect(() => {
    const checkLLMHealth = async () => {
      try {
        const health = await checkHealth();
        setLlmStatus(health.bedrock_available ? 'healthy' : 'unavailable');
      } catch (err) {
        console.error('Failed to check LLM health:', err);
        setLlmStatus('unavailable');
      }
    };
    checkLLMHealth();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setLoading(true);
    setError(null);

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: prompt,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const response: ChatResponse = await chat({
        prompt: prompt.trim(),
        match_id: matchId.trim() || undefined,
        champion_id: championId ? parseInt(championId) : undefined,
        page_context: pageContext,
      });

      // Add assistant message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.text,
        metadata: {
          model_used: response.model_used,
          complexity: response.complexity,
          contexts_used: response.contexts_used,
        },
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Clear prompt
      setPrompt('');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get response';
      setError(errorMessage);
      
      // Add error message
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `❌ Error: ${errorMessage}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  const loadExamplePrompt = (example: string) => {
    setPrompt(example);
  };

  return (
    <div className="test-chat-page">
      <div className="test-chat-container">
        {/* Header */}
        <div className="test-chat-header">
          <h1>🧪 AI Chat Test Page</h1>
          <div className="llm-status">
            <span className={`status-indicator status-${llmStatus}`}></span>
            <span className="status-text">
              {llmStatus === 'checking' && 'Checking LLM status...'}
              {llmStatus === 'healthy' && 'LLM Service: Healthy'}
              {llmStatus === 'unavailable' && 'LLM Service: Unavailable'}
            </span>
          </div>
        </div>

        {/* Instructions */}
        <div className="test-instructions">
          <h3>How to test:</h3>
          <ol>
            <li>Enter your question in the prompt field</li>
            <li>Optionally provide Match ID or Champion ID for context</li>
            <li>Click "Send" to get AI response</li>
            <li>View the response with metadata (model used, contexts fetched)</li>
          </ol>
        </div>

        {/* Example Prompts */}
        <div className="example-prompts">
          <h4>Example Prompts:</h4>
          <div className="example-buttons">
            <button onClick={() => loadExamplePrompt('How am I doing overall?')}>
              General Question
            </button>
            <button onClick={() => loadExamplePrompt('How am I doing on Yasuo?')}>
              Champion Question
            </button>
            <button onClick={() => loadExamplePrompt('What went wrong in this game?')}>
              Match Question
            </button>
            <button onClick={() => loadExamplePrompt('Am I improving on this champion?')}>
              Progress Question
            </button>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="empty-state">
              <p>No messages yet. Start by asking a question!</p>
            </div>
          ) : (
            messages.map((message) => (
              <div key={message.id} className={`message message-${message.role}`}>
                <div className="message-header">
                  <span className="message-role">
                    {message.role === 'user' ? '👤 You' : '🤖 AI Assistant'}
                  </span>
                  <span className="message-time">
                    {message.timestamp.toLocaleTimeString()}
                  </span>
                </div>
                <div className="message-content">{message.content}</div>
                {message.metadata && (
                  <div className="message-metadata">
                    <span className="metadata-item">
                      Model: <strong>{message.metadata.model_used}</strong>
                    </span>
                    <span className="metadata-item">
                      Complexity: <strong>{message.metadata.complexity}</strong>
                    </span>
                    <span className="metadata-item">
                      Contexts: <strong>{message.metadata.contexts_used?.join(', ')}</strong>
                    </span>
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Input Form */}
        <form className="chat-form" onSubmit={handleSubmit}>
          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}

          <div className="form-row">
            <div className="form-group full-width">
              <label htmlFor="prompt">Prompt (Required)</label>
              <textarea
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Ask a question... (e.g., How am I doing on Yasuo?)"
                rows={3}
                disabled={loading}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="matchId">Match ID (Optional)</label>
              <input
                type="text"
                id="matchId"
                value={matchId}
                onChange={(e) => setMatchId(e.target.value)}
                placeholder="e.g., NA1_1234567890"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="championId">Champion ID (Optional)</label>
              <input
                type="number"
                id="championId"
                value={championId}
                onChange={(e) => setChampionId(e.target.value)}
                placeholder="e.g., 157 for Yasuo"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="pageContext">Page Context</label>
              <select
                id="pageContext"
                value={pageContext}
                onChange={(e) => setPageContext(e.target.value)}
                disabled={loading}
              >
                <option value="test_page">Test Page</option>
                <option value="dashboard">Dashboard</option>
                <option value="champion_detail">Champion Detail</option>
                <option value="match_detail">Match Detail</option>
              </select>
            </div>
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={clearChat}
              className="btn-secondary"
              disabled={loading || messages.length === 0}
            >
              Clear Chat
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={loading || !prompt.trim()}
            >
              {loading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
