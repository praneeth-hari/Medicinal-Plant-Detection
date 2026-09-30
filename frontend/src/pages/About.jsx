/**
 * About Page
 */
import { Sprout } from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import Card from '../components/common/Card';

export function About() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="About MediPlant AI"
        description="Technical overview of the RAG pipeline and plant image detection system."
      />

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
          The pipeline uses MobileNetV3-Small for image classification, FAISS + all-MiniLM-L6-v2 for semantic
          retrieval, and Ollama (qwen2.5:3b) for grounded answer generation. All inference runs
          locally — no external API calls for the core RAG flow.
        </p>
      </Card>
    </div>
  );
}

export default About;
