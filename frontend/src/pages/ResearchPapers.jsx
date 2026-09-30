import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, BookOpen, ExternalLink, Calendar, User, History, RefreshCw, AlertCircle, ChevronLeft, ChevronRight } from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import Card from '../components/common/Card';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import Loader from '../components/common/Loader';
import EmptyState from '../components/common/EmptyState';
import useToast from '../hooks/useToast';
import axios from 'axios';

const SEARCH_HISTORY_KEY = 'mediplant_search_history';
const FETCH_SIZE = 80;
const PAGE_SIZE = 8;

// ── Plant synonym map ─────────────────────────────────────────────
const PLANT_SYNONYMS = {
  tulsi: '("Ocimum tenuiflorum" OR "Ocimum sanctum" OR "holy basil")',
  neem: '("Azadirachta indica" OR "neem")',
  ashwagandha: '("Withania somnifera" OR "ashwagandha" OR "Indian ginseng")',
  'aloe vera': '("Aloe vera" OR "Aloe barbadensis")',
  brahmi: '("Bacopa monnieri" OR "brahmi")',
  turmeric: '("Curcuma longa" OR "turmeric" OR "curcumin")',
  amla: '("Phyllanthus emblica" OR "Emblica officinalis" OR "amla" OR "Indian gooseberry")',
  ginger: '("Zingiber officinale" OR "ginger")',
  garlic: '("Allium sativum" OR "garlic")',
  moringa: '("Moringa oleifera" OR "moringa" OR "drumstick tree")',
  giloy: '("Tinospora cordifolia" OR "giloy" OR "guduchi")',
  mint: '("Mentha spicata" OR "spearmint" OR "mint")',
  hibiscus: '("Hibiscus rosa-sinensis" OR "hibiscus")',
  shatavari: '("Asparagus racemosus" OR "shatavari")',
  fenugreek: '("Trigonella foenum-graecum" OR "fenugreek")',
};

// ── Medical intent keyword map ────────────────────────────────────
const MEDICAL_INTENTS = [
  { keywords: ['pregnant', 'pregnancy', 'maternal', 'gestational', 'trimester'], query: '(pregnancy OR pregnant OR maternal OR gestational safety)' },
  { keywords: ['warfarin', 'anticoagulant', 'blood thinner', 'coagulation', 'bleeding'], query: '(warfarin OR anticoagulant OR "drug interaction" OR coagulation OR bleeding)' },
  { keywords: ['diabetes', 'diabetic', 'blood sugar', 'glycemic', 'insulin', 'hypoglycemic'], query: '(diabetes OR diabetic OR glycemic OR "blood glucose" OR hypoglycemic)' },
  { keywords: ['safety', 'safe', 'toxicity', 'toxic', 'adverse', 'side effect'], query: '(safety OR toxicity OR "adverse effects" OR "side effects")' },
  { keywords: ['drug interaction', 'interaction', 'cyp', 'metabolism'], query: '("drug interaction" OR pharmacokinetics OR "herb drug interaction")' },
  { keywords: ['hypertension', 'blood pressure', 'antihypertensive'], query: '(hypertension OR "blood pressure" OR antihypertensive)' },
  { keywords: ['anxiety', 'stress', 'adaptogen', 'cortisol'], query: '(anxiety OR stress OR adaptogen OR cortisol)' },
  { keywords: ['cancer', 'tumor', 'anticancer', 'antitumor'], query: '(cancer OR tumor OR anticancer OR antitumor)' },
  { keywords: ['antimicrobial', 'antibacterial', 'antifungal', 'antiviral', 'infection'], query: '(antimicrobial OR antibacterial OR antifungal OR antiviral)' },
  { keywords: ['liver', 'hepato', 'hepatoprotective'], query: '(hepatoprotective OR liver OR hepatotoxicity)' },
];

// ── Study classification — three-layer priority system ────────────

// Layer 0A: Animal exclusion signals — if found in TITLE, always Animal Study
const ANIMAL_TITLE_SIGNALS = [
  'wistar rat', 'sprague-dawley', 'balb/c', 'c57bl/6', 'murine model',
  'rat model', 'mouse model', 'rodent model', 'zebrafish model', 'rabbit model',
  'guinea pig model', 'in rats', 'in mice', 'male rats', 'female rats',
  'male mice', 'female mice', 'albino rats', 'albino mice',
];

// Layer 0A: Animal signals — if found in ABSTRACT as primary methodology
const ANIMAL_ABSTRACT_SIGNALS = [
  'wistar rats', 'sprague-dawley rats', 'balb/c mice', 'c57bl/6 mice',
  'male wistar', 'female wistar', 'male sprague', 'albino rats were',
  'rats were divided', 'mice were divided', 'rats were treated',
  'mice were treated', 'rats were administered', 'mice were administered',
  'experimental rats', 'experimental mice', 'animal model of',
  'induced in rats', 'induced in mice', 'kidney injury rat',
  'hepatotoxicity in rats', 'gentamicin-induced', 'ccl4-induced',
  'streptozotocin-induced', 'doxorubicin-induced',
];

// Layer 0B: In-vitro exclusion signals — if lab assay is the primary method
const INVITRO_TITLE_SIGNALS = [
  'in vitro', 'agar diffusion', 'broth microdilution', 'minimum inhibitory',
  'mic determination', 'cell line', 'cytotoxicity assay', 'mtt assay',
  'time-kill assay', 'disc diffusion', 'antifungal activity against',
  'antibacterial activity against', 'protein leakage',
];

const INVITRO_ABSTRACT_SIGNALS = [
  'agar diffusion assay', 'broth microdilution', 'minimum inhibitory concentration',
  'time-kill assay', 'protein leakage assay', 'mtt assay', 'hela cells',
  'vero cells', 'hek 293', 'mcf-7', 'a549 cells', 'hela cell line',
  'candida albicans', 'aspergillus', 'e. coli strain', 'staphylococcus aureus strain',
  'antifungal testing', 'in vitro antibacterial', 'in vitro antifungal',
];

// Layer 1: High-confidence unambiguous markers
const HIGH_CONFIDENCE = [
  { label: 'Meta-Analysis',     score: 10, signals: ['meta-analysis', 'meta analysis', 'pooled analysis of', 'combined analysis of'] },
  { label: 'Systematic Review', score: 9,  signals: ['systematic review', 'systematic literature review', 'cochrane review'] },
  { label: 'RCT',               score: 8,  signals: ['randomized controlled trial', 'randomised controlled trial', 'double-blind placebo', 'double blind placebo', 'placebo-controlled trial', 'placebo controlled trial'] },
];

// Layer 2: Contextual — only valid if human subjects confirmed
const CONTEXTUAL_HUMAN = [
  { label: 'Clinical Trial',      score: 7, signals: ['clinical trial', 'clinical investigation', 'crossover trial', 'open-label trial', 'phase i trial', 'phase ii trial', 'phase iii trial'] },
  { label: 'Observational Study', score: 6, signals: ['cohort study', 'case-control study', 'cross-sectional study', 'prospective study', 'retrospective study', 'population-based study'] },
  { label: 'Case Report',         score: 5, signals: ['case report', 'case series', 'we report a case', 'a case of'] },
];

// Layer 3: Fallback classification
const FALLBACK_TYPES = [
  { label: 'Review',              score: 5, signals: ['literature review', 'narrative review', 'pharmacological review', 'comprehensive review', 'review of the literature'] },
  { label: 'Computational Study', score: 1, signals: ['molecular docking', 'in silico', 'computational study', 'bioinformatics analysis', 'network pharmacology'] },
];

// Human subjects confirmation signals
const HUMAN_CONFIRMATION = [
  'patients', 'participants', 'volunteers', 'healthy adults', 'human subjects',
  'enrolled', 'recruited', 'informed consent', 'institutional review board',
  'irb approval', 'ethics committee', 'clinical setting', 'hospital',
];

const IRRELEVANT_PATTERNS = [
  'cadmium stress', 'phytoremediation', 'biosorbent', 'dye removal', 'heavy metal removal',
  'wastewater treatment', 'agronomy', 'soil microbial', 'transcriptomic analysis',
  'nanoparticle synthesis', 'green synthesis of nanoparticles', 'gene expression analysis',
  'cadmium toxicity in plant', 'plant growth promotion',
];

// ── Query builder ─────────────────────────────────────────────────
function buildSmartQuery(rawInput) {
  const lower = rawInput.toLowerCase();

  // Check for plant synonym match
  let plantQuery = null;
  for (const [name, synonymQuery] of Object.entries(PLANT_SYNONYMS)) {
    if (lower.includes(name)) {
      plantQuery = synonymQuery;
      break;
    }
  }

  // Check for medical intents
  const matchedIntents = MEDICAL_INTENTS.filter(({ keywords }) =>
    keywords.some((kw) => lower.includes(kw))
  );

  // If no plant found and no intents, treat as raw query
  if (!plantQuery && matchedIntents.length === 0) {
    return { pubmedQuery: rawInput, expanded: false, intentLabels: [] };
  }

  const plantPart = plantQuery || `"${rawInput}"`;
  const intentParts = matchedIntents.map((i) => i.query);

  let pubmedQuery;
  if (intentParts.length > 0) {
    pubmedQuery = `${plantPart} AND (${intentParts.join(' OR ')})`;
  } else {
    pubmedQuery = `${plantPart} AND (clinical OR safety OR pharmacology OR therapy)`;
  }

  const intentLabels = matchedIntents.map((i) => i.keywords[0]);
  return { pubmedQuery, expanded: true, intentLabels };
}

// ── Safety alert signals — specific, not generic ─────────────────
const SAFETY_POSITIVE_SIGNALS = [
  'contraindicated', 'avoid during pregnancy', 'not recommended during pregnancy',
  'herb-drug interaction', 'clinically significant interaction',
  'bleeding risk', 'hepatotoxicity', 'nephrotoxicity', 'serious adverse',
  'potentially unsafe', 'do not use', 'avoid concomitant', 'increases warfarin',
  'potentiates warfarin', 'inhibits cyp', 'induces cyp',
  'reported toxicity', 'reported hepatotoxicity', 'case of toxicity',
  'hospitalised', 'hospitalized', 'emergency', 'liver failure', 'renal failure',
];

// Negation patterns — if any precede a safety signal, it is NOT a safety alert
const SAFETY_NEGATION_PREFIXES = [
  'no ', 'not ', 'without ', 'absence of ', 'well tolerated', 'well-tolerated',
  'no significant adverse', 'no adverse', 'no serious adverse', 'no major adverse',
  'did not cause', 'did not induce', 'was not associated', 'were not associated',
  'no evidence of', 'no signs of', 'no symptoms of',
];

function detectSafetyAlert(title, abstract) {
  const text = `${title} ${abstract}`;
  for (const signal of SAFETY_POSITIVE_SIGNALS) {
    if (!text.includes(signal)) continue;
    // Check 60-char window before signal for negation
    const idx = text.indexOf(signal);
    const window = text.substring(Math.max(0, idx - 60), idx);
    const negated = SAFETY_NEGATION_PREFIXES.some((neg) => window.includes(neg));
    if (!negated) return true;
  }
  return false;
}

// ── Study type classifier — priority hierarchy ────────────────────
function classifyStudyType(title, abstract) {
  const hasHuman = HUMAN_CONFIRMATION.some((s) => abstract.includes(s));

  // Layer 0A: Animal exclusion — title is definitive
  if (ANIMAL_TITLE_SIGNALS.some((s) => title.includes(s))) {
    return { label: 'Animal Study', score: 3 };
  }
  // Layer 0A: Animal exclusion — abstract primary methodology
  if (ANIMAL_ABSTRACT_SIGNALS.some((s) => abstract.includes(s))) {
    return { label: 'Animal Study', score: 3 };
  }

  // Layer 0B: In-vitro exclusion — title is definitive
  if (INVITRO_TITLE_SIGNALS.some((s) => title.includes(s))) {
    return { label: 'In-Vitro Study', score: 2 };
  }
  // Layer 0B: In-vitro exclusion — abstract primary methodology
  if (INVITRO_ABSTRACT_SIGNALS.some((s) => abstract.includes(s))) {
    return { label: 'In-Vitro Study', score: 2 };
  }

  // Layer 1: High-confidence unambiguous markers (title or abstract)
  for (const { label, score, signals } of HIGH_CONFIDENCE) {
    if (signals.some((s) => title.includes(s) || abstract.includes(s))) {
      return { label, score };
    }
  }

  // Layer 2: Contextual — ONLY valid with human confirmation
  if (hasHuman) {
    for (const { label, score, signals } of CONTEXTUAL_HUMAN) {
      if (signals.some((s) => title.includes(s) || abstract.includes(s))) {
        return { label, score };
      }
    }
    // Has human subjects but no specific design label → generic clinical study
    return { label: 'Clinical Study', score: 6 };
  }

  // Layer 3: Fallback — review or computational
  for (const { label, score, signals } of FALLBACK_TYPES) {
    if (signals.some((s) => title.includes(s) || abstract.includes(s))) {
      return { label, score };
    }
  }

  return { label: 'Study', score: 4 };
}

// ── Paper scoring ─────────────────────────────────────────────────
function scorePaper(paper) {
  const title = paper.title.toLowerCase();
  const abstract = paper.abstract.toLowerCase();
  const text = `${title} ${abstract}`;

  // Hard irrelevance filter
  if (IRRELEVANT_PATTERNS.some((p) => text.includes(p))) {
    return { score: -1, studyLabel: 'Irrelevant', studyColor: 'red', isSafetyAlert: false };
  }

  // Penalise missing abstracts — cannot classify without text
  if (paper.abstract === 'Abstract not available.') {
    return { score: 1, studyLabel: 'No Abstract', studyColor: 'gray', isSafetyAlert: false };
  }

  // Classify study type using priority hierarchy
  const { label, score } = classifyStudyType(title, abstract);

  // Safety alert — context-aware, with negation detection
  const isSafetyAlert = detectSafetyAlert(title, abstract);

  // Recency bonus
  const pubYear = parseInt(paper.pubDate) || 2000;
  const recencyBonus = pubYear >= 2020 ? 2 : pubYear >= 2015 ? 1 : 0;

  // Human subjects bonus
  const humanBonus = HUMAN_CONFIRMATION.some((s) => abstract.includes(s)) ? 1 : 0;

  // Safety bonus — elevates important safety papers regardless of study type
  const safetyBonus = isSafetyAlert ? 3 : 0;

  return {
    score: score + humanBonus + recencyBonus + safetyBonus,
    studyLabel: label,
    studyColor: isSafetyAlert ? 'red' : getStudyColor(score),
    isSafetyAlert,
  };
}

function getStudyColor(score) {
  if (score >= 9) return 'purple';
  if (score >= 7) return 'blue';
  if (score >= 5) return 'green';
  if (score >= 3) return 'yellow';
  return 'gray';
}

const STUDY_COLOR_CLASSES = {
  purple: 'bg-purple-500/10 border-purple-500/20 text-purple-700 dark:text-purple-300',
  blue:   'bg-blue-500/10 border-blue-500/20 text-blue-700 dark:text-blue-300',
  green:  'bg-emerald-500/10 border-emerald-500/20 text-emerald-700 dark:text-emerald-300',
  yellow: 'bg-yellow-500/10 border-yellow-500/20 text-yellow-700 dark:text-yellow-300',
  gray:   'bg-surface-500/10 border-surface-500/20 text-surface-600 dark:text-surface-400',
  red:    'bg-red-500/10 border-red-500/20 text-red-600 dark:text-red-400',
};

export function ResearchPapers() {
  const { addToast } = useToast();
  const [searchParams, setSearchParams] = useSearchParams();

  const [searchQuery, setSearchQuery] = useState('');
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchHistory, setSearchHistory] = useState([]);
  const [expandedQuery, setExpandedQuery] = useState('');
  const [intentLabels, setIntentLabels] = useState([]);

  // Pagination over filtered results
  const [allRankedPapers, setAllRankedPapers] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    const history = localStorage.getItem(SEARCH_HISTORY_KEY);
    if (history) {
      try { setSearchHistory(JSON.parse(history)); } catch (_) { /* ignore corrupt saved history */ }
    }
  }, []);

  const saveToHistory = (term) => {
    if (!term.trim()) return;
    const cleanTerm = term.trim();
    const filtered = searchHistory.filter((t) => t.toLowerCase() !== cleanTerm.toLowerCase());
    const updated = [cleanTerm, ...filtered].slice(0, 8);
    setSearchHistory(updated);
    localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(updated));
  };

  const executeSearch = useCallback(async (query) => {
    if (!query.trim()) return;
    setLoading(true);
    setError('');
    setAllRankedPapers([]);
    setCurrentPage(1);

    const { pubmedQuery, expanded, intentLabels: labels } = buildSmartQuery(query.trim());
    setExpandedQuery(expanded ? pubmedQuery : '');
    setIntentLabels(labels);

    try {
      // Step 1: Fetch up to FETCH_SIZE PMIDs
      const searchUrl = `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=${encodeURIComponent(pubmedQuery)}&retmode=json&retmax=${FETCH_SIZE}&retstart=0&sort=relevance`;
      const searchRes = await axios.get(searchUrl);
      const esearchResult = searchRes.data?.esearchresult || {};
      const idList = esearchResult.idlist || [];
      setTotalCount(parseInt(esearchResult.count || '0', 10));

      if (idList.length === 0) {
        setPapers([]);
        setLoading(false);
        return;
      }

      // Step 2: Fetch metadata + abstracts in parallel
      const idsParam = idList.join(',');
      const [summaryRes, fetchRes] = await Promise.all([
        axios.get(`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=${idsParam}&retmode=json`),
        axios.get(`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=${idsParam}&rettype=abstract&retmode=xml`),
      ]);

      const resultObj = summaryRes.data?.result || {};

      // Parse abstracts from XML
      const xmlDoc = new DOMParser().parseFromString(fetchRes.data, 'text/xml');
      const abstractMap = {};
      xmlDoc.querySelectorAll('PubmedArticle').forEach((article) => {
        const pmid = article.querySelector('PMID')?.textContent;
        const texts = article.querySelectorAll('AbstractText');
        if (pmid && texts.length > 0) {
          abstractMap[pmid] = Array.from(texts).map((el) => el.textContent).join(' ');
        }
      });

      // Step 3: Build paper objects
      const allPapers = idList.map((id) => {
        const item = resultObj[id] || {};
        const authorNames = item.authors ? item.authors.map((a) => a.name).join(', ') : 'Unknown Authors';
        let doi = '';
        if (item.articleids) {
          const doiObj = item.articleids.find((aid) => aid.idtype === 'doi');
          if (doiObj) doi = doiObj.value;
        }
        return {
          id,
          title: item.title || 'Untitled Publication',
          authors: authorNames,
          journal: item.source || 'Unknown Journal',
          pubDate: item.pubdate || 'N/A',
          doi,
          url: `https://pubmed.ncbi.nlm.nih.gov/${id}/`,
          abstract: abstractMap[id] || 'Abstract not available.',
        };
      });

      // Step 4: Score, filter irrelevant, sort by evidence quality
      const scored = allPapers
        .map((p) => ({ ...p, ...scorePaper(p) }))
        .filter((p) => p.score >= 0)
        .sort((a, b) => b.score - a.score);

      setAllRankedPapers(scored);
      setPapers(scored.slice(0, PAGE_SIZE));
    } catch (err) {
      console.error(err);
      if (err.response?.status === 429) {
        setError('PubMed API rate limit exceeded. Please wait a moment and try again.');
      } else {
        setError('Failed to connect to PubMed. Check your internet connection.');
      }
      addToast('Error querying PubMed records.', 'error');
    } finally {
      setLoading(false);
    }
  }, [addToast]);

  useEffect(() => {
    const q = searchParams.get('q');
    if (q) {
      setSearchQuery(q);
      executeSearch(q);
      saveToHistory(q);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    saveToHistory(searchQuery);
    setSearchParams({ q: searchQuery });
    executeSearch(searchQuery);
  };

  const handleHistoryClick = (term) => {
    setSearchQuery(term);
    saveToHistory(term);
    setSearchParams({ q: term });
    executeSearch(term);
  };

  const clearHistory = () => {
    setSearchHistory([]);
    localStorage.removeItem(SEARCH_HISTORY_KEY);
    addToast('Search history cleared.', 'success');
  };

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    const start = (newPage - 1) * PAGE_SIZE;
    setPapers(allRankedPapers.slice(start, start + PAGE_SIZE));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="space-y-6 relative z-10 w-full pb-10">
      <PageHeader
        title="PubMed Research Papers"
        description="Browse clinical trials, biological assays, and pharmacological reviews for therapeutic applications."
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Search Panel */}
        <div className="lg:col-span-3 space-y-6">
          <Card className="glass p-4 rounded-2xl shadow-lg">
            <form onSubmit={handleSearchSubmit} className="flex gap-2">
              <Input
                placeholder="Search PubMed keywords (e.g. Aegle marmelos, Ocimum tenuiflorum)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 bg-transparent border-none focus:ring-0 text-surface-900 dark:text-white text-xs"
              />
              <Button type="submit" variant="primary" disabled={loading} className="rounded-xl shadow-glow">
                <Search className="w-4 h-4 mr-2" /> Search
              </Button>
            </form>
          </Card>

          <AnimatePresence mode="wait">
            {loading ? (
              <motion.div
                key="loader"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center justify-center py-20 space-y-4"
              >
                <Loader className="w-8 h-8 text-primary-500" />
                <p className="text-xs text-surface-400">Fetching registry index from NCBI E-Utilities...</p>
              </motion.div>
            ) : error ? (
              <motion.div key="error" className="p-8 border border-red-500/20 bg-red-500/5 text-center rounded-2xl shadow-lg">
                <AlertCircle className="w-12 h-12 text-red-500 dark:text-red-400 mx-auto mb-3" />
                <h4 className="font-bold text-red-700 dark:text-red-300 mb-1">Search failed</h4>
                <p className="text-xs text-red-800 dark:text-red-400 max-w-sm mx-auto mb-4">{error}</p>
                <Button onClick={() => executeSearch(searchQuery, currentPage)} variant="secondary" className="py-2.5 px-4 text-xs">
                  <RefreshCw className="w-4 h-4 mr-2" /> Retry Request
                </Button>
              </motion.div>
            ) : papers.length === 0 ? (
              <motion.div key="empty" className="w-full">
                <EmptyState
                  title={searchQuery ? 'No publications found' : 'Begin Search'}
                  description={
                    searchQuery
                      ? `No publications match "${searchQuery}". Please verify naming variants.`
                      : 'Enter plant common or scientific nomenclature labels above to pull indexed papers.'
                  }
                  icon={BookOpen}
                />
              </motion.div>
            ) : (
              <motion.div
                key="results"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-4"
              >
                <div className="space-y-2">
                  <div className="text-[10px] font-bold text-surface-500 dark:text-surface-400 uppercase tracking-wider">
                    Found {totalCount} publications — showing {allRankedPapers.length} after evidence filtering, ranked by study quality
                  </div>
                  {expandedQuery && (
                    <div className="text-[9px] bg-primary-500/5 border border-primary-500/20 rounded-lg px-3 py-2 text-primary-700 dark:text-primary-300 font-mono break-all">
                      <span className="font-bold not-italic font-sans mr-1">Query:</span>{expandedQuery}
                    </div>
                  )}
                  {intentLabels.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {intentLabels.map((label) => (
                        <span key={label} className="text-[9px] bg-emerald-500/10 border border-emerald-500/20 text-emerald-700 dark:text-emerald-300 px-2 py-0.5 rounded font-bold capitalize">
                          {label}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="space-y-4">
                  {papers.map((paper) => (
                    <Card key={paper.id} className="glass hover:border-primary-500/30 transition-all rounded-2xl p-5 shadow-lg group relative overflow-hidden card-hover">
                      <div className="space-y-3">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="inline-flex items-center gap-1 text-[9px] bg-primary-500/10 border border-primary-500/20 text-primary-700 dark:text-primary-400 px-2 py-0.5 rounded font-bold">
                            PMID: {paper.id}
                          </span>
                          {paper.studyLabel && (
                            <span className={`inline-flex items-center text-[9px] px-2 py-0.5 rounded border font-bold ${STUDY_COLOR_CLASSES[paper.studyColor] || STUDY_COLOR_CLASSES.gray}`}>
                              {paper.studyLabel}
                            </span>
                          )}
                          {paper.isSafetyAlert && (
                            <span className="inline-flex items-center gap-1 text-[9px] px-2 py-0.5 rounded border bg-red-500/10 border-red-500/20 text-red-700 dark:text-red-300 font-bold">
                              ⚠ Safety Alert
                            </span>
                          )}
                          {paper.score >= 9 && !paper.isSafetyAlert && (
                            <span className="inline-flex items-center text-[9px] px-2 py-0.5 rounded border bg-amber-500/10 border-amber-500/20 text-amber-700 dark:text-amber-300 font-bold">
                              ★ High Evidence
                            </span>
                          )}
                        </div>

                        <h4 className="text-sm font-extrabold text-surface-900 dark:text-white leading-snug">
                          <a
                            href={paper.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:text-primary-500 dark:hover:text-primary-400 inline-flex items-center gap-1.5 transition-colors"
                          >
                            {paper.title.replace(/\.$/, '')}
                            <ExternalLink className="w-3.5 h-3.5 text-surface-400 dark:text-surface-300 group-hover:text-primary-500 dark:group-hover:text-primary-400" />
                          </a>
                        </h4>

                        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[10px] text-surface-500 dark:text-surface-400 font-semibold">
                          <span className="flex items-center gap-1">
                            <User className="w-3.5 h-3.5 text-surface-400 dark:text-surface-300" />
                            {paper.authors.length > 55 ? `${paper.authors.substring(0, 55)}...` : paper.authors}
                          </span>
                          <span>•</span>
                          <span className="text-primary-600 dark:text-primary-400 truncate max-w-[150px]">{paper.journal}</span>
                          <span>•</span>
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3.5 h-3.5 text-surface-400 dark:text-surface-300" />
                            {paper.pubDate}
                          </span>
                        </div>

                        <p className="text-[11px] text-surface-700 dark:text-surface-300 leading-relaxed bg-surface-50 dark:bg-black/40 p-3.5 rounded-xl border border-surface-200 dark:border-white/5 font-medium">
                          {paper.abstract}
                        </p>

                        {paper.doi && (
                          <div className="text-[9px] text-surface-500 dark:text-surface-400 font-bold">
                            DOI: <span className="font-mono">{paper.doi}</span>
                          </div>
                        )}
                      </div>
                    </Card>
                  ))}
                </div>

                {/* Pagination Controls */}
                {allRankedPapers.length > PAGE_SIZE && (
                  <div className="flex justify-between items-center glass p-4 rounded-xl mt-6">
                    <Button
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1 || loading}
                      variant="secondary"
                      size="sm"
                      className="text-xs px-3.5"
                    >
                      <ChevronLeft className="w-4 h-4 mr-1" /> Previous
                    </Button>
                    <span className="text-xs text-surface-700 dark:text-surface-300 font-bold">
                      Page {currentPage} of {Math.ceil(allRankedPapers.length / PAGE_SIZE)}
                    </span>
                    <Button
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage * PAGE_SIZE >= allRankedPapers.length || loading}
                      variant="secondary"
                      size="sm"
                      className="text-xs px-3.5"
                    >
                      Next <ChevronRight className="w-4 h-4 ml-1" />
                    </Button>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Sidebar History Panel */}
        <div className="lg:col-span-1">
          <Card className="glass rounded-2xl p-5 shadow-lg">
            <div className="flex items-center justify-between pb-2 border-b border-surface-200 dark:border-white/5 mb-4">
              <h3 className="text-[10px] font-bold uppercase text-surface-500 dark:text-surface-400 tracking-wider flex items-center gap-1.5">
                <History className="w-4 h-4 text-surface-400 dark:text-surface-300" /> Recent Terms
              </h3>
              {searchHistory.length > 0 && (
                <button
                  onClick={clearHistory}
                  className="text-[9px] text-red-600 dark:text-red-400 font-bold hover:underline"
                >
                  Clear
                </button>
              )}
            </div>

            {searchHistory.length === 0 ? (
              <div className="text-center py-6 text-xs text-surface-500 dark:text-surface-400 font-medium">
                No past queries.
              </div>
            ) : (
              <div className="space-y-1.5">
                {searchHistory.map((term, i) => (
                  <button
                    key={i}
                    onClick={() => handleHistoryClick(term)}
                    className="flex items-center gap-2 w-full text-left px-2.5 py-2 rounded-xl text-xs text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-white/5 border border-transparent hover:border-surface-200 dark:hover:border-white/5 transition-all font-semibold truncate"
                  >
                    <Search className="w-3.5 h-3.5 text-surface-400 dark:text-surface-300 flex-shrink-0" />
                    <span className="truncate flex-1">{term}</span>
                  </button>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}

export default ResearchPapers;
