/**
 * Favorites Page
 * ==============
 *
 * Displays medicinal plant monographs bookmarked by the user, persisted in localStorage.
 * Supports toggling between Grid and List layouts, and immediate unfavoriting.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Heart, Sprout, LayoutGrid, List } from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Loader from '../components/common/Loader';
import EmptyState from '../components/common/EmptyState';
import { getPlants } from '../api/plants';
import useToast from '../hooks/useToast';

const FAVORITES_KEY = 'mediplant_favorites';

export function Favorites() {
  const navigate = useNavigate();
  const { addToast } = useToast();

  // States
  const [favoriteIds, setFavoriteIds] = useState([]);
  const [favoritePlants, setFavoritePlants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isGridView, setIsGridView] = useState(true);

  // Load favorite IDs from localStorage
  const loadFavorites = () => {
    const stored = localStorage.getItem(FAVORITES_KEY);
    if (stored) {
      try {
        return JSON.parse(stored);
      } catch (e) {
        console.error('Failed to parse favorites', e);
      }
    }
    return [];
  };

  const fetchFavoritesData = async () => {
    setLoading(true);
    const ids = loadFavorites();
    setFavoriteIds(ids);

    if (ids.length === 0) {
      setFavoritePlants([]);
      setLoading(false);
      return;
    }

    try {
      const response = await getPlants();
      const allPlants = response.data || [];
      const filtered = allPlants.filter((p) => ids.includes(p.id));
      setFavoritePlants(filtered);
    } catch (err) {
      console.error(err);
      addToast('Failed to load favorites list data.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFavoritesData();
  }, []);

  // Remove a plant from favorites list
  const handleRemoveFavorite = (plantId, name) => {
    const updatedIds = favoriteIds.filter((id) => id !== plantId);
    setFavoriteIds(updatedIds);
    localStorage.setItem(FAVORITES_KEY, JSON.stringify(updatedIds));
    setFavoritePlants((prev) => prev.filter((p) => p.id !== plantId));
    addToast(`${name} removed from favorites.`, 'info');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[300px]">
        <Loader className="w-8 h-8 text-primary-650" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Saved Favorites"
        description="Access your quick-reference list of starred medicinal plant monographs."
        actions={
          favoritePlants.length > 0 && (
            <div className="flex bg-surface-100 dark:bg-surface-900 p-1 rounded-lg border border-surface-200 dark:border-white/10">
              <button
                onClick={() => setIsGridView(true)}
                className={`p-1.5 rounded-md transition-colors ${
                  isGridView
                    ? 'bg-white dark:bg-surface-800 text-primary-600 shadow-sm'
                    : 'text-surface-500 dark:text-surface-400 hover:text-surface-600'
                }`}
                aria-label="Grid view"
              >
                <LayoutGrid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsGridView(false)}
                className={`p-1.5 rounded-md transition-colors ${
                  !isGridView
                    ? 'bg-white dark:bg-surface-800 text-primary-600 shadow-sm'
                    : 'text-surface-500 dark:text-surface-400 hover:text-surface-600'
                }`}
                aria-label="List view"
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          )
        }
      />

      {favoritePlants.length === 0 ? (
        <EmptyState
          title="No favorite plants"
          description="Star medicinal plants in the catalog to add them to your bookmarks for quick offline access."
          icon={Heart}
          actionText="Browse Plant Catalog"
          onAction={() => navigate('/plants')}
        />
      ) : isGridView ? (
        // Grid Layout View
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {favoritePlants.map((plant) => (
            <Card
              key={plant.id}
              className="flex flex-col justify-between h-full cursor-pointer relative group p-5 shadow-sm hover:shadow-glow-sm"
            >
              <div>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="p-2 bg-primary-500/10 rounded-lg text-primary-600">
                      <Sprout className="w-4 h-4" />
                    </div>
                    <h4 className="text-base font-extrabold text-surface-900 dark:text-white truncate max-w-[180px]">
                      {plant.common_name}
                    </h4>
                  </div>
                  <button
                    onClick={() => handleRemoveFavorite(plant.id, plant.common_name)}
                    className="text-red-500 hover:scale-110 transition-transform p-1"
                    aria-label="Remove favorite"
                  >
                    <Heart className="w-5 h-5 fill-current" />
                  </button>
                </div>
                <p className="text-xs italic text-surface-500 dark:text-surface-400 mb-4 truncate font-medium">{plant.scientific_name}</p>
                <p className="text-sm text-surface-600 dark:text-surface-400 line-clamp-3 leading-relaxed mb-6">
                  {plant.medicinal_uses || plant.therapeutic_uses || plant.description || 'No details available.'}
                </p>
              </div>
              <Button
                onClick={() => navigate(`/plants/${plant.id}`)}
                variant="secondary"
                className="w-full mt-auto rounded-xl py-2 px-3"
              >
                Open Monograph
              </Button>
            </Card>
          ))}
        </div>
      ) : (
        // List Layout View
        <div className="space-y-4">
          {favoritePlants.map((plant) => (
            <Card
              key={plant.id}
              className="flex items-center justify-between p-4 rounded-xl shadow-sm hover:shadow-glow-sm transition-all duration-300 card-hover"
            >
              <div className="flex items-center gap-4 min-w-0 flex-1">
                <div className="p-2.5 bg-primary-500/10 text-primary-600 rounded-lg flex-shrink-0">
                  <Sprout className="w-5 h-5" />
                </div>
                <div className="min-w-0">
                  <h4 className="text-sm font-extrabold text-surface-900 dark:text-white truncate">
                    {plant.common_name}{' '}
                    <span className="text-xs font-medium italic text-surface-500 dark:text-surface-400 ml-1">
                      ({plant.scientific_name})
                    </span>
                  </h4>
                  <p className="text-xs text-surface-600 dark:text-surface-400 truncate mt-0.5 max-w-xl">
                    {plant.medicinal_uses || plant.therapeutic_uses || plant.description}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-4 ml-4">
                <Button
                  onClick={() => navigate(`/plants/${plant.id}`)}
                  variant="secondary"
                  size="sm"
                  className="rounded-lg py-1.5 px-3"
                >
                  View Detail
                </Button>
                <button
                  onClick={() => handleRemoveFavorite(plant.id, plant.common_name)}
                  className="text-red-500 hover:scale-110 transition-transform p-1"
                  aria-label="Remove favorite"
                >
                  <Heart className="w-5 h-5 fill-current" />
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

export default Favorites;
