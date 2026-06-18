import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Moon, Sun, Cpu, Settings as SettingsIcon, User, Lock, Scan } from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import useTheme from '../hooks/useTheme';
import useToast from '../hooks/useToast';
import { useAuth } from '../hooks/useAuth';
import { changePassword } from '../api/auth';

const CHAT_TEMP_KEY        = 'mediplant_chat_temp';
const CHAT_TOKENS_KEY      = 'mediplant_chat_tokens';
const DETECT_THRESHOLD_KEY = 'mediplant_detect_threshold';
const DETECT_MAX_KEY       = 'mediplant_detect_max';

export function Settings() {
  const { setTheme, isDark } = useTheme();
  const { addToast } = useToast();
  const { user, isDeveloper } = useAuth();

  const [activeTab, setActiveTab] = useState('general');

  // AI settings
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens]     = useState(2048);

  // Detection preferences
  const [threshold, setThreshold] = useState(0.7);
  const [maxResults, setMaxResults] = useState(5);

  // Change password
  const [currentPw, setCurrentPw]   = useState('');
  const [newPw, setNewPw]           = useState('');
  const [confirmPw, setConfirmPw]   = useState('');
  const [pwLoading, setPwLoading]   = useState(false);

  useEffect(() => {
    const temp = localStorage.getItem(CHAT_TEMP_KEY);
    if (temp) setTemperature(parseFloat(temp));

    const tokens = localStorage.getItem(CHAT_TOKENS_KEY);
    if (tokens) setMaxTokens(parseInt(tokens, 10));

    const thresh = localStorage.getItem(DETECT_THRESHOLD_KEY);
    if (thresh) setThreshold(parseFloat(thresh));

    const maxR = localStorage.getItem(DETECT_MAX_KEY);
    if (maxR) setMaxResults(parseInt(maxR, 10));
  }, []);

  const handleSaveAI = (e) => {
    e.preventDefault();
    localStorage.setItem(CHAT_TEMP_KEY, temperature.toString());
    localStorage.setItem(CHAT_TOKENS_KEY, maxTokens.toString());
    addToast('AI settings saved!', 'success');
  };

  const handleSaveDetection = (e) => {
    e.preventDefault();
    localStorage.setItem(DETECT_THRESHOLD_KEY, threshold.toString());
    localStorage.setItem(DETECT_MAX_KEY, maxResults.toString());
    addToast('Detection preferences saved!', 'success');
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (newPw !== confirmPw) {
      addToast('New passwords do not match.', 'error');
      return;
    }
    setPwLoading(true);
    try {
      await changePassword(currentPw, newPw);
      addToast('Password changed successfully!', 'success');
      setCurrentPw(''); setNewPw(''); setConfirmPw('');
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Failed to change password.';
      addToast(msg, 'error');
    } finally {
      setPwLoading(false);
    }
  };

  const tabs = [
    { id: 'general',   label: 'General',   icon: SettingsIcon, devOnly: false },
    { id: 'ai',        label: 'AI & RAG',   icon: Cpu,          devOnly: true  },
    { id: 'detection', label: 'Detection',  icon: Scan,         devOnly: true  },
    { id: 'theme',     label: 'Theme',      icon: Sun,          devOnly: false },
  ].filter(t => !t.devOnly || isDeveloper);

  return (
    <div className="space-y-6 relative z-10 w-full pb-10">
      <PageHeader
        title="App Preferences"
        description="Manage your account, RAG configuration, detection thresholds, and visual theme."
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Tab Sidebar */}
        <Card className="lg:col-span-1 glass p-3 h-fit space-y-1.5 rounded-2xl shadow-lg">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2.5 w-full text-left px-3.5 py-3 rounded-xl text-xs font-bold transition-all ${
                  activeTab === tab.id
                    ? 'bg-primary-500/10 border border-primary-500/30 text-primary-750 dark:text-white shadow-glow-sm'
                    : 'text-surface-600 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-white/5 border border-transparent'
                }`}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                {tab.label}
              </button>
            );
          })}
        </Card>

        {/* Panels */}
        <Card className="lg:col-span-3 glass p-6 rounded-2xl shadow-lg">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
              className="space-y-6 min-h-[260px]"
            >
              {/* ── General: Account Info + Change Password ── */}
              {activeTab === 'general' && (
                <div className="space-y-6">
                  {/* Account Info */}
                  <div className="space-y-4">
                    <h3 className="text-sm font-extrabold text-surface-900 dark:text-white pb-3 border-b border-surface-200 dark:border-white/5 flex items-center gap-2">
                      <User className="w-4 h-4 text-primary-450" /> Account Info
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="space-y-1">
                        <p className="text-[10px] uppercase font-bold text-surface-400 tracking-wider">Username</p>
                        <p className="text-sm font-semibold text-surface-800 dark:text-white">{user?.username || '—'}</p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-[10px] uppercase font-bold text-surface-400 tracking-wider">Email</p>
                        <p className="text-sm font-semibold text-surface-800 dark:text-white">{user?.email || '—'}</p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-[10px] uppercase font-bold text-surface-400 tracking-wider">Role</p>
                        <span className={`inline-block text-xs font-bold px-2.5 py-1 rounded-full ${
                          isDeveloper
                            ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400'
                            : 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
                        }`}>
                          {isDeveloper ? 'Developer' : 'Customer'}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Change Password */}
                  <form onSubmit={handleChangePassword} className="space-y-4">
                    <h3 className="text-sm font-extrabold text-surface-900 dark:text-white pb-3 border-b border-surface-200 dark:border-white/5 flex items-center gap-2">
                      <Lock className="w-4 h-4 text-primary-450" /> Change Password
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <Input
                        label="Current Password"
                        type="password"
                        value={currentPw}
                        onChange={(e) => setCurrentPw(e.target.value)}
                        required
                        className="text-surface-900 dark:text-white text-xs"
                      />
                      <Input
                        label="New Password"
                        type="password"
                        value={newPw}
                        onChange={(e) => setNewPw(e.target.value)}
                        required
                        className="text-surface-900 dark:text-white text-xs"
                      />
                      <Input
                        label="Confirm New Password"
                        type="password"
                        value={confirmPw}
                        onChange={(e) => setConfirmPw(e.target.value)}
                        required
                        className="text-surface-900 dark:text-white text-xs"
                      />
                    </div>
                    <div className="flex justify-end">
                      <Button type="submit" variant="primary" className="rounded-xl px-6" disabled={pwLoading}>
                        {pwLoading ? 'Saving…' : 'Update Password'}
                      </Button>
                    </div>
                  </form>
                </div>
              )}

              {/* ── AI & RAG ── */}
              {activeTab === 'ai' && (
                <form onSubmit={handleSaveAI} className="space-y-5">
                  <h3 className="text-sm font-extrabold text-surface-900 dark:text-white pb-3 border-b border-surface-200 dark:border-white/5 flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-primary-450" /> AI & RAG Metrics
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-xs font-bold uppercase tracking-wider text-surface-500 dark:text-surface-400">
                        Temperature ({temperature})
                      </label>
                      <input
                        type="range" min="0" max="1.2" step="0.1"
                        value={temperature}
                        onChange={(e) => setTemperature(parseFloat(e.target.value))}
                        className="w-full h-1.5 bg-surface-200 dark:bg-black/40 rounded-lg appearance-none cursor-pointer accent-primary-500"
                      />
                      <p className="text-[10px] text-surface-500 dark:text-surface-450 leading-relaxed font-semibold">
                        Lower = more factual. Higher = more creative responses.
                      </p>
                    </div>
                    <Input
                      label="Maximum Answer Tokens"
                      type="number" min="128" max="4096" step="64"
                      value={maxTokens}
                      onChange={(e) => setMaxTokens(parseInt(e.target.value, 10))}
                      required
                      className="text-surface-900 dark:text-white font-mono text-xs"
                    />
                  </div>
                  <div className="flex justify-end pt-2">
                    <Button type="submit" variant="primary" className="rounded-xl px-6 shadow-glow">Save</Button>
                  </div>
                </form>
              )}

              {/* ── Detection Preferences ── */}
              {activeTab === 'detection' && (
                <form onSubmit={handleSaveDetection} className="space-y-5">
                  <h3 className="text-sm font-extrabold text-surface-900 dark:text-white pb-3 border-b border-surface-200 dark:border-white/5 flex items-center gap-2">
                    <Scan className="w-4 h-4 text-primary-450" /> Detection Preferences
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-xs font-bold uppercase tracking-wider text-surface-500 dark:text-surface-400">
                        Confidence Threshold ({Math.round(threshold * 100)}%)
                      </label>
                      <input
                        type="range" min="0.3" max="0.99" step="0.01"
                        value={threshold}
                        onChange={(e) => setThreshold(parseFloat(e.target.value))}
                        className="w-full h-1.5 bg-surface-200 dark:bg-black/40 rounded-lg appearance-none cursor-pointer accent-primary-500"
                      />
                      <p className="text-[10px] text-surface-500 dark:text-surface-450 leading-relaxed font-semibold">
                        Minimum confidence required to show a detection result.
                      </p>
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-bold uppercase tracking-wider text-surface-500 dark:text-surface-400">
                        Max Top Results ({maxResults})
                      </label>
                      <input
                        type="range" min="1" max="10" step="1"
                        value={maxResults}
                        onChange={(e) => setMaxResults(parseInt(e.target.value, 10))}
                        className="w-full h-1.5 bg-surface-200 dark:bg-black/40 rounded-lg appearance-none cursor-pointer accent-primary-500"
                      />
                      <p className="text-[10px] text-surface-500 dark:text-surface-450 leading-relaxed font-semibold">
                        Number of top predictions to display per detection.
                      </p>
                    </div>
                  </div>
                  <div className="flex justify-end pt-2">
                    <Button type="submit" variant="primary" className="rounded-xl px-6 shadow-glow">Save</Button>
                  </div>
                </form>
              )}

              {/* ── Theme ── */}
              {activeTab === 'theme' && (
                <div className="space-y-5">
                  <h3 className="text-sm font-extrabold text-surface-900 dark:text-white pb-3 border-b border-surface-200 dark:border-white/5 flex items-center gap-2">
                    <Sun className="w-4 h-4 text-primary-450" /> Visual Styling
                  </h3>
                  <div className="space-y-2">
                    <label className="text-xs font-bold uppercase tracking-wider text-surface-500 dark:text-surface-400">Application Mode</label>
                    <div className="grid grid-cols-2 gap-3 max-w-sm">
                      <button
                        type="button"
                        onClick={() => setTheme('light')}
                        className={`flex items-center justify-center gap-2 py-3 px-4 rounded-xl border text-xs font-extrabold transition-all ${
                          !isDark
                            ? 'bg-primary-500/15 border-primary-500/35 text-primary-700 dark:text-white shadow-glow-sm'
                            : 'border-surface-200 bg-surface-50 text-surface-600 hover:bg-surface-100 dark:border-white/10 dark:bg-white/5 dark:text-surface-300 dark:hover:bg-white/10'
                        }`}
                      >
                        <Sun className="w-4 h-4 text-amber-500" /> Light Mode
                      </button>
                      <button
                        type="button"
                        onClick={() => setTheme('dark')}
                        className={`flex items-center justify-center gap-2 py-3 px-4 rounded-xl border text-xs font-extrabold transition-all ${
                          isDark
                            ? 'bg-primary-500/15 border-primary-500/35 text-primary-700 dark:text-white shadow-glow-sm'
                            : 'border-white/10 bg-white/5 text-surface-300 hover:bg-white/10'
                        }`}
                      >
                        <Moon className="w-4 h-4 text-primary-400" /> Dark Mode
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </Card>
      </div>
    </div>
  );
}

export default Settings;
