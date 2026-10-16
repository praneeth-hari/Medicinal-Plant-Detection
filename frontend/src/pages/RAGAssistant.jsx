import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageSquare,
  Plus,
  Send,
  Sprout,
  BookOpen,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Bot,
  Info,
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  Search,
  Sparkles,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Loader from '../components/common/Loader';
import useToast from '../hooks/useToast';
import { sendMessage, getSessions, getSessionMessages } from '../api/chat';
import { getPlants } from '../api/plants';
import config from '../config/config';

export function RAGAssistant() {
  const { addToast } = useToast();
  const navigate = useNavigate();
  const messagesEndRef = useRef(null);

  // States
  const [sessions, setSessions] = useState([]);
  const [sessionsLoading, setSessionsLoading] = useState(true);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [sessionSearch, setSessionSearch] = useState('');
  const [messages, setMessages] = useState([]);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [catalogMap, setCatalogMap] = useState({}); // Matches source docs to plant profile IDs
  const [copiedMsgId, setCopiedMsgId] = useState(null);
  const [feedback, setFeedback] = useState({}); // { [msgId]: 'up' | 'down' }

  // Source expanded toggles: { [`${msgId}-${idx}`]: boolean }
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
    if (config.DEMO_MODE) {
      setSessions([]);
      setSessionsLoading(false);
      return;
    }
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
  // eslint-disable-next-line react-hooks/exhaustive-deps
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

  // Copy message text to clipboard
  const handleCopyMessage = (msgId, text) => {
    navigator.clipboard.writeText(text);
    setCopiedMsgId(msgId);
    addToast('Answer copied to clipboard!', 'success');
    setTimeout(() => {
      setCopiedMsgId(null);
    }, 2000);
  };

  // Handle feedback (Thumbs up / down)
  const handleFeedback = (msgId, type) => {
    setFeedback((prev) => ({
      ...prev,
      [msgId]: prev[msgId] === type ? null : type
    }));
    addToast(type === 'up' ? 'Helpful feedback recorded!' : 'Feedback noted for model improvement.', 'info');
  };

  // Submit new query
  const handleSend = async (queryToSend = null) => {
    const rawQuery = queryToSend || inputValue;
    if (!rawQuery.trim() || isSending) return;

    const userQuery = rawQuery.trim();
    setInputValue('');
    setIsSending(true);

    const tempUserMsg = {
      id: Date.now(),
      role: 'user',
      content: userQuery,
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    if (config.DEMO_MODE) {
      addToast('Live RAG requires the local backend server.', 'info');
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: 'ℹ️ **Static Showcase Mode:** Live conversational RAG requires the locally running FastAPI backend, Ollama (`qwen2.5:3b`), and the initialized FAISS vector database. Refer to the repository documentation to run the complete pipeline locally.',
          created_at: new Date().toISOString()
        }
      ]);
      setIsSending(false);
      return;
    }

    try {
      const response = await sendMessage(activeSessionId, userQuery);
      
      if (!activeSessionId) {
        const newSessionId = response.session_id;
        if (response.message) {
          setMessages((prev) => [...prev, response.message]);
        }
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

  // Safe and clean Markdown-like parser helper
  const parseMarkdown = (text) => {
    if (!text) return '';
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
    
    // Bold formatting: **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-surface-900">$1</strong>');
    
    // Italic formatting: *text*
    html = html.replace(/\*(.*?)\*/g, '<em class="italic text-surface-700">$1</em>');
    
    // Bullet / numbered list tags replacement
    html = html.replace(/^\s*[-*]\s+(.*)$/gm, '<li class="my-1">$1</li>');
    html = html.replace(/^\s*\d+\.\s+(.*)$/gm, '<li class="my-1">$1</li>');

    const lines = html.split('\n');
    let inList = false;
    let result = [];
    
    lines.forEach((line) => {
      const trimmed = line.trim();
      const isListItem = line.includes('<li>');
      
      if (isListItem) {
        if (!inList) {
          result.push('<ul class="list-disc pl-5 space-y-1 my-2.5 text-surface-700">');
          inList = true;
        }
        result.push(line);
      } else {
        if (inList) {
          result.push('</ul>');
          inList = false;
        }
        if (trimmed) {
          result.push(`<p class="leading-relaxed mb-3 text-surface-800">${line}</p>`);
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

  // Filtered session list
  const filteredSessions = sessions.filter((s) =>
    s.title?.toLowerCase().includes(sessionSearch.toLowerCase())
  );

  const sampleQuestions = [
    {
      title: 'Tulsi (Holy Basil)',
      prompt: 'What are the medicinal uses and active bio-compounds in Tulsi?'
    },
    {
      title: 'Ashwagandha Precautions',
      prompt: 'What precautions and contraindications should be considered with Ashwagandha?'
    },
    {
      title: 'Cardiovascular Formulations',
      prompt: 'Which medicinal plants are traditionally used to support heart health and blood pressure?'
    },
    {
      title: 'Giloy & Immunity',
      prompt: 'How is Giloy (Tinospora cordifolia) prepared for immune modulation?'
    }
  ];

  return (
    <div className="flex flex-col lg:flex-row gap-5 h-[calc(100vh-8.5rem)] relative z-10 w-full">
      {/* ─── Left Sidebar: Sessions & History ─────────────────── */}
      <div className="w-full lg:w-72 flex-shrink-0 flex flex-col gap-3 h-auto lg:h-full">
        <Button
          onClick={handleNewConversation}
          variant="primary"
          className="w-full flex items-center justify-center gap-2 py-3 rounded-xl text-xs shadow-md font-bold"
        >
          <Plus className="w-4 h-4" /> New Conversation
        </Button>

        <Card className="flex-1 overflow-hidden glass p-3 flex flex-col rounded-2xl shadow-sm">
          {/* Header & Search */}
          <div className="space-y-2 mb-2 pb-2 border-b border-surface-200">
            <div className="flex items-center justify-between px-1">
              <span className="text-[10px] font-bold text-surface-500 uppercase tracking-wider">
                Conversation History
              </span>
              <span className="text-[10px] font-mono text-surface-450 bg-surface-100 px-1.5 py-0.5 rounded">
                {sessions.length}
              </span>
            </div>
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-surface-400" />
              <input
                type="text"
                value={sessionSearch}
                onChange={(e) => setSessionSearch(e.target.value)}
                placeholder="Search chats..."
                className="w-full pl-8 pr-3 py-1.5 text-[11px] rounded-lg border border-surface-200 bg-white/70 focus:bg-white focus:outline-none focus:ring-1 focus:ring-primary-500/30 transition-all placeholder-surface-400"
              />
            </div>
          </div>

          {/* Session List */}
          <div className="flex-1 overflow-y-auto space-y-1 pr-1">
            {sessionsLoading && sessions.length === 0 ? (
              <div className="flex items-center justify-center py-8">
                <Loader className="w-5 h-5 text-primary-500" />
              </div>
            ) : filteredSessions.length === 0 ? (
              <div className="text-center py-8 text-xs text-surface-500 font-medium">
                {sessionSearch ? 'No matches found.' : 'No conversations yet.'}
              </div>
            ) : (
              filteredSessions.map((session) => {
                const isActive = activeSessionId === session.id;
                return (
                  <button
                    key={session.id}
                    onClick={() => setActiveSessionId(session.id)}
                    className={`flex items-center gap-2.5 w-full text-left px-3 py-2.5 rounded-xl text-xs transition-all ${
                      isActive
                        ? 'bg-primary-500/15 border border-primary-500/30 text-primary-750 font-bold shadow-sm'
                        : 'text-surface-700 hover:bg-black/5 border border-transparent font-medium'
                    }`}
                  >
                    <MessageSquare className={`w-3.5 h-3.5 flex-shrink-0 ${isActive ? 'text-primary-600' : 'text-surface-400'}`} />
                    <span className="truncate flex-1">{session.title}</span>
                  </button>
                );
              })
            )}
          </div>
        </Card>
      </div>

      {/* ─── Main Chat Window (Perplexity-Style Centered Stream) ─── */}
      <Card className="flex-1 flex flex-col glass p-0 overflow-hidden relative h-full rounded-2xl shadow-md border border-surface-200">
        {/* Top Header Bar */}
        <div className="px-6 py-3.5 border-b border-surface-200 flex items-center justify-between bg-white/60 z-10 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-500/10 rounded-xl border border-primary-500/20 text-primary-600">
              <Sprout className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-xs font-extrabold text-surface-900 flex items-center gap-1.5">
                MediPlant RAG Assistant
              </h4>
              <p className="text-[10px] text-surface-500 font-medium">
                Retrieval-Augmented Botanical Intelligence &amp; Clinical Monographs
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {config.DEMO_MODE ? (
              <span className="inline-flex items-center gap-1 text-[10px] bg-amber-500/10 border border-amber-500/25 text-amber-700 px-2.5 py-1 rounded-full font-bold">
                <span className="w-1.5 h-1.5 bg-amber-500 rounded-full" /> Demo Mode
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-[10px] bg-primary-500/10 border border-primary-500/25 text-primary-650 px-2.5 py-1 rounded-full font-bold">
                <span className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-ping" /> Online
              </span>
            )}
          </div>
        </div>

        {/* Demo Mode Notice Banner */}
        {config.DEMO_MODE && (
          <div className="mx-6 mt-3 px-3.5 py-2.5 bg-amber-500/10 border border-amber-500/20 rounded-xl text-amber-800 text-xs flex items-start gap-2.5 flex-shrink-0">
            <Info className="w-4 h-4 flex-shrink-0 mt-0.5 text-amber-600" />
            <p className="text-[11px] leading-relaxed">
              <strong className="font-semibold">Static Showcase Mode:</strong> Live RAG requires the local backend, Ollama (<code className="font-mono text-[10px]">qwen2.5:3b</code>), and initialized FAISS embeddings.
            </p>
          </div>
        )}

        {/* ─── Scrollable Message Stream (Centered Reading Column) ─── */}
        <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6">
          <div className="max-w-3xl mx-auto space-y-6">
            <AnimatePresence initial={false}>
              {messages.length === 0 && !isSending ? (
                /* Empty / New Chat State */
                <motion.div
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex flex-col items-center justify-center text-center py-10 space-y-6"
                >
                  <div className="w-16 h-16 rounded-2xl bg-primary-500/10 border border-primary-500/25 text-primary-600 flex items-center justify-center shadow-md">
                    <Sprout className="w-8 h-8 animate-pulse" />
                  </div>

                  <div className="space-y-1.5 max-w-lg">
                    <h3 className="text-xl font-black text-surface-900 tracking-tight">
                      What medicinal plant would you like to explore?
                    </h3>
                    <p className="text-xs text-surface-600 leading-relaxed font-medium">
                      Ask about active phytochemicals, Ayurvedic formulations, clinical safety, dosage protocols, and botanical monographs.
                    </p>
                  </div>

                  {/* Sample Query Cards */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl pt-2 text-left">
                    {sampleQuestions.map((sample) => (
                      <button
                        key={sample.title}
                        onClick={() => handleSend(sample.prompt)}
                        className="p-3.5 rounded-xl border border-surface-200 bg-white/80 hover:bg-white hover:border-primary-500/35 hover:shadow-md transition-all group flex flex-col justify-between"
                      >
                        <div className="flex items-center justify-between w-full mb-1.5">
                          <span className="text-[11px] font-bold text-primary-700 flex items-center gap-1.5">
                            <Sparkles className="w-3 h-3 text-primary-500" />
                            {sample.title}
                          </span>
                          <ArrowRight className="w-3 h-3 text-surface-400 group-hover:text-primary-600 group-hover:translate-x-0.5 transition-all" />
                        </div>
                        <p className="text-[11px] text-surface-600 leading-relaxed font-normal">
                          {sample.prompt}
                        </p>
                      </button>
                    ))}
                  </div>
                </motion.div>
              ) : (
                /* Message List */
                messages.map((msg) => (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-3"
                  >
                    {msg.role === 'user' ? (
                      /* User Message Bubble */
                      <div className="flex justify-end">
                        <div className="max-w-xl rounded-2xl px-4 py-3 bg-primary-500 text-white shadow-md text-xs leading-relaxed font-medium">
                          <p className="whitespace-pre-line">{msg.content}</p>
                        </div>
                      </div>
                    ) : (
                      /* Assistant Message (Perplexity Research Layout) */
                      <div className="w-full bg-white rounded-2xl p-5 border border-surface-200 shadow-sm space-y-4">
                        {/* Header: Bot Avatar & Citation Summary */}
                        <div className="flex items-center justify-between pb-3 border-b border-surface-100">
                          <div className="flex items-center gap-2">
                            <div className="w-6 h-6 rounded-lg bg-primary-500/10 border border-primary-500/20 text-primary-600 flex items-center justify-center">
                              <Bot className="w-3.5 h-3.5" />
                            </div>
                            <span className="text-xs font-bold text-surface-900">
                              MediPlant RAG Model
                            </span>
                          </div>

                          {/* Quick Sources Count Badge */}
                          {msg.sources && msg.sources.length > 0 && (
                            <span className="text-[10px] font-bold text-primary-700 bg-primary-500/10 border border-primary-500/20 px-2 py-0.5 rounded-full flex items-center gap-1">
                              <BookOpen className="w-3 h-3" />
                              {msg.sources.length} Verified Sources
                            </span>
                          )}
                        </div>

                        {/* Perplexity-style Citations Pill Row */}
                        {msg.sources && Array.isArray(msg.sources) && msg.sources.length > 0 && (
                          <div className="space-y-2">
                            <div className="text-[10px] font-bold text-surface-500 uppercase tracking-wider flex items-center gap-1">
                              <span>Sources Referenced</span>
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {msg.sources.map((src, idx) => {
                                const key = `${msg.id}-${idx}`;
                                const isExpanded = expandedSources[key];
                                return (
                                  <button
                                    key={idx}
                                    onClick={() => toggleSourceExpand(msg.id, idx)}
                                    className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-semibold border transition-all ${
                                      isExpanded
                                        ? 'bg-primary-500/15 border-primary-500/35 text-primary-750 shadow-sm'
                                        : 'bg-surface-50 hover:bg-surface-100 border-surface-200 text-surface-700'
                                    }`}
                                  >
                                    <span className="font-mono text-[9px] px-1 bg-black/5 rounded">
                                      {idx + 1}
                                    </span>
                                    <span className="capitalize truncate max-w-[140px]">
                                      {src.document.replace(/_monograph$/, '').replace(/_/g, ' ')}
                                    </span>
                                    <span className="text-[9px] text-primary-600 font-mono font-bold">
                                      {Math.round(src.relevance_score * 100)}%
                                    </span>
                                    {isExpanded ? (
                                      <ChevronUp className="w-3 h-3 text-surface-400" />
                                    ) : (
                                      <ChevronDown className="w-3 h-3 text-surface-400" />
                                    )}
                                  </button>
                                );
                              })}
                            </div>

                            {/* Expanded Citation Preview Box */}
                            {msg.sources.map((src, idx) => {
                              const key = `${msg.id}-${idx}`;
                              const isExpanded = expandedSources[key];
                              if (!isExpanded) return null;
                              const linkId = getSourcePlantLink(src.document);
                              return (
                                <motion.div
                                  key={`expanded-${idx}`}
                                  initial={{ opacity: 0, height: 0 }}
                                  animate={{ opacity: 1, height: 'auto' }}
                                  exit={{ opacity: 0, height: 0 }}
                                  className="mt-2 p-3 bg-surface-50 rounded-xl border border-surface-200 text-xs space-y-2 text-surface-700"
                                >
                                  <div className="flex items-center justify-between font-bold text-[11px] text-surface-900 border-b border-surface-200 pb-1.5">
                                    <span className="capitalize">
                                      Reference [{idx + 1}]: {src.document.replace(/_/g, ' ')}
                                    </span>
                                    {src.page && (
                                      <span className="text-[10px] text-surface-500 font-mono">
                                        Page {src.page}
                                      </span>
                                    )}
                                  </div>
                                  <p className="italic text-[11px] text-surface-600 leading-relaxed border-l-2 border-primary-500 pl-2">
                                    &quot;{src.snippet}&quot;
                                  </p>
                                  {linkId && (
                                    <div className="pt-1 flex justify-end">
                                      <button
                                        onClick={() => navigate(`/plants/${linkId}`)}
                                        className="inline-flex items-center gap-1 font-bold text-primary-600 hover:text-primary-700 text-[10px] hover:underline"
                                      >
                                        View Full Plant Monograph in Library <ExternalLink className="w-3 h-3" />
                                      </button>
                                    </div>
                                  )}
                                </motion.div>
                              );
                            })}
                          </div>
                        )}

                        {/* Answer Content */}
                        <div
                          className="prose prose-sm max-w-none text-xs leading-relaxed pt-1"
                          dangerouslySetInnerHTML={{ __html: parseMarkdown(msg.content) }}
                        />

                        {/* Action Toolbar: Copy, Feedback */}
                        <div className="pt-2 border-t border-surface-100 flex items-center justify-between text-[11px] text-surface-500">
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => handleCopyMessage(msg.id, msg.content)}
                              className="inline-flex items-center gap-1 px-2 py-1 rounded-md hover:bg-surface-100 text-surface-600 hover:text-surface-900 transition-colors font-medium"
                              title="Copy answer"
                            >
                              {copiedMsgId === msg.id ? (
                                <>
                                  <Check className="w-3.5 h-3.5 text-emerald-600" />
                                  <span className="text-emerald-600 font-bold">Copied</span>
                                </>
                              ) : (
                                <>
                                  <Copy className="w-3.5 h-3.5" />
                                  <span>Copy</span>
                                </>
                              )}
                            </button>
                          </div>

                          <div className="flex items-center gap-1.5">
                            <button
                              onClick={() => handleFeedback(msg.id, 'up')}
                              className={`p-1 rounded-md transition-colors ${
                                feedback[msg.id] === 'up'
                                  ? 'bg-primary-500/15 text-primary-700'
                                  : 'hover:bg-surface-100 text-surface-400 hover:text-surface-700'
                              }`}
                              title="Helpful response"
                            >
                              <ThumbsUp className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleFeedback(msg.id, 'down')}
                              className={`p-1 rounded-md transition-colors ${
                                feedback[msg.id] === 'down'
                                  ? 'bg-red-500/15 text-red-700'
                                  : 'hover:bg-surface-100 text-surface-400 hover:text-surface-700'
                              }`}
                              title="Needs improvement"
                            >
                              <ThumbsDown className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))
              )}

              {/* Streaming / Thinking Indicator */}
              {isSending && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="w-full bg-white rounded-2xl p-4 border border-surface-200 shadow-sm flex items-center gap-3"
                >
                  <div className="w-6 h-6 rounded-lg bg-primary-500/10 text-primary-600 flex items-center justify-center">
                    <Bot className="w-3.5 h-3.5 animate-pulse" />
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="flex gap-1">
                      <span className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </span>
                    <span className="text-[11px] text-surface-500 font-bold tracking-wide">
                      Searching indexed monographs and analyzing traditional formulations...
                    </span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* ─── Bottom Floating Prompt Dock (Centered) ─────────── */}
        <div className="p-4 border-t border-surface-200 bg-white/70 backdrop-blur-sm flex-shrink-0 z-10">
          <div className="max-w-3xl mx-auto space-y-2">
            <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask about medicinal herbs, active compounds, dosages, precautions..."
                className="flex-1 px-4 py-3 text-xs rounded-xl border border-surface-200 bg-white focus:bg-white transition-all focus:outline-none focus:ring-2 focus:ring-primary-500/25 focus:border-primary-500 text-surface-900 placeholder-surface-400 shadow-inner"
                disabled={isSending || messagesLoading}
                required
              />
              <Button
                type="submit"
                variant="primary"
                disabled={!inputValue.trim() || isSending || messagesLoading}
                className="px-5 rounded-xl shadow-md text-xs font-bold"
              >
                <Send className="w-4 h-4" />
              </Button>
            </form>

            {/* Medical Disclaimer */}
            <div className="flex items-center justify-center gap-1.5 text-[10px] text-surface-450 text-center font-medium">
              <ShieldAlert className="w-3 h-3 text-surface-400" />
              <span>
                MediPlant AI retrieves indexed herbal monographs and research papers. Verify clinical applications with a qualified practitioner.
              </span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}

export default RAGAssistant;
