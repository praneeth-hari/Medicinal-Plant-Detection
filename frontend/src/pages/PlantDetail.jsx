import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sprout, ArrowLeft, ShieldAlert, Sparkles, BookOpen, Heart, Landmark, Globe, FileText, ArrowRight } from 'lucide-react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Loader from '../components/common/Loader';
import ErrorState from '../components/common/ErrorState';
import { getPlant } from '../api/plants';
import useToast from '../hooks/useToast';
import config from '../config/config';

const FAVORITES_KEY = 'mediplant_favorites';

export function PlantDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [plant, setPlant] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isFavorited, setIsFavorited] = useState(false);

  useEffect(() => {
    if (plant) {
      const stored = localStorage.getItem(FAVORITES_KEY);
      if (stored) {
        try {
          const ids = JSON.parse(stored);
          setIsFavorited(ids.includes(plant.id));
        } catch (e) {
          console.error(e);
        }
      }
    }
  }, [plant]);

  const loadPlantDetails = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getPlant(id);
      setPlant(response.data);
    } catch (err) {
      console.error(err);
      setError('Could not load plant monograph details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPlantDetails();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const handleToggleFavorite = () => {
    if (!plant) return;
    const stored = localStorage.getItem(FAVORITES_KEY);
    let ids = [];
    if (stored) {
      try {
        ids = JSON.parse(stored);
      } catch (e) {
        console.error(e);
      }
    }

    let updated;
    if (isFavorited) {
      updated = ids.filter((fid) => fid !== plant.id);
      setIsFavorited(false);
      addToast(`${plant.common_name} removed from favorites.`, 'info');
    } else {
      updated = [...ids, plant.id];
      setIsFavorited(true);
      addToast(`${plant.common_name} bookmarked as favorite!`, 'success');
    }
    localStorage.setItem(FAVORITES_KEY, JSON.stringify(updated));
  };

  // Get plant image URL or fallback to high-quality unsplash botanical placeholder
  const getPlantImage = (plant) => {
    if (plant.image_url) {
      if (plant.image_url.startsWith('http') || plant.image_url.startsWith('/')) {
        return plant.image_url;
      }
      const base = config.API_URL.replace('/api/v1', '');
      return `${base}/${plant.image_url.replace(/\\/g, '/')}`;
    }
    return 'https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?q=80&w=600&auto=format&fit=crop';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[300px] relative z-10 w-full">
        <Loader className="w-8 h-8 text-primary-500" />
      </div>
    );
  }

  if (error || !plant) {
    return (
      <div className="space-y-4 relative z-10 w-full">
        <Button onClick={() => navigate('/plants')} variant="secondary" className="flex items-center gap-1.5 rounded-xl text-xs text-white">
          <ArrowLeft className="w-4 h-4" /> Back to Catalog
        </Button>
        <ErrorState message={error || 'Plant not found'} onRetry={loadPlantDetails} />
      </div>
    );
  }

  return (
    <div className="space-y-6 relative z-10 w-full pb-10">
      {/* Back Button */}
      <button
        onClick={() => navigate('/plants')}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-primary-600 dark:text-primary-400 hover:bg-black/5 dark:hover:bg-white/5 transition-all"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Catalog
      </button>

      {/* Header Profile */}
      <div className="flex flex-col md:flex-row gap-6 items-start justify-between border-b border-surface-200 dark:border-white/10 pb-6">
        <div className="flex flex-col md:flex-row items-center gap-5 w-full md:w-auto">
          <div className="w-24 h-24 rounded-2xl overflow-hidden border border-surface-200 dark:border-white/10 shadow-md bg-black/5 dark:bg-black/40 flex-shrink-0">
            <img src={getPlantImage(plant)} alt={plant.common_name} className="w-full h-full object-cover" />
          </div>
          <div className="text-center md:text-left space-y-1">
            <span className="text-[10px] bg-primary-500/10 border border-primary-500/25 text-primary-600 dark:text-primary-400 px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider">
              {plant.family || 'Botanical Monograph'}
            </span>
            <h1 className="text-3xl md:text-4xl font-black text-surface-900 dark:text-white mt-1">
              {plant.common_name}
            </h1>
            <p className="text-sm italic text-surface-600 dark:text-surface-300 font-semibold">
              {plant.scientific_name}
            </p>
          </div>
        </div>

        <Button
          onClick={handleToggleFavorite}
          variant="secondary"
          className="w-full md:w-auto flex items-center justify-center gap-2 rounded-xl py-3 px-4 border border-surface-200 dark:border-white/10 text-surface-700 dark:text-white bg-white/40 text-xs"
        >
          <Heart className={`w-4 h-4 transition-colors ${isFavorited ? 'fill-red-500 text-red-500' : 'text-surface-400'}`} />
          <span className="text-xs font-bold">{isFavorited ? 'Saved in Favorites' : 'Save to Favorites'}</span>
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Stacked Glass Panels on Left */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Overview */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
          >
            <Card className="p-6 shadow-md leading-relaxed">
              <h3 className="text-xs font-bold uppercase tracking-wider text-surface-900 dark:text-white flex items-center gap-2.5 mb-4">
                <div className="p-2 bg-primary-500/10 text-primary-600 dark:text-primary-400 rounded-xl border border-primary-500/20">
                  <Sprout className="w-4.5 h-4.5" />
                </div>
                Botanical Description & Habitat
              </h3>
              <p className="text-xs text-surface-650 dark:text-surface-300 leading-relaxed font-medium">
                {plant.description || 'No botanical description available.'}
              </p>
            </Card>
          </motion.div>

          {/* Medicinal Uses */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="p-6 shadow-md leading-relaxed">
              <h3 className="text-xs font-bold uppercase tracking-wider text-surface-900 dark:text-white flex items-center gap-2.5 mb-4">
                <div className="p-2 bg-emerald-500/10 text-primary-650 dark:text-accent-400 rounded-xl border border-emerald-500/20">
                  <Sparkles className="w-4.5 h-4.5" />
                </div>
                Medicinal Uses & Therapeutic Value
              </h3>
              <p className="text-xs text-surface-650 dark:text-surface-300 leading-relaxed whitespace-pre-line font-medium">
                {plant.medicinal_uses || plant.therapeutic_uses || 'Information on therapeutic applications is not available.'}
              </p>
            </Card>
          </motion.div>

          {/* Preparation Methods */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
          >
            <Card className="p-6 shadow-md leading-relaxed">
              <h3 className="text-xs font-bold uppercase tracking-wider text-surface-900 dark:text-white flex items-center gap-2.5 mb-4">
                <div className="p-2 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-xl border border-emerald-500/20">
                  <BookOpen className="w-4.5 h-4.5" />
                </div>
                Preparation Methods & Dosages
              </h3>
              <p className="text-xs text-surface-650 dark:text-surface-300 leading-relaxed whitespace-pre-line font-medium">
                {plant.preparation_methods || 'Preparation guidelines not specified.'}
              </p>
            </Card>
          </motion.div>

          {/* Research References (Linked directly to literature page) */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="p-6 shadow-md leading-relaxed bg-gradient-to-br from-primary-500/[0.02] dark:from-primary-950/10 to-transparent">
              <h3 className="text-xs font-bold uppercase tracking-wider text-surface-900 dark:text-white flex items-center gap-2.5 mb-4">
                <div className="p-2 bg-white/40 dark:bg-white/5 text-primary-600 dark:text-primary-400 rounded-xl border border-surface-200 dark:border-white/10">
                  <FileText className="w-4.5 h-4.5" />
                </div>
                Research References & Clinical Papers
              </h3>
              <p className="text-xs text-surface-650 dark:text-surface-300 leading-relaxed mb-4 font-medium">
                Access external peer-reviewed publications, clinical trials, and toxicological index reviews indexed in the NCBI PubMed registry for this botanical species.
              </p>
              
              <div className="p-4 bg-white/40 dark:bg-black/40 border border-surface-200 dark:border-white/5 rounded-xl flex items-center justify-between">
                <div>
                  <h4 className="text-xs font-extrabold text-surface-900 dark:text-white">Search NCBI Database</h4>
                  <p className="text-[10px] text-surface-500 dark:text-surface-450 mt-0.5 font-bold">Lookup &quot;{plant.scientific_name}&quot;</p>
                </div>
                <Button
                  onClick={() => navigate(`/papers?q=${encodeURIComponent(plant.scientific_name)}`)}
                  variant="primary"
                  className="rounded-xl py-2 px-3 text-[10px] font-bold shadow-glow"
                >
                  Query Publications <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
                </Button>
              </div>
            </Card>
          </motion.div>
        </div>

        {/* Side panels on right */}
        <div className="lg:col-span-1 space-y-6">
          {/* Taxonomy Details */}
          <motion.div
            initial={{ opacity: 0, x: 15 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="p-6 shadow-md">
              <h3 className="text-xs font-bold uppercase tracking-wider text-surface-500 dark:text-surface-400 mb-4 border-b border-surface-200 dark:border-white/5 pb-2">Taxonomy Profile</h3>
              <ul className="text-xs space-y-3 font-bold">
                <li className="flex justify-between py-1.5 border-b border-surface-150 dark:border-white/5">
                  <span className="text-surface-500 flex items-center gap-1"><Landmark className="w-3.5 h-3.5" /> Family</span>
                  <span className="text-surface-900 dark:text-white font-mono">{plant.family || 'N/A'}</span>
                </li>
                <li className="flex justify-between py-1.5 border-b border-surface-150 dark:border-white/5">
                  <span className="text-surface-500 flex items-center gap-1"><Sprout className="w-3.5 h-3.5" /> Genus</span>
                  <span className="text-surface-900 dark:text-white italic">{plant.scientific_name?.split(' ')[0] || 'N/A'}</span>
                </li>
                <li className="flex justify-between py-1.5">
                  <span className="text-surface-500 flex items-center gap-1"><Globe className="w-3.5 h-3.5" /> Habitat</span>
                  <span className="text-surface-900 dark:text-white text-right truncate max-w-[120px]" title={plant.habitat}>{plant.habitat || 'N/A'}</span>
                </li>
              </ul>
            </Card>
          </motion.div>

          {/* Precautions / Warnings */}
          <motion.div
            initial={{ opacity: 0, x: 15 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.15 }}
          >
            <Card className="bg-red-50 dark:bg-red-500/5 border border-red-250 dark:border-red-500/20 text-red-800 dark:text-red-300 p-6 rounded-2xl shadow-md leading-relaxed">
              <h3 className="text-xs font-bold uppercase tracking-wider mb-4 flex items-center gap-2 text-red-750 dark:text-red-400">
                <div className="p-1.5 bg-red-100 dark:bg-red-500/10 text-red-600 dark:text-red-400 rounded-lg border border-red-200 dark:border-red-500/20">
                  <ShieldAlert className="w-4 h-4" />
                </div>
                Safety Warnings & Warnings
              </h3>
              <p className="text-[11px] font-semibold leading-relaxed">
                {plant.precautions || 'No precautions reported. Consult with professional herbal practitioners before using.'}
              </p>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

export default PlantDetail;
