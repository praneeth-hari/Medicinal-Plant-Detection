import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageSquare,
  Plus,
  Send,
  Sprout,
  User,
  History,
  BookOpen,
  ChevronDown,
  ChevronUp,
  Search,
  ExternalLink,
  Bot
} from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Loader from '../components/common/Loader';
import useToast from '../hooks/useToast';
import { sendMessage, getSessions, getSessionMessages } from '../api/chat';
import { getPlants } from '../api/plants';

export function RAGAssistant() {
  const { addToast } = useToast();
  const navigate = useNavigate();
  const messagesEndRef = useRef(null);

  // States
  const [sessions, setSessions] = useState([]);
  const [sessionsLoading, setSessionsLoading] = useState(true);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [catalogMap, setCatalogMap] = useState({}); // Matches source docs to plant profile IDs

  // Source expanded toggles
  const [expandedSources, setExpandedSources] = useState({});

  // Fetch catalog mapping so we can link citations back to detail monographs
  useEffect(() => {
    async function fetchCatalog() {
      try {
        const response = await getPlants();
        const mapping = {};
        if (response.data && Array.isArray(response.data)) {
          response.data.forEach((p) => {
            mapping[p.common_name.toLowerCase()] = p.id;
            mapping[p.scientific_name.toLowerCase()] = p.id;
            const monoKey = p.common_name.toLowerCase().replace(/\s+/g, '_') + '_monograph';
            mapping[monoKey] = p.id;
          });
        }
        setCatalogMap(mapping);
      } catch (err) {
        console.warn('Failed to load plant catalog index mapping:', err);
      }
    }
    fetchCatalog();
  }, []);

  // Fetch all chat sessions
  const loadSessions = useCallback(async (selectId = null) => {
    setSessionsLoading(true);
    try {
      const data = await getSessions();
      setSessions(data || []);
      
      if (selectId) {
        setActiveSessionId(selectId);
      } else if (data && data.length > 0 && !activeSessionId) {
        setActiveSessionId(data[0].id);
      }
    } catch (err) {
      console.error(err);
      addToast('Failed to load chat history sessions.', 'error');
    } finally {
      setSessionsLoading(false);
    }
  }, [activeSessionId, addToast]);

  // Load message logs for active session
  const loadMessages = useCallback(async (sessionId) => {
    if (!sessionId) return;
    setMessagesLoading(true);
    try {
      const data = await getSessionMessages(sessionId);
      setMessages(data || []);
    } catch (err) {
      console.error(err);
      addToast('Failed to load messages history.', 'error');
    } finally {
      setMessagesLoading(false);
    }
  }, [addToast]);

  // Initial load
  useEffect(() => {
    loadSessions();
  }, []);

  // Sync messages when active session changes
  useEffect(() => {
    if (activeSessionId) {
      loadMessages(activeSessionId);
    } else {
      setMessages([]);
    }
  }, [activeSessionId, loadMessages]);

  // Auto-scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isSending]);

  // Start a new clean conversation session
  const handleNewConversation = () => {
    setActiveSessionId(null);
    setMessages([]);
    setInputValue('');
  };

  // Submit new query
  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isSending) return;

    const userQuery = inputValue.trim();
    setInputValue('');
    setIsSending(true);

    const tempUserMsg = {
      id: Date.now(),
      role: 'user',
      content: userQuery,
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const response = await sendMessage(activeSessionId, userQuery);
      
      if (!activeSessionId) {
        const newSessionId = response.session_id;
        setActiveSessionId(newSessionId);
        await loadSessions(newSessionId);
      } else {
        setMessages((prev) => [...prev, response.message]);
      }
    } catch (err) {
      console.error(err);
      addToast('Error generating answer. RAG Pipeline offline.', 'error');
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: '⚠️ Connection lost. Ensure local Ollama service is running with your custom model and the vector database is initialized.',
          created_at: new Date().toISOString()
        }
      ]);
    } finally {
      setIsSending(false);
    }
  };

  // Safe and clean Markdown-like parser helper (inherits text color)
  const parseMarkdown = (text) => {
    if (!text) return '';
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
    
    // Bold formatting: **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Italic formatting: *text*
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Bullet / numbered list tags replacement
    html = html.replace(/^\s*[-*]\s+(.*)$/gm, '<li>$1</li>');
    html = html.replace(/^\s*\d+\.\s+(.*)$/gm, '<li>$1</li>');

    const lines = html.split('\n');
    let inList = false;
    let result = [];
    
    lines.forEach((line) => {
      const trimmed = line.trim();
      const isListItem = line.includes('<li>');
      
      if (isListItem) {
        if (!inList) {
          result.push('<ul class="list-slate list-disc pl-5 space-y-1.5 my-2">');
          inList = true;
        }
        result.push(line);
      } else {
        if (inList) {
          result.push('</ul>');
          inList = false;
        }
        if (trimmed) {
          result.push(`<p class="leading-relaxed mb-3">${line}</p>`);
        }
      }
    });
    
    if (inList) result.push('</ul>');
    return result.join('\n');
  };

  const toggleSourceExpand = (msgId, srcIdx) => {
    const key = `${msgId}-${srcIdx}`;
    setExpandedSources((prev) => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const getSourcePlantLink = (docName) => {
    if (!docName) return null;
    const cleanDoc = docName.toLowerCase().replace(/_monograph$/, '').replace(/_/g, ' ');
    return catalogMap[cleanDoc] || catalogMap[docName.toLowerCase()] || null;
  };

  return (
    <div className="flex flex-col lg:flex-row gap-6 h-[calc(100vh-10rem)] relative z-10 w-full">
      {/* Session selection panel */}
      <div className="w-full lg:w-64 flex-shrink-0 flex flex-col gap-3 h-full">
        <Button
          onClick={handleNewConversation}
          variant="primary"
          className="w-full flex items-center justify-center gap-2 py-3 shadow-glow rounded-xl text-xs"
        >
          <Plus className="w-4 h-4" /> New Conversation
        </Button>

        <Card className="flex-1 overflow-y-auto glass border border-surface-200 dark:border-white/10 p-3 flex flex-col min-h-[150px] lg:min-h-0 rounded-2xl shadow-md">
          <div className="text-[10px] font-bold text-surface-500 dark:text-surface-400 uppercase tracking-wider px-2 py-1.5 mb-2 border-b border-surface-200 dark:border-white/5">
            Conversation Logs
          </div>
          
          {sessionsLoading && sessions.length === 0 ? (
            <div className="flex items-center justify-center py-8">
              <Loader className="w-5 h-5 text-primary-500" />
            </div>
          ) : sessions.length === 0 ? (
            <div className="text-center py-8 text-xs text-surface-500 dark:text-surface-450 font-bold">
              No history found.
            </div>
          ) : (
            <div className="space-y-1.5 flex-1 overflow-y-auto pr-1">
              {sessions.map((session) => (
                <button
                  key={session.id}
                  onClick={() => setActiveSessionId(session.id)}
                  className={`flex items-center gap-2.5 w-full text-left px-3 py-2.5 rounded-xl text-xs font-semibold border transition-all ${
                    activeSessionId === session.id
                      ? 'bg-primary-500/10 border-primary-500/30 text-surface-900 dark:text-white font-extrabold shadow-glow-sm'
                      : 'text-surface-600 dark:text-surface-300 hover:bg-black/5 dark:hover:bg-white/5 border-transparent'
                  }`}
                >
                  <MessageSquare className="w-4 h-4 flex-shrink-0 text-surface-400" />
                  <span className="truncate flex-1">{session.title}</span>
                </button>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* Main chat window */}
      <Card className="flex-1 flex flex-col glass border border-surface-200 dark:border-white/10 p-0 overflow-hidden relative h-full rounded-2xl shadow-lg">
        {/* Connection health check bar */}
        <div className="px-6 py-4 border-b border-surface-200 dark:border-white/10 flex items-center justify-between bg-black/[0.02] dark:bg-black/25 z-10 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-500/15 rounded-xl border border-primary-500/25">
              <Sprout className="w-4 h-4 text-primary-600 dark:text-primary-400" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-surface-900 dark:text-white flex items-center gap-1.5">
                MediPlant RAG Expert
              </h4>
              <p className="text-[9px] text-surface-500 dark:text-surface-400 font-semibold">Contextual references loaded dynamically</p>
            </div>
          </div>
          <span className="inline-flex items-center gap-1 text-[9px] bg-primary-500/10 border border-primary-500/25 text-primary-600 dark:text-primary-400 px-2 py-0.5 rounded-full font-bold">
            <span className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-ping" /> Online
          </span>
        </div>

        {/* Message Feed Area */}
        <div className="flex-1 p-6 space-y-6 overflow-y-auto bg-gradient-to-b from-white/[0.01] to-transparent">
          <AnimatePresence initial={false}>
            {messages.length === 0 && !isSending ? (
              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col items-center justify-center h-full text-center max-w-md mx-auto py-12 space-y-4"
              >
                <div className="w-14 h-14 rounded-2xl bg-white/5 border border-surface-200 dark:border-white/10 text-primary-600 dark:text-primary-400 flex items-center justify-center shadow-md">
                  <Sprout className="w-7 h-7 animate-pulse" />
                </div>
                <h3 className="text-sm font-extrabold text-surface-900 dark:text-white">
                  Consult the Medicinal RAG Assistant
                </h3>
                <p className="text-xs text-surface-600 dark:text-surface-300 leading-relaxed max-w-sm font-semibold">
                  Inquire regarding botanical compound classifications, prep methodology, and clinical precautions.
                </p>
                <div className="grid grid-cols-1 gap-2 w-full pt-2">
                  <button
                    onClick={() => setInputValue('What are the medicinal uses of Tulsi?')}
                    className="px-4 py-3 text-left text-xs bg-white dark:bg-white/5 hover:bg-black/5 dark:hover:bg-white/10 rounded-xl border border-surface-200 dark:border-white/10 text-surface-700 dark:text-surface-200 transition-all font-bold"
                  >
                    What are the medicinal uses of Tulsi?
                  </button>
                  <button
                    onClick={() => setInputValue('What precautions should be taken with Ashwagandha?')}
                    className="px-4 py-3 text-left text-xs bg-white dark:bg-white/5 hover:bg-black/5 dark:hover:bg-white/10 rounded-xl border border-surface-200 dark:border-white/10 text-surface-700 dark:text-surface-200 transition-all font-bold"
                  >
                    What precautions should be taken with Ashwagandha?
                  </button>
                </div>
              </motion.div>
            ) : (
              <div className="space-y-6">
                {messages.map((msg) => (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-2xl text-xs space-y-2 rounded-2xl p-5 shadow-md border ${
                        msg.role === 'user'
                          ? 'bg-gradient-to-br from-primary-600 to-emerald-600 border-primary-500/35 text-white rounded-br-none'
                          : 'glass border-surface-200 dark:border-white/10 text-surface-800 dark:text-surface-200 rounded-bl-none'
                      }`}
                    >
                      <div className="flex items-center gap-2 text-[9px] uppercase tracking-wider font-bold opacity-60 mb-2 border-b border-surface-150 dark:border-white/5 pb-1">
                        {msg.role === 'user' ? (
                          <>
                            <User className="w-3.5 h-3.5" />
                            <span>User</span>
                          </>
                        ) : (
                          <>
                            <Bot className="w-3.5 h-3.5 text-primary-600 dark:text-primary-400" />
                            <span>MediPlant Agent</span>
                          </>
                        )}
                      </div>

                      {msg.role === 'user' ? (
                        <p className="leading-relaxed whitespace-pre-line text-sm">{msg.content}</p>
                      ) : (
                        <div
                          className="prose prose-sm dark:prose-invert max-w-none text-xs leading-relaxed"
                          dangerouslySetInnerHTML={{ __html: parseMarkdown(msg.content) }}
                        />
                      )}

                      {/* Cited Sources Panel */}
                      {msg.role === 'assistant' && msg.sources && Array.isArray(msg.sources) && msg.sources.length > 0 && (
                        <div className="mt-4 pt-3 border-t border-surface-150 dark:border-white/5 space-y-2">
                          <div className="text-[10px] font-bold text-surface-500 dark:text-surface-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                            <BookOpen className="w-3.5 h-3.5 text-primary-600 dark:text-primary-400" />
                            <span>Cited Documents ({msg.sources.length})</span>
                          </div>
                          
                          <div className="space-y-2">
                            {msg.sources.map((src, idx) => {
                              const isExpanded = expandedSources[`${msg.id}-${idx}`];
                              const linkId = getSourcePlantLink(src.document);
                              return (
                                <div
                                  key={idx}
                                  className="bg-black/[0.02] dark:bg-black/30 border border-surface-200 dark:border-white/5 rounded-xl p-3 text-xs"
                                >
                                  <div className="flex justify-between items-center">
                                    <div className="flex items-center gap-2">
                                      <span className="font-bold text-surface-900 dark:text-white capitalize">
                                        {src.document.replace(/_/g, ' ')}
                                      </span>
                                      {src.page && <span className="text-[9px] text-surface-500 dark:text-surface-450">P. {src.page}</span>}
                                    </div>
                                    <div className="flex items-center gap-2.5">
                                      <span className="text-[9px] font-bold text-primary-600 dark:text-primary-400 bg-primary-500/10 px-1.5 py-0.5 rounded border border-primary-500/20">
                                        Match: {Math.round(src.relevance_score * 100)}%
                                      </span>
                                      <button
                                        onClick={() => toggleSourceExpand(msg.id, idx)}
                                        className="p-0.5 hover:bg-black/5 dark:hover:bg-white/10 rounded transition-colors text-surface-500 hover:text-surface-900 dark:text-surface-400 dark:hover:text-white"
                                      >
                                        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                                      </button>
                                    </div>
                                  </div>

                                  {isExpanded && (
                                    <div className="mt-2 text-[11px] italic bg-white/40 dark:bg-white/[0.02] p-2.5 rounded border-l-2 border-primary-500 leading-relaxed text-surface-600 dark:text-surface-300">
                                      "{src.snippet}"
                                      {linkId && (
                                        <div className="mt-2.5 text-right">
                                          <button
                                            onClick={() => navigate(`/plants/${linkId}`)}
                                            className="inline-flex items-center gap-1 font-bold text-primary-600 dark:text-primary-400 hover:underline text-[9px]"
                                          >
                                            View Monograph File <ExternalLink className="w-3 h-3" />
                                          </button>
                                        </div>
                                      )}
                                    </div>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}

                {isSending && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex justify-start"
                  >
                    <div className="rounded-2xl p-4 bg-white dark:bg-white/5 border border-surface-200 dark:border-white/5 text-xs flex items-center gap-2 shadow-sm">
                      <span className="flex gap-1">
                        <span className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <span className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <span className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </span>
                      <span className="text-[10px] text-surface-500 dark:text-surface-400 font-bold ml-1 uppercase tracking-wider">Groq Model is computing...</span>
                    </div>
                  </motion.div>
                )}
              </div>
            )}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </div>

        {/* Input Text Form */}
        <form
          onSubmit={handleSend}
          className="p-4 border-t border-surface-200 dark:border-white/10 bg-black/[0.01] dark:bg-black/25 flex gap-2 flex-shrink-0 z-10"
        >
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type a medicinal query..."
            className="flex-1 px-4 py-3 text-xs rounded-xl border border-surface-200 dark:border-white/10 bg-white dark:bg-black/40 focus:bg-white dark:focus:bg-black/60 transition-all focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 text-surface-900 dark:text-white placeholder-surface-400 dark:placeholder-surface-450"
            disabled={isSending || messagesLoading}
            required
          />
          <Button
            type="submit"
            variant="primary"
            disabled={!inputValue.trim() || isSending || messagesLoading}
            className="px-5 rounded-xl shadow-glow text-xs"
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </Card>
    </div>
  );
}

export default RAGAssistant;
