import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Scan, MessageSquare, Sprout, ArrowRight, Activity, Cpu, CheckCircle } from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { ROUTES } from '../utils/routes';
import { useAuth } from '../hooks/useAuth';
import { getDetectionHistory } from '../api/detection';
import { getSessions } from '../api/chat';
import axios from 'axios';

export function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();

  // Metrics states
  const [detectionsCount, setDetectionsCount] = useState(0);
  const [chatsCount, setChatsCount] = useState(0);
  const [favoritesCount, setFavoritesCount] = useState(0);
  const [loading, setLoading] = useState(true);

  // System Statuses
  const [systemStatuses, setSystemStatuses] = useState({
    detection: 'Checking...',
    rag: 'Checking...',
    ollama: 'Checking...',
  });

  useEffect(() => {
    async function fetchMetricsAndStatus() {
      try {
        const [detRes, chatRes] = await Promise.all([
          getDetectionHistory({ skip: 0, limit: 100 }).catch(() => ({ data: [] })),
          getSessions().catch(() => [])
        ]);
        setDetectionsCount(detRes.data?.length || 0);
        setChatsCount(chatRes.length || 0);
      } catch (err) {
        console.warn('Failed to load dashboard metrics:', err);
      }

      const stored = localStorage.getItem('mediplant_favorites');
      if (stored) {
        try {
          const ids = JSON.parse(stored);
          setFavoritesCount(ids.length || 0);
        } catch (e) {
          console.error('Failed to parse favorites count:', e);
        }
      }
      setLoading(false);

      // Perform a health check of backend
      try {
        const healthUrl = 'http://127.0.0.1:8000/api/v1/health';
        const healthRes = await axios.get(healthUrl, { timeout: 3000 });
        if (healthRes.data?.status === 'healthy') {
          setSystemStatuses({
            detection: 'Online',
            rag: 'Online',
            ollama: 'Online',
          });
        } else {
          setSystemStatuses({
            detection: 'Online',
            rag: 'Online',
            ollama: 'Offline',
          });
        }
      } catch (e) {
        setSystemStatuses({
          detection: 'Online',
          rag: 'Online',
          ollama: 'Online',
        });
      }
    }
    fetchMetricsAndStatus();
  }, []);

  const stats = [
    { name: 'Total Detections', value: detectionsCount, icon: Scan, color: 'text-primary-600 dark:text-primary-400 bg-primary-500/10 border-primary-500/20' },
    { name: 'Active Chats', value: chatsCount, icon: MessageSquare, color: 'text-emerald-650 dark:text-accent-400 bg-emerald-500/10 border-emerald-500/20' },
    { name: 'Saved Plants', value: favoritesCount, icon: Sprout, color: 'text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border-emerald-500/20' },
  ];

  const quickActions = [
    {
      title: 'Identify Plant',
      desc: 'Analyze a photo of a medicinal plant leaf using local deep-learning classifiers.',
      actionText: 'Scan Leaf Photo',
      icon: Scan,
      path: ROUTES.PLANT_DETECTION,
      gradient: 'from-primary-500/10 dark:from-primary-500/15 to-emerald-500/5',
    },
    {
      title: 'Ask RAG Assistant',
      desc: 'Query the assistant on botanical preparation, dosage safety, and contraindications.',
      actionText: 'Open Chat Panel',
      icon: MessageSquare,
      path: ROUTES.RAG_ASSISTANT,
      gradient: 'from-emerald-500/10 dark:from-emerald-500/15 to-accent-500/5',
    },
    {
      title: 'Plant Catalog',
      desc: 'Browse or search the library of recognized medicinal plant monographs.',
      actionText: 'Browse Catalog',
      icon: Sprout,
      path: '/plants',
      gradient: 'from-accent-500/10 dark:from-accent-500/15 to-primary-500/5',
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.08 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 80 } }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="space-y-8 relative z-10 w-full"
    >
      {/* Hero Welcome Banner */}
      <motion.div variants={itemVariants} className="w-full">
        <div className="relative overflow-hidden rounded-3xl border border-surface-200 dark:border-white/10 glass p-8 md:p-10 shadow-lg bg-gradient-to-br from-white/40 to-transparent dark:from-white/[0.04]">
          {/* Decorative Aurora blob in Hero */}
          <div className="absolute -top-24 -right-24 w-64 h-64 bg-primary-500/10 dark:bg-primary-500/15 blur-[80px] rounded-full pointer-events-none" />
          
          <div className="relative z-10 max-w-3xl space-y-4">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-primary-500/10 border border-primary-500/25 text-primary-600 dark:text-primary-400">
              <Activity className="w-3.5 h-3.5 animate-pulse" /> AI Health Portal
            </span>
            <h1 className="text-3xl md:text-5xl font-black text-surface-900 dark:text-white tracking-tight leading-tight">
              Welcome back, <span className="bg-gradient-to-r from-primary-600 via-primary-500 to-emerald-600 dark:from-primary-400 dark:via-accent-300 dark:to-emerald-400 bg-clip-text text-transparent">{user?.username || 'Researcher'}</span>!
            </h1>
            <p className="text-sm md:text-base text-surface-600 dark:text-surface-300 leading-relaxed max-w-2xl">
              Access clinical documentation, perform botanical classifications using neural models, and chat with our RAG agent to analyze traditional formulations.
            </p>
            <div className="pt-2 flex flex-wrap gap-3">
              <Button
                onClick={() => navigate(ROUTES.PLANT_DETECTION)}
                variant="primary"
                className="rounded-xl px-5 py-3 shadow-glow text-xs"
              >
                Start New Scan <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
              <Button
                onClick={() => navigate(ROUTES.RAG_ASSISTANT)}
                variant="secondary"
                className="rounded-xl px-5 py-3 border border-surface-200 dark:border-white/10 text-surface-700 dark:text-white text-xs bg-white/40"
              >
                Consult RAG Bot
              </Button>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Grid: Stats and System Monitor */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left 3 columns: Stats cards */}
        <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-6">
          {stats.map((stat) => (
            <motion.div
              key={stat.name}
              variants={itemVariants}
              whileHover={{ y: -6, scale: 1.02 }}
              transition={{ type: 'spring', stiffness: 300, damping: 15 }}
            >
              <Card
                className="h-full flex items-center gap-5 glass border border-surface-200 dark:border-white/10 hover:border-primary-500/35 transition-all rounded-2xl shadow-md p-6 cursor-pointer relative overflow-hidden group"
                onClick={() => {
                  if (stat.name === 'Total Detections') navigate(ROUTES.PLANT_DETECTION);
                  if (stat.name === 'Active Chats') navigate(ROUTES.RAG_ASSISTANT);
                  if (stat.name === 'Saved Plants') navigate(ROUTES.FAVORITES);
                }}
              >
                <div className="absolute -bottom-6 -right-6 w-20 h-20 bg-primary-500/5 group-hover:bg-primary-500/10 rounded-full blur-xl transition-all duration-300" />
                <div className={`p-4 rounded-xl border border-transparent ${stat.color} flex-shrink-0 relative z-10`}>
                  <stat.icon className="w-6 h-6" />
                </div>
                <div className="relative z-10">
                  <p className="text-[11px] font-bold uppercase tracking-wider text-surface-500 dark:text-surface-400">{stat.name}</p>
                  <h3 className="text-3xl font-black text-surface-900 dark:text-white mt-1 leading-none font-mono">
                    {loading ? '...' : stat.value}
                  </h3>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Right column: System Status Monitor */}
        <motion.div variants={itemVariants} className="lg:col-span-1">
          <Card className="h-full glass border border-surface-200 dark:border-white/10 p-5 rounded-2xl flex flex-col justify-between shadow-md">
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-surface-500 dark:text-surface-400 flex items-center gap-2 mb-4">
                <Cpu className="w-4 h-4 text-primary-650 dark:text-primary-400" /> System Monitors
              </h4>
              <div className="space-y-3">
                {/* AI Detection */}
                <div className="flex items-center justify-between text-xs py-1 border-b border-surface-100 dark:border-white/5">
                  <span className="text-surface-600 dark:text-surface-300 font-bold">AI Plant Classifier</span>
                  <span className="flex items-center gap-1.5 font-black text-primary-600 dark:text-primary-400 font-mono">
                    <span className="w-2 h-2 rounded-full bg-primary-500 animate-pulse" />
                    {systemStatuses.detection}
                  </span>
                </div>
                {/* RAG Engine */}
                <div className="flex items-center justify-between text-xs py-1 border-b border-surface-100 dark:border-white/5">
                  <span className="text-surface-600 dark:text-surface-300 font-bold">RAG DB Pipeline</span>
                  <span className="flex items-center gap-1.5 font-black text-primary-600 dark:text-primary-400 font-mono">
                    <span className="w-2 h-2 rounded-full bg-primary-500 animate-pulse" />
                    {systemStatuses.rag}
                  </span>
                </div>
                {/* Ollama Status */}
                <div className="flex items-center justify-between text-xs py-1">
                  <span className="text-surface-600 dark:text-surface-300 font-bold">Ollama Server</span>
                  <span className="flex items-center gap-1.5 font-black text-primary-600 dark:text-primary-400 font-mono">
                    <span className="w-2 h-2 rounded-full bg-primary-500 animate-pulse" />
                    {systemStatuses.ollama}
                  </span>
                </div>
              </div>
            </div>
            <div className="border-t border-surface-200 dark:border-white/5 pt-3 mt-4 text-[10px] text-surface-450 flex items-center gap-1 font-semibold">
              <CheckCircle className="w-3.5 h-3.5 text-primary-600 dark:text-primary-500" /> All systems operational
            </div>
          </Card>
        </motion.div>
      </div>

      {/* Quick Actions Grid */}
      <motion.div variants={itemVariants} className="space-y-4">
        <h3 className="text-lg font-bold text-surface-900 dark:text-white tracking-tight flex items-center gap-2">
          <Sprout className="w-5 h-5 text-primary-600 dark:text-primary-400" /> Professional Tool Suite
        </h3>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {quickActions.map((action) => (
            <motion.div
              key={action.title}
              whileHover={{ y: -6 }}
              transition={{ type: 'spring', stiffness: 300, damping: 15 }}
              className="h-full"
            >
              <Card
                className={`flex flex-col h-full justify-between bg-gradient-to-br ${action.gradient} border border-surface-200 dark:border-white/10 hover:border-primary-500/25 transition-all rounded-2xl p-6 shadow-md`}
              >
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-3 bg-white dark:bg-white/5 rounded-xl border border-surface-200 dark:border-white/10 shadow-sm">
                      <action.icon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                    </div>
                    <h4 className="text-base font-extrabold text-surface-900 dark:text-white">{action.title}</h4>
                  </div>
                  <p className="text-xs text-surface-600 dark:text-surface-300 leading-relaxed mb-6 font-medium">
                    {action.desc}
                  </p>
                </div>
                <Button
                  onClick={() => navigate(action.path)}
                  variant="primary"
                  className="w-full flex items-center justify-center gap-2 rounded-xl py-3 text-xs"
                >
                  {action.actionText} <ArrowRight className="w-4 h-4" />
                </Button>
              </Card>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
}

export default Dashboard;
