import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  UploadCloud,
  History,
  X,
  FileImage,
  AlertCircle,
  ArrowRight,
  ChevronLeft,
  ChevronRight,
  Image as ImageIcon,
  Sparkles,
  Camera,
  CameraOff,
  Circle,
} from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Loader from '../components/common/Loader';
import Modal from '../components/common/Modal';
import useToast from '../hooks/useToast';
import { detectPlant, getDetectionHistory } from '../api/detection';
import config from '../config/config';
import { getPlants } from '../api/plants';

export function PlantDetection() {
  const { addToast } = useToast();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const videoRef    = useRef(null);
  const streamRef   = useRef(null);

  // Webcam state
  const [inputMode, setInputMode]       = useState('upload'); // 'upload' | 'webcam'
  const [camActive, setCamActive]       = useState(false);
  const [camError, setCamError]         = useState('');

  // States for uploading
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [isDetecting, setIsDetecting] = useState(false);
  const [detectionResult, setDetectionResult] = useState(null);
  const [uploadError, setUploadError] = useState('');
  const [dragActive, setDragActive] = useState(false);

  // States for history
  const [historyList, setHistoryList] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState('');
  const [skip, setSkip] = useState(0);
  const limit = 4; // Page size for bottom slider
  const [catalogMap, setCatalogMap] = useState({}); // Matches plant names to catalog IDs

  // Modal details state
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [activeDetail, setActiveDetail] = useState(null);

  // Fetch catalog mapping so we can link results directly to detail monographs
  useEffect(() => {
    async function fetchCatalog() {
      try {
        const response = await getPlants();
        const mapping = {};
        if (response.data && Array.isArray(response.data)) {
          response.data.forEach((p) => {
            mapping[p.common_name.toLowerCase()] = p.id;
          });
        }
        setCatalogMap(mapping);
      } catch (err) {
        console.warn('Failed to fetch catalog mapping for navigation links:', err);
      }
    }
    fetchCatalog();
  }, []);

  // Fetch detection history
  const loadHistory = useCallback(async () => {
    setHistoryLoading(true);
    setHistoryError('');
    try {
      const response = await getDetectionHistory({ skip, limit });
      setHistoryList(response.data || []);
    } catch (err) {
      console.error(err);
      setHistoryError('Failed to retrieve history logs.');
    } finally {
      setHistoryLoading(false);
    }
  }, [skip]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  // File validations
  const validateFile = (file) => {
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
      return 'Invalid file type. Only JPG, JPEG, and PNG are allowed.';
    }
    const maxSize = 5 * 1024 * 1024; // 5 MB
    if (file.size > maxSize) {
      return 'File is too large. Max file size is 5MB.';
    }
    return '';
  };

  const handleFileChange = (file) => {
    if (!file) return;
    const error = validateFile(file);
    if (error) {
      setUploadError(error);
      addToast(error, 'error');
      return;
    }

    setUploadError('');
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setDetectionResult(null);
  };

  // Drag & Drop handlers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleRemoveImage = () => {
    setSelectedFile(null);
    setPreviewUrl('');
    setDetectionResult(null);
    setUploadError('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const startCamera = async () => {
    setCamError('');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      streamRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
      setCamActive(true);
    } catch {
      setCamError('Could not access camera. Please allow camera permission.');
    }
  };

  const stopCamera = () => {
    streamRef.current?.getTracks().forEach(t => t.stop());
    streamRef.current = null;
    setCamActive(false);
    setCamError('');
  };

  const switchMode = (mode) => {
    if (mode === inputMode) return;
    stopCamera();
    handleRemoveImage();
    setInputMode(mode);
    if (mode === 'webcam') setTimeout(startCamera, 100);
  };

  const capturePhoto = () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width  = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    canvas.toBlob((blob) => {
      if (!blob) return;
      const file = new File([blob], 'webcam-capture.jpg', { type: 'image/jpeg' });
      stopCamera();
      setInputMode('upload');
      handleFileChange(file);
    }, 'image/jpeg', 0.92);
  };

  // Cleanup camera on unmount
  useEffect(() => () => stopCamera(), []);

  const handleUploadSubmit = async () => {
    if (!selectedFile) return;

    setIsDetecting(true);
    setUploadError('');
    try {
      const response = await detectPlant(selectedFile);
      setDetectionResult(response.data);
      addToast('Image analyzed successfully!', 'success');
      loadHistory();
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.message || 'Classification request failed.';
      setUploadError(detail);
      addToast(detail, 'error');
    } finally {
      setIsDetecting(false);
    }
  };

  // Normalize image paths
  const getAbsoluteImageUrl = (path) => {
    if (!path) return '';
    const normalized = path.replace(/\\/g, '/');
    const base = config.API_URL.replace('/api/v1', '');
    return `${base}/${normalized}`;
  };

  const getCatalogLink = (plantName) => {
    if (!plantName) return null;
    return catalogMap[plantName.toLowerCase()] || null;
  };

  const openDetails = (detection) => {
    setActiveDetail(detection);
    setDetailModalOpen(true);
  };

  return (
    <div className="space-y-8 relative z-10 w-full">
      <PageHeader
        title="AI Plant Classifier"
        description="Submit plant photos to classify botanical family species and obtain clinical monographs instantly."
      />

      {/* 3-Column Showcase Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Column 1: Upload Area */}
        <Card className="glass border border-surface-200 dark:border-white/10 p-6 rounded-2xl shadow-lg flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-surface-500 dark:text-surface-400 mb-4 flex items-center gap-1.5">
              <UploadCloud className="w-4 h-4 text-primary-600 dark:text-primary-400" /> 1. Input Source
            </h3>

            {/* Mode Toggle */}
            <div className="flex rounded-xl border border-surface-200 dark:border-white/10 overflow-hidden mb-4">
              <button
                onClick={() => switchMode('upload')}
                className={`flex-1 flex items-center justify-center gap-1.5 py-2 text-xs font-bold transition-all ${
                  inputMode === 'upload'
                    ? 'bg-primary-500/10 text-primary-700 dark:text-primary-400'
                    : 'text-surface-500 hover:bg-surface-100 dark:hover:bg-white/5'
                }`}
              >
                <UploadCloud className="w-3.5 h-3.5" /> Upload
              </button>
              <button
                onClick={() => switchMode('webcam')}
                className={`flex-1 flex items-center justify-center gap-1.5 py-2 text-xs font-bold transition-all ${
                  inputMode === 'webcam'
                    ? 'bg-primary-500/10 text-primary-700 dark:text-primary-400'
                    : 'text-surface-500 hover:bg-surface-100 dark:hover:bg-white/5'
                }`}
              >
                <Camera className="w-3.5 h-3.5" /> Webcam
              </button>
            </div>

            {/* Upload mode */}
            {inputMode === 'upload' && !selectedFile && (
              <div
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`flex flex-col items-center justify-center p-8 text-center border-2 border-dashed rounded-2xl cursor-pointer aspect-square transition-all duration-300 ${
                  dragActive
                    ? 'border-primary-500 bg-primary-500/10 shadow-glow'
                    : 'border-surface-200 dark:border-white/10 hover:border-primary-500/50 hover:bg-primary-500/5'
                }`}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={(e) => handleFileChange(e.target.files[0])}
                  className="hidden"
                  accept="image/jpeg,image/png,image/jpg"
                />
                <UploadCloud className="w-10 h-10 text-primary-600 dark:text-primary-400 mb-3 animate-bounce" />
                <h4 className="text-xs font-bold text-surface-900 dark:text-white mb-1">
                  Drag & Drop Leaf Photo
                </h4>
                <p className="text-[10px] text-surface-500 dark:text-surface-400 max-w-[180px] mx-auto mt-1 leading-relaxed">
                  Or click to browse. Supports JPG, PNG up to 5MB.
                </p>
              </div>
            )}

            {/* File selected */}
            {inputMode === 'upload' && selectedFile && (
              <div className="space-y-4">
                <div className="p-4 bg-white/50 dark:bg-white/5 border border-surface-200 dark:border-white/10 rounded-2xl flex items-center gap-3">
                  <div className="p-2.5 bg-primary-500/10 rounded-xl text-primary-600 dark:text-primary-400">
                    <FileImage className="w-5 h-5" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <h4 className="text-xs font-bold text-surface-900 dark:text-white truncate">{selectedFile.name}</h4>
                    <p className="text-[10px] text-surface-500 dark:text-surface-400">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                  </div>
                  <button
                    onClick={handleRemoveImage}
                    disabled={isDetecting}
                    className="p-1 rounded-lg hover:bg-black/5 dark:hover:bg-white/10 text-surface-450 hover:text-surface-900 dark:hover:text-white transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
                {uploadError && (
                  <div className="p-3 text-xs text-red-700 dark:text-red-400 bg-red-50 dark:bg-red-950/15 border border-red-200 dark:border-red-900/50 rounded-xl flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    <span>{uploadError}</span>
                  </div>
                )}
              </div>
            )}

            {/* Webcam mode */}
            {inputMode === 'webcam' && (
              <div className="space-y-3">
                <div className="relative rounded-2xl overflow-hidden border border-surface-200 dark:border-white/10 bg-black aspect-square flex items-center justify-center">
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full h-full object-cover"
                  />
                  {!camActive && (
                    <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 bg-black/60">
                      <CameraOff className="w-8 h-8 text-white/40" />
                      <p className="text-[10px] text-white/50 font-semibold">Camera off</p>
                    </div>
                  )}
                </div>
                {camError && (
                  <div className="p-3 text-xs text-red-700 dark:text-red-400 bg-red-50 dark:bg-red-950/15 border border-red-200 dark:border-red-900/50 rounded-xl flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    <span>{camError}</span>
                  </div>
                )}
                <div className="flex gap-2">
                  {!camActive ? (
                    <Button onClick={startCamera} variant="secondary" className="flex-1 py-2.5 text-xs">
                      <Camera className="w-3.5 h-3.5 mr-1.5" /> Start Camera
                    </Button>
                  ) : (
                    <>
                      <Button onClick={capturePhoto} variant="primary" className="flex-1 py-2.5 text-xs shadow-glow">
                        <Circle className="w-3.5 h-3.5 mr-1.5 fill-current" /> Capture
                      </Button>
                      <Button onClick={stopCamera} variant="secondary" className="py-2.5 px-3 text-xs">
                        <CameraOff className="w-3.5 h-3.5" />
                      </Button>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>

          {selectedFile && !detectionResult && (
            <div className="flex flex-col gap-2 pt-4">
              <Button
                onClick={handleUploadSubmit}
                variant="primary"
                isLoading={isDetecting}
                className="w-full py-3 shadow-glow text-xs"
              >
                Analyze Leaf Pattern
              </Button>
              <Button
                onClick={handleRemoveImage}
                variant="secondary"
                disabled={isDetecting}
                className="w-full py-3 text-xs"
              >
                Cancel
              </Button>
            </div>
          )}
        </Card>

        {/* Column 2: Image Preview */}
        <Card className="glass border border-surface-200 dark:border-white/10 p-6 rounded-2xl shadow-lg flex flex-col items-center justify-center min-h-[300px]">
          <h3 className="text-sm font-bold uppercase tracking-wider text-surface-500 dark:text-surface-400 mb-4 self-start flex items-center gap-1.5 w-full">
            <ImageIcon className="w-4 h-4 text-primary-600 dark:text-primary-400" /> 2. Image Preview
          </h3>
          
          <div className="relative w-full flex-1 rounded-2xl overflow-hidden border border-surface-200 dark:border-white/10 bg-black/5 dark:bg-black/30 backdrop-blur-sm flex items-center justify-center aspect-square">
            {previewUrl ? (
              <img
                src={previewUrl}
                alt="Uploaded Leaf Pattern"
                className="max-h-full max-w-full object-contain"
              />
            ) : (
              <div className="text-center space-y-2 p-6">
                <ImageIcon className="w-12 h-12 text-surface-400 mx-auto opacity-40" />
                <p className="text-xs text-surface-500 dark:text-surface-400 font-semibold">Waiting for image upload...</p>
              </div>
            )}
          </div>
        </Card>

        {/* Column 3: Results & Metrics */}
        <Card className="glass border border-surface-200 dark:border-white/10 p-6 rounded-2xl shadow-lg flex flex-col justify-between min-h-[300px]">
          <div className="h-full flex flex-col">
            <h3 className="text-sm font-bold uppercase tracking-wider text-surface-500 dark:text-surface-400 mb-4 flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-primary-650 dark:text-primary-400" /> 3. Classifier Output
            </h3>

            {isDetecting ? (
              <div className="flex-1 flex flex-col items-center justify-center py-10 space-y-4">
                <Loader className="w-8 h-8 text-primary-500" />
                <p className="text-xs text-surface-600 dark:text-surface-300 font-semibold">Extracting features...</p>
              </div>
            ) : detectionResult ? (
              <div className="space-y-6 flex-1 flex flex-col justify-between">
                <div className="space-y-4">
                  <div className="flex justify-between items-start border-b border-surface-200 dark:border-white/5 pb-4">
                    <div>
                      <span className="text-[10px] font-bold uppercase text-primary-600 dark:text-primary-400 tracking-wider">Top Match</span>
                      <h3 className="text-xl font-extrabold text-surface-900 dark:text-white mt-1">
                        {detectionResult.plant_name || 'Unknown Species'}
                      </h3>
                      <p className="text-xs italic text-surface-500 dark:text-surface-300 mt-0.5">
                        {detectionResult.scientific_name || 'N/A'}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-3xl font-black text-primary-600 dark:text-primary-400 font-mono">
                        {Math.round(detectionResult.confidence * 100)}%
                      </div>
                      <span className="text-[9px] text-surface-500 dark:text-surface-450 uppercase font-semibold">Match Score</span>
                    </div>
                  </div>

                  {/* Confidence breakdown progress bars */}
                  <div className="space-y-3.5">
                    {detectionResult.top_predictions?.slice(0, 3).map((pred, i) => (
                      <div key={i} className="space-y-1">
                        <div className="flex justify-between text-xs font-semibold">
                          <span className="text-surface-800 dark:text-surface-200">{pred.name}</span>
                          <span className="text-primary-600 dark:text-primary-400 font-mono">{Math.round(pred.confidence * 100)}%</span>
                        </div>
                        <div className="w-full bg-black/5 dark:bg-white/5 h-2 rounded-full overflow-hidden border border-surface-200 dark:border-white/5">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${pred.confidence * 100}%` }}
                            transition={{ duration: 0.8, ease: 'easeOut' }}
                            className="bg-gradient-to-r from-primary-500 to-accent-500 h-full rounded-full"
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex flex-col gap-2 pt-4 border-t border-surface-200 dark:border-white/5">
                  {getCatalogLink(detectionResult.plant_name) ? (
                    <Button
                      onClick={() => navigate(`/plants/${getCatalogLink(detectionResult.plant_name)}`)}
                      variant="primary"
                      className="w-full py-3 shadow-glow text-xs"
                    >
                      View Monograph File <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  ) : (
                    <Button disabled variant="primary" className="w-full py-3 text-xs">
                      Monograph Unavailable
                    </Button>
                  )}
                  <Button onClick={handleRemoveImage} variant="secondary" className="w-full py-3 text-xs">
                    Scan Next Leaf
                  </Button>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-6 space-y-2 opacity-50">
                <Sparkles className="w-10 h-10 text-surface-450" />
                <p className="text-xs text-surface-500 dark:text-surface-450 font-semibold max-w-[200px]">
                  Submit and run analysis to populate classifier results.
                </p>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Horizontal History Slider at Bottom */}
      <Card className="glass border border-surface-200 dark:border-white/10 p-6 rounded-2xl shadow-lg">
        <div className="flex items-center justify-between pb-4 border-b border-surface-200 dark:border-white/5 mb-5">
          <h3 className="text-xs font-bold uppercase tracking-wider text-surface-500 dark:text-surface-400 flex items-center gap-1.5">
            <History className="w-4 h-4 text-primary-600 dark:text-primary-400" /> Inference Registry
          </h3>
          <div className="flex gap-2">
            <button
              disabled={skip === 0}
              onClick={() => setSkip((prev) => Math.max(0, prev - limit))}
              className="p-1 rounded-lg hover:bg-black/5 dark:hover:bg-white/10 text-surface-500 hover:text-surface-900 dark:hover:text-white disabled:opacity-50 transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button
              disabled={historyList.length < limit}
              onClick={() => setSkip((prev) => prev + limit)}
              className="p-1 rounded-lg hover:bg-black/5 dark:hover:bg-white/10 text-surface-500 hover:text-surface-900 dark:hover:text-white disabled:opacity-50 transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>

        {historyLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader className="w-6 h-6 text-primary-500" />
          </div>
        ) : historyError ? (
          <div className="text-center py-6 text-xs text-red-500">{historyError}</div>
        ) : historyList.length === 0 ? (
          <p className="text-center text-xs text-surface-500 py-6">No entries in identification registry.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {historyList.map((item) => (
              <motion.div
                key={item.id}
                onClick={() => openDetails(item)}
                whileHover={{ scale: 1.02, y: -2 }}
                className="glass hover:bg-white/5 border border-surface-200 dark:border-white/5 hover:border-primary-500/20 p-3 rounded-xl flex items-center gap-3 cursor-pointer transition-all duration-300"
              >
                <div className="w-12 h-12 rounded-lg bg-black/5 dark:bg-black/40 overflow-hidden flex-shrink-0 flex items-center justify-center border border-surface-200 dark:border-white/5">
                  {item.image_path ? (
                    <img
                      src={getAbsoluteImageUrl(item.image_path)}
                      alt={item.plant_name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <FileImage className="w-4 h-4 text-surface-450" />
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex justify-between items-start gap-1">
                    <h4 className="text-xs font-bold text-surface-900 dark:text-white truncate">{item.plant_name || 'Unidentified'}</h4>
                    <span className="text-[10px] font-extrabold text-primary-600 dark:text-primary-400 font-mono">
                      {Math.round(item.confidence * 100)}%
                    </span>
                  </div>
                  <p className="text-[10px] text-surface-500 dark:text-surface-400 italic truncate">{item.scientific_name || 'N/A'}</p>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </Card>

      {/* History Detail Modal */}
      {activeDetail && (
        <Modal
          isOpen={detailModalOpen}
          onClose={() => setDetailModalOpen(false)}
          title={`Detection Record #${activeDetail.id}`}
          size="md"
          footer={
            <div className="flex gap-2 w-full">
              <Button onClick={() => setDetailModalOpen(false)} variant="secondary" className="flex-1 py-3 text-xs">
                Close
              </Button>
              {getCatalogLink(activeDetail.plant_name) && (
                <Button
                  onClick={() => {
                    setDetailModalOpen(false);
                    navigate(`/plants/${getCatalogLink(activeDetail.plant_name)}`);
                  }}
                  variant="primary"
                  className="flex-1 py-3 shadow-glow text-xs"
                >
                  View Catalog Monograph
                </Button>
              )}
            </div>
          }
        >
          <div className="space-y-4">
            <div className="relative rounded-xl overflow-hidden border border-surface-200 dark:border-white/10 bg-black/5 dark:bg-black/40 aspect-video flex items-center justify-center">
              <img
                src={getAbsoluteImageUrl(activeDetail.image_path)}
                alt={activeDetail.plant_name}
                className="max-h-full object-contain"
              />
            </div>

            <div className="flex justify-between items-start border-b border-surface-200 dark:border-white/5 pb-3">
              <div>
                <h4 className="text-base font-bold text-surface-900 dark:text-white">
                  {activeDetail.plant_name || 'Unidentified'}
                </h4>
                <p className="text-xs italic text-surface-500 dark:text-surface-300 mt-0.5">
                  {activeDetail.scientific_name || 'N/A'}
                </p>
                <p className="text-[10px] text-surface-500 dark:text-surface-400 mt-1.5 font-semibold">
                  Submission Date: {new Date(activeDetail.created_at).toLocaleString()}
                </p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-black text-primary-600 dark:text-primary-400 font-mono">
                  {Math.round(activeDetail.confidence * 100)}%
                </div>
                <div className="text-[9px] text-surface-500 dark:text-surface-450 uppercase font-semibold">Score</div>
              </div>
            </div>

            {/* Subpredictions list */}
            {activeDetail.top_predictions && (
              <div className="space-y-2.5">
                <h5 className="text-xs font-bold uppercase text-surface-500 dark:text-surface-400">Predictions breakdown</h5>
                <div className="space-y-2">
                  {activeDetail.top_predictions.map((pred, i) => (
                    <div key={i} className="flex items-center justify-between text-xs">
                      <span className="text-surface-800 dark:text-surface-300 font-semibold">{pred.name}</span>
                      <span className="font-extrabold text-surface-900 dark:text-white font-mono">{Math.round(pred.confidence * 100)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
}

export default PlantDetection;
