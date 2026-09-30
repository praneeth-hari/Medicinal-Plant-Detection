/**
 * History Page
 * =====================
 */
import { useState, useEffect } from 'react';
import { History as Calendar } from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import Card from '../components/common/Card';
import { getDetectionHistory } from '../api/detection';
import { getSessions } from '../api/chat';
import Loader from '../components/common/Loader';

export function History() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchHistory() {
      try {
        const [detRes, chatRes] = await Promise.all([
          getDetectionHistory({ skip: 0, limit: 50 }).catch(() => ({ data: [] })),
          getSessions().catch(() => []),
        ]);

        const detections = (detRes.data || []).map((d) => ({
          type: 'Detection',
          item: d.plant_name || 'Unknown Plant',
          date: d.created_at ? new Date(d.created_at).toLocaleString() : '—',
          details: d.confidence ? `${Math.round(d.confidence * 100)}% confidence` : '—',
          linkPath: null,
        }));

        const chats = (chatRes || []).map((s) => ({
          type: 'Chat',
          item: s.title || 'Chat Session',
          date: s.created_at ? new Date(s.created_at).toLocaleString() : '—',
          details: `${s.message_count || 0} message(s)`,
          linkPath: null,
        }));

        // Combine and sort by date descending
        const combined = [...detections, ...chats].sort(
          (a, b) => new Date(b.date) - new Date(a.date)
        );
        setLogs(combined);
      } catch (err) {
        console.error('Failed to load history:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchHistory();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="History Log"
        description="Review your past plant identification uploads and conversation threads."
      />

      <Card className="bg-white dark:bg-surface-900 overflow-hidden p-0 border-surface-200 dark:border-surface-800">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader className="w-6 h-6 text-primary-500" />
          </div>
        ) : logs.length === 0 ? (
          <div className="text-center py-16 text-sm text-surface-500">
            No history found. Start by detecting a plant or chatting with the RAG assistant.
          </div>
        ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-surface-50 dark:bg-surface-950/40 text-surface-600 dark:text-surface-400 text-xs font-bold uppercase border-b border-surface-200 dark:border-surface-800">
                <th className="px-6 py-3">Type</th>
                <th className="px-6 py-3">Activity</th>
                <th className="px-6 py-3">Date</th>
                <th className="px-6 py-3">Status/Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-200 dark:divide-surface-800 text-sm">
              {logs.map((log, i) => (
                <tr key={i} className="hover:bg-surface-50/50 dark:hover:bg-surface-950/20">
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${
                      log.type === 'Detection'
                        ? 'bg-primary-50 text-primary-700 dark:bg-primary-950/20 dark:text-primary-400'
                        : 'bg-amber-50 text-amber-700 dark:bg-amber-950/20 dark:text-amber-400'
                    }`}>
                      {log.type}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-semibold text-surface-900 dark:text-white">{log.item}</td>
                  <td className="px-6 py-4 text-surface-500 flex items-center gap-1.5 mt-0.5">
                    <Calendar className="w-3.5 h-3.5" />
                    {log.date}
                  </td>
                  <td className="px-6 py-4 text-surface-600 dark:text-surface-400 font-medium">{log.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        )}
      </Card>
    </div>
  );
}

export default History;
