/**
 * About Page
 */
import React from 'react';
import { Sprout, Scan, MessageSquare, BookOpen, ShieldCheck } from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import Card from '../components/common/Card';
import { useAuth } from '../hooks/useAuth';

const FEATURES = [
  {
    icon: Scan,
    title: 'Plant Detection',
    desc: 'Take or upload a photo of any medicinal plant leaf and get an instant identification.',
  },
  {
    icon: MessageSquare,
    title: 'Ask Anything',
    desc: 'Chat with our AI assistant to learn about uses, dosage, and benefits of any plant.',
  },
  {
    icon: BookOpen,
    title: 'Plant Library',
    desc: 'Browse a curated collection of Indian medicinal plants with detailed monographs.',
  },
  {
    icon: ShieldCheck,
    title: 'Safe & Private',
    desc: 'All processing happens locally. Your data never leaves your device.',
  },
];

export function About() {
  const { isDeveloper } = useAuth();

  return (
    <div className="space-y-6">
      <PageHeader
        title="About MediPlant AI"
        description={isDeveloper
          ? 'Technical overview of the RAG pipeline and plant image detection system.'
          : 'Your guide to identifying and learning about medicinal plants.'}
      />

      {isDeveloper ? (
        /* ── Developer view: technical detail ── */
        <Card className="bg-white dark:bg-surface-900 border-surface-200 dark:border-surface-800 space-y-4">
          <h3 className="text-lg font-bold text-surface-900 dark:text-white flex items-center gap-2">
            <Sprout className="w-5 h-5 text-primary-600" /> Project Objective
          </h3>
          <p className="text-sm leading-relaxed text-surface-600 dark:text-surface-400">
            MediPlant AI aims to democratize botanical knowledge by combining local deep learning models
            with advanced retrieval architectures. Users can instantly classify medicinal leaves using image uploads,
            and converse with a local knowledge base of curated plant monographs running on local infrastructure.
          </p>
          <p className="text-sm leading-relaxed text-surface-600 dark:text-surface-400">
            The pipeline uses ResNet-50 for image classification, ChromaDB + all-MiniLM-L6-v2 for semantic
            retrieval, and Groq (llama-3.1-8b-instant) for grounded answer generation. All inference runs
            offline — no external API calls for the core RAG flow.
          </p>
        </Card>
      ) : (
        /* ── Customer view: simple & friendly ── */
        <div className="space-y-6">
          <Card className="bg-white dark:bg-surface-900 border-surface-200 dark:border-surface-800 space-y-3">
            <h3 className="text-lg font-bold text-surface-900 dark:text-white flex items-center gap-2">
              <Sprout className="w-5 h-5 text-primary-600" /> What is MediPlant AI?
            </h3>
            <p className="text-sm leading-relaxed text-surface-600 dark:text-surface-400">
              MediPlant AI helps you identify medicinal plants from photos and learn about their
              traditional uses, health benefits, and safety information — all in one place.
            </p>
            <p className="text-sm leading-relaxed text-surface-600 dark:text-surface-400">
              Whether you spotted a plant in your garden or want to know more about Ayurvedic herbs,
              just upload a photo or ask our assistant and get accurate, trusted answers instantly.
            </p>
          </Card>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {FEATURES.map(({ icon: Icon, title, desc }) => (
              <Card key={title} className="bg-white dark:bg-surface-900 border-surface-200 dark:border-surface-800 flex items-start gap-4">
                <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-primary-500/10 flex items-center justify-center">
                  <Icon className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="text-sm font-bold text-surface-900 dark:text-white">{title}</p>
                  <p className="text-xs text-surface-500 dark:text-surface-400 mt-1 leading-relaxed">{desc}</p>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default About;
