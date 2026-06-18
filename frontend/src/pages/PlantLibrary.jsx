import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Sprout, Search, Heart, ArrowRight } from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import Card from '../components/common/Card';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import Loader from '../components/common/Loader';
import ErrorState from '../components/common/ErrorState';
import { getPlants, searchPlants } from '../api/plants';
import useToast from '../hooks/useToast';
import config from '../config/config';

const FAVORITES_KEY = 'mediplant_favorites';

export function PlantLibrary() {
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [plants, setPlants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [favorites, setFavorites] = useState([]);

  // Load favorites list
  useEffect(() => {
    const stored = localStorage.getItem(FAVORITES_KEY);
    if (stored) {
      try {
        setFavorites(JSON.parse(stored));
      } catch (e) {
        console.error(e);
      }
    }
  }, []);

  const loadPlants = async (query = '') => {
    setLoading(true);
    setError(null);
    try {
      let data;
      if (query) {
        data = await searchPlants(query);
      } else {
        const response = await getPlants();
        data = response.data;
      }
      setPlants(data || []);
    } catch (err) {
      console.error(err);
      setError('Could not load plant monographs from the server.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPlants();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadPlants(searchQuery);
  };

  // Toggle favorite bookmark state
  const handleToggleFavorite = (e, plantId, name) => {
    e.stopPropagation();
    let updated;
    if (favorites.includes(plantId)) {
      updated = favorites.filter((id) => id !== plantId);
      addToast(`${name} removed from favorites.`, 'info');
    } else {
      updated = [...favorites, plantId];
      addToast(`${name} bookmarked as favorite!`, 'success');
    }
    setFavorites(updated);
    localStorage.setItem(FAVORITES_KEY, JSON.stringify(updated));
  };

  // Get plant image URL or fallback to high-quality unsplash botanical placeholders
  const getPlantImage = (plant) => {
    if (plant.image_url) {
      if (plant.image_url.startsWith('http') || plant.image_url.startsWith('/')) {
        return plant.image_url;
      }
      const base = config.API_URL.replace('/api/v1', '');
      return `${base}/${plant.image_url.replace(/\\/g, '/')}`;
    }
    const fallbacks = [
      'https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?q=80&w=400&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1512428559087-560fa5ceab42?q=80&w=400&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1502082553048-f009c37129b9?q=80&w=400&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1530968033775-2c92736b1c1e?q=80&w=400&auto=format&fit=crop',
    ];
    return fallbacks[plant.id % fallbacks.length];
  };

  return (
    <div className="space-y-8 relative z-10 w-full">
      <PageHeader
        title="Botanical Monograph Library"
        description="Search or browse our verified registry of medicinal plant records and clinical preparation standards."
      />

      {/* Search Input Bar */}
      <form onSubmit={handleSearchSubmit} className="flex gap-2 max-w-md glass border border-surface-200 dark:border-white/10 p-1.5 rounded-2xl shadow-md">
        <Input
          placeholder="Search common or scientific name..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 border-none focus:ring-0 bg-transparent text-surface-900 dark:text-white placeholder-surface-400 dark:placeholder-surface-450 text-xs"
        />
        <Button type="submit" variant="primary" className="rounded-xl shadow-glow py-2 text-xs">
          <Search className="w-4 h-4" />
        </Button>
      </form>

      {/* Grid listing */}
      {loading ? (
        <div className="flex items-center justify-center min-h-[250px]">
          <Loader className="w-8 h-8 text-primary-500" />
        </div>
      ) : error ? (
        <ErrorState message={error} onRetry={() => loadPlants(searchQuery)} />
      ) : plants.length === 0 ? (
        <Card className="text-center p-12 border-dashed border-2 border-surface-200 dark:border-white/10 glass rounded-2xl">
          <Sprout className="w-12 h-12 text-surface-400 mx-auto mb-3" />
          <h4 className="font-bold text-surface-900 dark:text-white">No monographs match your query.</h4>
          <Button onClick={() => { setSearchQuery(''); loadPlants(''); }} variant="secondary" className="mt-4 text-xs text-white">
            Reset Filters
          </Button>
        </Card>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {plants.map((plant) => {
            const isFavorited = favorites.includes(plant.id);
            return (
              <motion.div
                key={plant.id}
                whileHover={{ y: -6 }}
                transition={{ type: 'spring', stiffness: 300, damping: 18 }}
              >
                <Card
                  onClick={() => navigate(`/plants/${plant.id}`)}
                  className="flex flex-col h-full bg-white border border-surface-200 dark:border-white/10 hover:border-primary-500/35 transition-all rounded-2xl overflow-hidden cursor-pointer relative group shadow-md p-0"
                >
                  {/* Large Card Image */}
                  <div className="relative aspect-video w-full overflow-hidden bg-black/5 dark:bg-black/40 border-b border-surface-200 dark:border-white/10">
                    <img
                      src={getPlantImage(plant)}
                      alt={plant.common_name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                    
                    <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent opacity-60" />

                    {/* Bookmark Button */}
                    <button
                      onClick={(e) => handleToggleFavorite(e, plant.id, plant.common_name)}
                      className="absolute top-3 right-3 p-2 bg-black/40 hover:bg-black/60 rounded-full border border-white/10 text-white backdrop-blur-md transition-all active:scale-95 z-20"
                      aria-label={isFavorited ? "Remove from favorites" : "Add to favorites"}
                    >
                      <Heart className={`w-4 h-4 transition-colors ${isFavorited ? 'fill-red-500 text-red-500' : 'text-surface-300 hover:text-red-400'}`} />
                    </button>

                    {/* Quick Family Tag */}
                    {plant.family && (
                      <span className="absolute bottom-3 left-3 text-[10px] bg-primary-500/20 border border-primary-500/30 text-primary-600 dark:text-primary-300 px-2 py-0.5 rounded-full font-bold backdrop-blur-md uppercase tracking-wider">
                        {plant.family}
                      </span>
                    )}
                  </div>

                  {/* Body Content */}
                  <div className="p-5 flex flex-col justify-between flex-1 space-y-4">
                    <div className="space-y-1.5">
                      <h4 className="text-base font-extrabold text-surface-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                        {plant.common_name}
                      </h4>
                      <p className="text-xs italic text-surface-600 dark:text-surface-300 font-semibold">{plant.scientific_name}</p>
                      <p className="text-xs text-surface-550 dark:text-surface-400 line-clamp-3 leading-relaxed pt-1.5 font-medium">
                        {plant.medicinal_uses || plant.description || 'No medicinal profile logs seeded.'}
                      </p>
                    </div>

                    <div className="text-xs font-bold text-primary-600 dark:text-primary-400 group-hover:text-primary-500 flex items-center justify-end gap-1 pt-2.5 border-t border-surface-150 dark:border-white/5">
                      Read Monograph <ArrowRight className="w-4.5 h-4.5 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </motion.div>
      )}
    </div>
  );
}

export default PlantLibrary;
