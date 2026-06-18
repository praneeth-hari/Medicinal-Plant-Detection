/**
 * History Page Scaffold
 * =====================
 */
import React from 'react';
import { History as HistoryIcon, Search, Calendar, Eye } from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import Card from '../components/common/Card';
import Button from '../components/common/Button';

export function History() {
  const logs = [
    { type: 'Detection', item: 'Tulsi Leaf Classification', date: '2026-06-03 14:10', details: '92% confidence' },
    { type: 'Chat', item: 'Question about Ashwagandha interactions', date: '2026-06-02 18:45', details: 'Session active' },
    { type: 'Detection', item: 'Neem Bark Classification', date: '2026-06-02 09:30', details: '88% confidence' },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="History Log"
        description="Review your past plant identification uploads and conversation threads."
      />

      <Card className="bg-white dark:bg-surface-900 overflow-hidden p-0 border-surface-200 dark:border-surface-800">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-surface-50 dark:bg-surface-950/40 text-surface-600 dark:text-surface-400 text-xs font-bold uppercase border-b border-surface-200 dark:border-surface-800">
                <th className="px-6 py-3">Type</th>
                <th className="px-6 py-3">Activity</th>
                <th className="px-6 py-3">Date</th>
                <th className="px-6 py-3">Status/Details</th>
                <th className="px-6 py-3 text-right">View</th>
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
                  <td className="px-6 py-4 text-right">
                    <Button variant="ghost" size="sm">
                      <Eye className="w-4 h-4 mr-1.5" /> Details
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

export default History;
