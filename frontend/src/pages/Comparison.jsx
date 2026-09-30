import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeftRight, Search, Sprout, AlertTriangle, Info, Check, ChevronDown } from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import Card from '../components/common/Card';
import Loader from '../components/common/Loader';
import ErrorState from '../components/common/ErrorState';
import { getPlants } from '../api/plants';

export function Comparison() {
  const [allPlants, setAllPlants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Active selections
  const [plant1, setPlant1] = useState(null);
  const [plant2, setPlant2] = useState(null);

  // Dropdown states
  const [showDropdown1, setShowDropdown1] = useState(false);
  const [showDropdown2, setShowDropdown2] = useState(false);
  const [search1, setSearch1] = useState('');
  const [search2, setSearch2] = useState('');

  // Ref selectors
  const dropdownRef1 = useRef(null);
  const dropdownRef2 = useRef(null);

  // Load all plants from database catalog
  const loadPlantsList = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getPlants();
      const list = response.data || [];
      setAllPlants(list);
      
      if (list.length >= 2) {
        setPlant1(list[0]);
        setPlant2(list[1]);
      } else if (list.length === 1) {
        setPlant1(list[0]);
      }
    } catch (err) {
      console.error(err);
      setError('Could not load plant monographs list from backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPlantsList();
  }, []);

  // Click outside dropdown handler
  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef1.current && !dropdownRef1.current.contains(e.target)) {
        setShowDropdown1(false);
      }
      if (dropdownRef2.current && !dropdownRef2.current.contains(e.target)) {
        setShowDropdown2(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Filters
  const filteredPlants1 = allPlants.filter(
    (p) =>
      p.common_name.toLowerCase().includes(search1.toLowerCase()) ||
      p.scientific_name.toLowerCase().includes(search1.toLowerCase())
  );

  const filteredPlants2 = allPlants.filter(
    (p) =>
      p.common_name.toLowerCase().includes(search2.toLowerCase()) ||
      p.scientific_name.toLowerCase().includes(search2.toLowerCase())
  );

  // Compare helper to highlight differences
  const isDifferent = (val1, val2) => {
    if (!val1 && !val2) return false;
    return String(val1).trim().toLowerCase() !== String(val2).trim().toLowerCase();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[300px] relative z-10 w-full">
        <Loader className="w-8 h-8 text-primary-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="relative z-10 w-full">
        <ErrorState message={error} onRetry={loadPlantsList} />
      </div>
    );
  }

  return (
    <div className="space-y-6 relative z-10 w-full pb-10">
      <PageHeader
        title="Plant Comparison Matrix"
        description="Select two botanical species from the catalog to analyze family differences, prep variations, and warning profiles side-by-side."
      />

      {/* Comparison Selectors Panel */}
      <div className="flex flex-col md:flex-row items-center gap-4 glass p-5 rounded-2xl relative z-20">
        
        {/* Searchable Selector 1 */}
        <div ref={dropdownRef1} className="flex-1 w-full relative">
          <label className="text-[10px] font-bold text-surface-500 dark:text-surface-400 uppercase tracking-wider block mb-1.5 ml-1">Species 1</label>
          <button
            type="button"
            onClick={() => setShowDropdown1(!showDropdown1)}
            className="w-full text-left px-4 py-3 text-xs rounded-xl border border-surface-200 dark:border-white/10 bg-white dark:bg-white/5 text-surface-900 dark:text-white flex items-center justify-between hover:bg-surface-50 dark:hover:bg-white/10 transition-all focus:outline-none font-semibold"
          >
            <span className="truncate">
              {plant1 ? `${plant1.common_name} (${plant1.scientific_name})` : 'Select a species...'}
            </span>
            <ChevronDown className="w-4 h-4 text-surface-500 dark:text-surface-400 flex-shrink-0 ml-2" />
          </button>

          <AnimatePresence>
            {showDropdown1 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="absolute top-16 left-0 right-0 p-2 shadow-xl border border-surface-200 dark:border-white/10 bg-white/95 dark:bg-[#081c10]/95 backdrop-blur-md max-h-60 overflow-y-auto z-30 rounded-xl space-y-2"
              >
                <div className="flex items-center gap-2 px-2 py-1.5 bg-surface-50 dark:bg-black/20 rounded-lg border border-surface-200 dark:border-white/5">
                  <Search className="w-4 h-4 text-surface-400 dark:text-surface-350" />
                  <input
                    type="text"
                    placeholder="Search..."
                    value={search1}
                    onChange={(e) => setSearch1(e.target.value)}
                    className="w-full bg-transparent text-xs text-surface-900 dark:text-white placeholder-surface-400 dark:placeholder-surface-450 focus:outline-none"
                  />
                </div>
                <div className="space-y-0.5">
                  {filteredPlants1.length === 0 ? (
                    <div className="text-center text-xs text-surface-500 dark:text-surface-450 py-2">No matching results.</div>
                  ) : (
                    filteredPlants1.map((p) => (
                      <button
                        key={p.id}
                        onClick={() => {
                          setPlant1(p);
                          setShowDropdown1(false);
                          setSearch1('');
                        }}
                        className="flex items-center justify-between w-full text-left px-2.5 py-2 text-xs rounded-lg hover:bg-surface-50 dark:hover:bg-white/5 text-surface-700 dark:text-surface-200"
                      >
                        <span>{p.common_name} <span className="italic opacity-60 ml-1">({p.scientific_name})</span></span>
                        {plant1?.id === p.id && <Check className="w-3.5 h-3.5 text-primary-450" />}
                      </button>
                    ))
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <div className="p-3 bg-primary-500/10 rounded-full border border-primary-500/25 flex-shrink-0">
          <ArrowLeftRight className="w-5 h-5 text-primary-400 rotate-90 md:rotate-0" />
        </div>

        {/* Searchable Selector 2 */}
        <div ref={dropdownRef2} className="flex-1 w-full relative">
          <label className="text-[10px] font-bold text-surface-500 dark:text-surface-400 uppercase tracking-wider block mb-1.5 ml-1">Species 2</label>
          <button
            type="button"
            onClick={() => setShowDropdown2(!showDropdown2)}
            className="w-full text-left px-4 py-3 text-xs rounded-xl border border-surface-200 dark:border-white/10 bg-white dark:bg-white/5 text-surface-900 dark:text-white flex items-center justify-between hover:bg-surface-50 dark:hover:bg-white/10 transition-all focus:outline-none font-semibold"
          >
            <span className="truncate">
              {plant2 ? `${plant2.common_name} (${plant2.scientific_name})` : 'Select a species...'}
            </span>
            <ChevronDown className="w-4 h-4 text-surface-500 dark:text-surface-400 flex-shrink-0 ml-2" />
          </button>

          <AnimatePresence>
            {showDropdown2 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="absolute top-16 left-0 right-0 p-2 shadow-xl border border-surface-200 dark:border-white/10 bg-white/95 dark:bg-[#081c10]/95 backdrop-blur-md max-h-60 overflow-y-auto z-30 rounded-xl space-y-2"
              >
                <div className="flex items-center gap-2 px-2 py-1.5 bg-surface-50 dark:bg-black/20 rounded-lg border border-surface-200 dark:border-white/5">
                  <Search className="w-4 h-4 text-surface-400 dark:text-surface-350" />
                  <input
                    type="text"
                    placeholder="Search..."
                    value={search2}
                    onChange={(e) => setSearch2(e.target.value)}
                    className="w-full bg-transparent text-xs text-surface-900 dark:text-white placeholder-surface-400 dark:placeholder-surface-450 focus:outline-none"
                  />
                </div>
                <div className="space-y-0.5">
                  {filteredPlants2.length === 0 ? (
                    <div className="text-center text-xs text-surface-500 dark:text-surface-450 py-2">No matching results.</div>
                  ) : (
                    filteredPlants2.map((p) => (
                      <button
                        key={p.id}
                        onClick={() => {
                          setPlant2(p);
                          setShowDropdown2(false);
                          setSearch2('');
                        }}
                        className="flex items-center justify-between w-full text-left px-2.5 py-2 text-xs rounded-lg hover:bg-surface-50 dark:hover:bg-white/5 text-surface-700 dark:text-surface-200"
                      >
                        <span>{p.common_name} <span className="italic opacity-60 ml-1">({p.scientific_name})</span></span>
                        {plant2?.id === p.id && <Check className="w-3.5 h-3.5 text-primary-450" />}
                      </button>
                    ))
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

      </div>

      {/* Comparison Grid Board */}
      {!plant1 || !plant2 ? (
        <Card className="p-12 text-center border-dashed border-2 border-surface-300 dark:border-white/10 glass rounded-2xl">
          <Sprout className="w-12 h-12 text-surface-400 mx-auto mb-3" />
          <h4 className="font-bold text-surface-900 dark:text-white">Choose two plants above to begin comparison</h4>
        </Card>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4 relative z-10"
        >
          <Card className="glass overflow-hidden p-0 shadow-lg rounded-2xl">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse table-fixed min-w-[700px]">
                <thead>
                  <tr className="bg-surface-100 dark:bg-black/35 text-surface-900 dark:text-white border-b border-surface-200 dark:border-white/10">
                    <th className="px-6 py-4.5 text-[10px] font-bold uppercase tracking-wider text-surface-600 dark:text-surface-400 w-[20%]">Attribute</th>
                    <th className="px-6 py-4.5 text-sm font-extrabold text-primary-600 dark:text-primary-400 w-[40%] border-r border-surface-200 dark:border-white/10">
                      {plant1.common_name}
                    </th>
                    <th className="px-6 py-4.5 text-sm font-extrabold text-primary-600 dark:text-primary-400 w-[40%]">
                      {plant2.common_name}
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-200 dark:divide-white/5 text-xs text-surface-700 dark:text-surface-300">
                  {/* Scientific Name */}
                  <tr className={`transition-colors ${isDifferent(plant1.scientific_name, plant2.scientific_name) ? 'bg-primary-500/5' : ''}`}>
                    <td className="px-6 py-4 font-extrabold text-surface-500 dark:text-surface-400 uppercase text-[10px]">Scientific Name</td>
                    <td className="px-6 py-4 italic font-semibold border-r border-surface-200 dark:border-white/10 text-surface-900 dark:text-white">{plant1.scientific_name}</td>
                    <td className="px-6 py-4 italic font-semibold text-surface-900 dark:text-white">{plant2.scientific_name}</td>
                  </tr>

                  {/* Family */}
                  <tr className={`transition-colors ${isDifferent(plant1.family, plant2.family) ? 'bg-primary-500/5' : ''}`}>
                    <td className="px-6 py-4 font-extrabold text-surface-500 dark:text-surface-400 uppercase text-[10px]">Family</td>
                    <td className="px-6 py-4 border-r border-surface-200 dark:border-white/10 font-medium text-surface-900 dark:text-white">{plant1.family || 'N/A'}</td>
                    <td className="px-6 py-4 font-medium text-surface-900 dark:text-white">{plant2.family || 'N/A'}</td>
                  </tr>

                  {/* Description */}
                  <tr className={`transition-colors ${isDifferent(plant1.description, plant2.description) ? 'bg-primary-500/5' : ''}`}>
                    <td className="px-6 py-4 font-extrabold text-surface-500 dark:text-surface-400 uppercase text-[10px]">Description</td>
                    <td className="px-6 py-4 border-r border-surface-200 dark:border-white/10 leading-relaxed text-surface-800 dark:text-surface-200">{plant1.description || 'N/A'}</td>
                    <td className="px-6 py-4 leading-relaxed text-surface-800 dark:text-surface-200">{plant2.description || 'N/A'}</td>
                  </tr>

                  {/* Medicinal Uses */}
                  <tr className={`transition-colors ${isDifferent(plant1.medicinal_uses, plant2.medicinal_uses) ? 'bg-primary-500/5' : ''}`}>
                    <td className="px-6 py-4 font-extrabold text-surface-500 dark:text-surface-400 uppercase text-[10px]">Medicinal Uses</td>
                    <td className="px-6 py-4 border-r border-surface-200 dark:border-white/10 leading-relaxed text-surface-800 dark:text-surface-200">{plant1.medicinal_uses || 'N/A'}</td>
                    <td className="px-6 py-4 leading-relaxed text-surface-800 dark:text-surface-200">{plant2.medicinal_uses || 'N/A'}</td>
                  </tr>

                  {/* Habitat */}
                  <tr className={`transition-colors ${isDifferent(plant1.habitat, plant2.habitat) ? 'bg-primary-500/5' : ''}`}>
                    <td className="px-6 py-4 font-extrabold text-surface-500 dark:text-surface-400 uppercase text-[10px]">Habitat</td>
                    <td className="px-6 py-4 border-r border-surface-200 dark:border-white/10 leading-relaxed text-surface-800 dark:text-surface-200">{plant1.habitat || 'N/A'}</td>
                    <td className="px-6 py-4 leading-relaxed text-surface-800 dark:text-surface-200">{plant2.habitat || 'N/A'}</td>
                  </tr>

                  {/* Preparation Methods */}
                  <tr className={`transition-colors ${isDifferent(plant1.preparation_methods, plant2.preparation_methods) ? 'bg-primary-500/5' : ''}`}>
                    <td className="px-6 py-4 font-extrabold text-surface-500 dark:text-surface-400 uppercase text-[10px]">Preparation</td>
                    <td className="px-6 py-4 border-r border-surface-200 dark:border-white/10 leading-relaxed text-surface-800 dark:text-surface-200">{plant1.preparation_methods || 'N/A'}</td>
                    <td className="px-6 py-4 leading-relaxed text-surface-800 dark:text-surface-200">{plant2.preparation_methods || 'N/A'}</td>
                  </tr>

                  {/* Precautions (Danger alerts) */}
                  <tr className="bg-red-500/5 dark:bg-red-500/10 border-t border-surface-200 dark:border-white/10">
                    <td className="px-6 py-4.5 font-bold text-red-600 dark:text-red-400 uppercase text-[10px] flex items-center gap-1.5">
                      <AlertTriangle className="w-4 h-4 text-red-500 dark:text-red-400 flex-shrink-0 animate-pulse" />
                      Warnings
                    </td>
                    <td className="px-6 py-4.5 border-r border-surface-200 dark:border-white/10 leading-relaxed text-red-800 dark:text-red-205 font-semibold">
                      {plant1.precautions || 'No precautions reported.'}
                    </td>
                    <td className="px-6 py-4.5 leading-relaxed text-red-800 dark:text-red-205 font-semibold">
                      {plant2.precautions || 'No precautions reported.'}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </Card>
          
          <div className="flex items-center gap-1.5 text-[10px] text-surface-500 dark:text-surface-400 px-2 font-semibold">
            <Info className="w-3.5 h-3.5 text-primary-500 dark:text-primary-400" /> Rows highlighted with green gradients indicate distinct plant attributes.
          </div>
        </motion.div>
      )}
    </div>
  );
}

export default Comparison;
