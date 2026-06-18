"""
Build Vector Index
==================

Script to build the FAISS vector index from sample medicinal plant
documents.  Run this once before using the chat assistant:

    python -m scripts.build_index

The script:
1. Defines sample medicinal plant knowledge base entries.
2. Chunks them for optimal retrieval.
3. Generates embeddings via sentence-transformers.
4. Builds and persists a FAISS index.
"""
from __future__ import annotations

import sys
import os
import time

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.embeddings import get_embedding_service, EmbeddingService
from rag.vector_store import VectorStoreService

# ── Sample Medicinal Plant Knowledge Base ─────────────────────

PLANT_DOCUMENTS = [
    {
        "source": "tulsi_monograph",
        "plant": "Tulsi",
        "content": (
            "Tulsi (Ocimum tenuiflorum), also known as Holy Basil, is one of the most sacred plants in India, belonging to the family Lamiaceae. "
            "Medicinal Uses: Revered as an adaptogen, Tulsi helps the body adapt to stress and balances energy. It exhibits strong anti-inflammatory, antioxidant, and antimicrobial properties. It is highly effective in treating respiratory conditions such as coughs, cold, bronchitis, asthma, and sore throats. It helps regulate blood sugar, supports cardiac function, and boosts overall immune system activity. "
            "Preparation Methods: Commonly consumed as an herbal infusion (Tulsi tea) by boiling 5-8 fresh leaves in water. The fresh leaf juice can be extracted directly, or the raw leaves can be chewed. "
            "Precautions: Tulsi may lower blood glucose levels; diabetics on insulin or oral medications should monitor blood sugar. It contains eugenol, which has mild blood-thinning effects, so avoid excessive quantities before surgery or if taking antiplatelet/anticoagulant drugs. Safety during pregnancy and lactation is not established; consult a doctor. "
            "Common Misconceptions: Some believe Tulsi has no side effects because it is sacred, but large doses can cause liver strain due to eugenol concentration, and chewing leaves excessively is sometimes discouraged due to trace mercury or iron content that can damage tooth enamel."
        ),
    },
    {
        "source": "neem_monograph",
        "plant": "Neem",
        "content": (
            "Neem (Azadirachta indica), belonging to the family Meliaceae, is traditionally called the 'village pharmacy' due to its comprehensive healing traits. "
            "Medicinal Uses: Neem is a powerful antiseptic, antifungal, antibacterial, and antiviral agent. It is widely applied in dermatology to cure acne, eczema, psoriasis, ringworm, and scabies. Neem bark extracts act as anti-malarial agents, and neem oil is used for head lice and insect repellent. It is highly valued for blood purification, liver detoxification, and improving oral hygiene. "
            "Preparation Methods: Neem leaves are crushed into a paste for topical application on skin infections. A decoction is prepared by boiling leaves in water. Neem oil is diluted in a carrier oil for skin application. Twigs are chewed as natural toothbrushes. "
            "Precautions: Neem is a potent abortifacient and must be strictly avoided during pregnancy. Long-term internal use can lead to liver or kidney toxicity. It can lower blood sugar, requiring careful monitoring in diabetics. Neem oil should never be ingested internally in large doses, especially by children, as it can cause severe poisoning or death. "
            "Common Misconceptions: Many assume that because neem twigs are good for gums, neem oil can be consumed daily as a health tonic. Internal ingestion of neem oil is highly toxic and can cause liver damage."
        ),
    },
    {
        "source": "ashwagandha_monograph",
        "plant": "Ashwagandha",
        "content": (
            "Ashwagandha (Withania somnifera), known as Indian Ginseng or Winter Cherry, belongs to the family Solanaceae and has been used in Ayurveda for over 3,000 years. "
            "Medicinal Uses: As a premier adaptogenic herb, Ashwagandha reduces physical and mental stress, lowers cortisol levels, and alleviates anxiety and depression. It enhances cognitive function, memory, concentration, and muscle strength. It boosts testosterone and improves sperm quality and motility, addressing male fertility issues. It also supports thyroid health in hypothyroidism and aids sleep. "
            "Preparation Methods: The dried root powder (Churna) is traditionally mixed with warm milk and honey before bedtime. It is also available in standardized tablets or liquid extracts. "
            "Precautions: Ashwagandha must be avoided during pregnancy as it may cause uterine contractions. People with autoimmune diseases (lupus, rheumatoid arthritis, type 1 diabetes) should avoid it as it stimulates immune response. It may interact with thyroid hormone supplements, sedatives, and immunosuppressive medications. "
            "Common Misconceptions: A common misconception is that Ashwagandha is a stimulant because it increases stamina. In reality, it is a calming adaptogen that helps balance the nervous system, improving sleep quality rather than causing insomnia."
        ),
    },
    {
        "source": "aloe_vera_monograph",
        "plant": "Aloe Vera",
        "content": (
            "Aloe Vera (Aloe barbadensis miller) is a succulent plant belonging to the family Asphodelaceae, utilized across historical cultures for skincare and digestive health. "
            "Medicinal Uses: The cooling inner leaf gel is highly effective for soothing sunburns, thermal burns, cuts, and minor skin wounds. Orally, aloe vera juice supports digestive health, reduces inflammation in ulcerative colitis, and acts as a laxative. It has strong moisturizing, antimicrobial, and anti-aging properties. "
            "Preparation Methods: The fresh inner gel is scraped from cut leaves and applied directly to the skin. The gel can be blended with water or juice for oral consumption. "
            "Precautions: Avoid consuming the yellow latex (aloin) found directly beneath the leaf rind, as it is a harsh anthraquinone laxative that causes severe abdominal cramps and electrolyte depletion. Oral ingestion is contraindicated during pregnancy due to risk of uterine contractions. It may interact with diuretics and diabetic medications. "
            "Common Misconceptions: Many believe the whole aloe leaf can be juiced and consumed safely. However, the outer leaf and yellow latex contain aloin, which is a gastrointestinal irritant and a suspected carcinogen in high chronic doses."
        ),
    },
    {
        "source": "brahmi_monograph",
        "plant": "Brahmi",
        "content": (
            "Brahmi (Bacopa monnieri), belonging to the family Plantaginaceae, is a creeping perennial herb found in wet, marshy wetlands and is revered as a cognitive enhancer. "
            "Medicinal Uses: Brahmi is renowned for improving memory, learning retention, speed of information processing, and overall cognitive performance. It reduces anxiety, stress, and mental fatigue by modulating cortisol. It exhibits antioxidant and anti-inflammatory properties that protect brain cells from oxidative stress. "
            "Preparation Methods: Consumed as fresh leaf juice, infusion of dried herb, or dried root/herb powder mixed with warm water, milk, or clarified butter (ghee). "
            "Precautions: Brahmi may cause mild gastrointestinal symptoms, including nausea, bloating, and stomach cramps, particularly if taken on an empty stomach. It has mild sedative properties and may interact with thyroid drugs or anticholinergic medications. "
            "Common Misconceptions: People often confuse Bacopa monnieri (Brahmi) with Centella asiatica (Gotu Kola), which is also sometimes called Brahmi. While both support brain health, they are botanically distinct plants with different active constituents."
        ),
    },
    {
        "source": "turmeric_monograph",
        "plant": "Turmeric",
        "content": (
            "Turmeric (Curcuma longa) is a rhizomatous herbaceous plant of the ginger family Zingiberaceae, native to the Indian subcontinent. "
            "Medicinal Uses: The active polyphenol curcumin gives turmeric its potent anti-inflammatory and antioxidant properties. It is highly effective in relieving joint pain, stiffness, and inflammation associated with osteoarthritis and rheumatoid arthritis. It supports liver detoxification, cardiovascular function, and digestive health. "
            "Preparation Methods: The dried rhizome powder is used widely in cooking, or mixed with warm milk and black pepper (golden milk) to enhance curcumin absorption. Supplements are available as standardized capsules. "
            "Precautions: Curcumin has mild anticoagulant properties and should not be taken in high doses by individuals on blood thinners. It is contraindicated in cases of bile duct obstruction or gallstones. High doses can cause mild gastric irritation. "
            "Common Misconceptions: A common misconception is that regular culinary turmeric provides enough curcumin for therapeutic effects. In truth, curcumin has very low bioavailability, and therapeutic outcomes usually require black pepper (piperine) or lipid-formulations to enhance absorption."
        ),
    },
    {
        "source": "amla_monograph",
        "plant": "Amla",
        "content": (
            "Amla (Phyllanthus emblica), also called Indian Gooseberry, is a deciduous tree of the family Phyllanthaceae yielding translucent green fruits. "
            "Medicinal Uses: Amla is one of the richest natural sources of Vitamin C, providing potent antioxidant activity. It boosts immune response, enhances skin and hair health, prevents premature hair greying, regulates digestive acidity, and supports liver health. It also helps manage blood glucose and lipid profiles. "
            "Preparation Methods: Fresh fruit juice, dried fruit powder mixed with water or honey, or consumed raw or pickled. "
            "Precautions: Amla is highly acidic; individuals with acute hyperacidity or acid reflux should consume it with food. It has mild antiplatelet properties, so caution is advised if taking blood-thinning medications or before surgeries. "
            "Common Misconceptions: Some think that cooking Amla destroys all its Vitamin C. However, Amla contains heat-stable tannins that protect its Vitamin C content, preserving its antioxidant benefits even after moderate heat processing."
        ),
    },
    {
        "source": "mint_monograph",
        "plant": "Mint",
        "content": (
            "Mint (Mentha spicata), belonging to the family Lamiaceae, is a highly aromatic herb cultivated globally for its cooling flavor and digestive properties. "
            "Medicinal Uses: Mint is widely used to treat indigestion, nausea, flatulence, and irritable bowel syndrome (IBS) by relaxing gastrointestinal muscles. It clears respiratory congestion, relieves tension headaches when applied as oil, and serves as an antibacterial mouth freshener. "
            "Preparation Methods: Steep fresh leaves in hot water for mint tea, inhale essential oil vapors, or apply leaf paste topically. "
            "Precautions: Mint relaxes the lower esophageal sphincter, which can worsen acid reflux and gastroesophageal reflux disease (GERD). Avoid placing pure peppermint oil on the face of infants due to risk of respiratory spasms. "
            "Common Misconceptions: Many believe mint tea is a universal cure for all stomach issues, but if the stomach discomfort is caused by acid reflux (GERD), mint can actually aggravate the burning sensation by relaxing the esophageal valve."
        ),
    },
    {
        "source": "curry_leaves_monograph",
        "plant": "Curry Leaves",
        "content": (
            "Curry Leaves (Murraya koenigii), belonging to the family Rutaceae, are aromatic leaves widely used in South Asian cuisine and traditional medicine. "
            "Medicinal Uses: They are rich in carbazole alkaloids, which exhibit strong antioxidant, anti-inflammatory, and antimicrobial properties. They aid in digestion, regulate blood sugar levels, improve hair growth and scalp health, and help lower cholesterol levels. "
            "Preparation Methods: Infused into warm culinary oils, boiled as an herbal tea, or crushed into hair masks with carrier oils. "
            "Precautions: Generally extremely safe in food amounts. However, curry leaf seeds contain toxic compounds and must never be consumed. "
            "Common Misconceptions: People often assume curry leaves are related to curry powder. Curry powder is actually a commercial blend of spices (turmeric, coriander, cumin) and rarely contains actual curry leaves, which have a distinct citrus-herbal aroma."
        ),
    },
    {
        "source": "hibiscus_monograph",
        "plant": "Hibiscus",
        "content": (
            "Hibiscus (Hibiscus rosa-sinensis), belonging to the family Malvaceae, is a showy evergreen shrub famous for its vibrant trumpet-shaped flowers. "
            "Medicinal Uses: Hibiscus flower extracts are highly valued for regulating high blood pressure and improving lipid profiles. The leaves and petals are rich in mucilage, which strengthens hair roots, prevents dandruff, and cools the body. It displays robust antioxidant properties. "
            "Preparation Methods: Petals are dried and steeped in hot water for a tart herbal tea, or fresh flowers are crushed into a paste for hair and scalp conditioning. "
            "Precautions: Large medicinal doses can lower blood pressure significantly; consult a physician if taking antihypertensive drugs. It contains phytoestrogens and should be avoided by pregnant or lactating women. "
            "Common Misconceptions: Some think any hibiscus species is suitable for tea. In fact, Hibiscus sabdariffa (Roselle) is typically used for culinary tea, while Hibiscus rosa-sinensis is primarily used for hair care and traditional topical preparations."
        ),
    },
    {
        "source": "ginger_monograph",
        "plant": "Ginger",
        "content": (
            "Ginger (Zingiber officinale) is a flowering plant in the family Zingiberaceae, whose underground rhizome is used globally as a spice and medicine. "
            "Medicinal Uses: Ginger is highly effective for alleviating nausea, morning sickness in pregnancy, and motion sickness. It has potent anti-inflammatory properties that ease joint and muscle pain in arthritis. It acts as a carminative, helping to relieve bloating, gas, and digestive cramps. "
            "Preparation Methods: Steep fresh rhizome slices in boiling water for ginger tea, add grated ginger to foods, or consume dried rhizome powder capsules. "
            "Precautions: Ginger may interact with blood thinners due to its antiplatelet properties. Avoid large therapeutic doses if taking warfarin or aspirin. High doses can trigger mild heartburn or diarrhea in sensitive individuals. "
            "Common Misconceptions: Some believe ginger can be consumed in unlimited quantities. However, consuming more than 4 grams of ginger daily can lead to gastric irritation, reflux, and increased risk of bleeding."
        ),
    },
    {
        "source": "garlic_monograph",
        "plant": "Garlic",
        "content": (
            "Garlic (Allium sativum) is a bulbous perennial of the family Amaryllidaceae, containing the organosulfur compound allicin which provides its characteristic odor and medical activity. "
            "Medicinal Uses: Garlic supports cardiovascular health by lowering blood pressure and regulating cholesterol levels. It exhibits broad-spectrum antimicrobial activity against bacteria, viruses, and fungi. It boosts immune response to counter common colds and acts as an antioxidant. "
            "Preparation Methods: Consumed raw (chopped or crushed to activate allicin), infused in oils, or taken as aged garlic extract tablets. "
            "Precautions: Garlic has significant antiplatelet effects and can increase the risk of bleeding. Discontinue therapeutic doses two weeks prior to surgery. It can cause gastrointestinal upset or heartburn if eaten raw in excess. "
            "Common Misconceptions: Many swallow whole garlic cloves to avoid bad breath. However, unless the garlic clove is crushed or chewed, allicin is not synthesized, and most of its medicinal benefits are lost."
        ),
    },
    {
        "source": "moringa_monograph",
        "plant": "Moringa",
        "content": (
            "Moringa (Moringa oleifera), of the family Moringaceae, is a fast-growing, drought-resistant tree native to northwestern India, often called the 'miracle tree'. "
            "Medicinal Uses: Moringa leaves are exceptionally nutrient-dense, providing vitamins, minerals, and essential amino acids. It combats nutritional fatigue, reduces inflammation, helps regulate blood sugar, lowers cholesterol, and acts as a powerful antioxidant. "
            "Preparation Methods: Dried leaf powder is added to smoothies, warm water, or taken as capsules. Fresh leaves are cooked as vegetables. "
            "Precautions: Avoid consuming moringa root extracts or bark, as they contain spirochin, a cardiotoxic alkaloid. Consult a doctor during pregnancy, as moringa leaves may stimulate uterine contractions in high doses. "
            "Common Misconceptions: People assume the entire moringa tree is safe. While the leaves, pods, and seeds are nutritious, the roots and bark contain neurotoxins and should not be eaten."
        ),
    },
    {
        "source": "lemongrass_monograph",
        "plant": "Lemongrass",
        "content": (
            "Lemongrass (Cymbopogon citratus), belonging to the family Poaceae, is a tall perennial grass native to tropical regions of Asia, known for its citrusy scent. "
            "Medicinal Uses: It contains citral, which provides anti-inflammatory, antifungal, and antibacterial benefits. It relieves digestive spasms, bloating, and stomach pain. It acts as a mild sedative to calm anxiety and improve sleep, and helps reduce fevers. "
            "Preparation Methods: Fresh or dried stalks are sliced and steeped in boiling water for lemongrass tea. Essential oil is used in aromatherapy. "
            "Precautions: Pure lemongrass essential oil must be diluted with a carrier oil before skin application to prevent contact dermatitis. Do not ingest pure essential oil. Not recommended in large amounts during pregnancy due to potential uterine stimulation. "
            "Common Misconceptions: Many assume lemongrass tea has caffeine because of its refreshing energy. In fact, lemongrass is completely caffeine-free and is traditionally used as a calming bedtime tea."
        ),
    },
    {
        "source": "shatavari_monograph",
        "plant": "Shatavari",
        "content": (
            "Shatavari (Asparagus racemosus), belonging to the family Asparagaceae, is a climbing species of asparagus native to India, renowned as a reproductive tonic. "
            "Medicinal Uses: Highly valued as a female hormone balancer, Shatavari acts as a galactagogue to promote lactation in nursing mothers. It acts as a cooling demulcent to soothe stomach ulcers, reduces symptoms of menopause (hot flashes), and boosts overall stamina. "
            "Preparation Methods: The root powder is mixed with warm milk and honey, or taken as standardized capsules. "
            "Precautions: Shatavari has mild diuretic properties and should be used with caution if taking prescription diuretic drugs. Avoid if allergic to asparagus species. "
            "Common Misconceptions: A common misconception is that Shatavari is exclusively for women. In Ayurvedic tradition, Shatavari is also used by men to enhance stamina, muscle strength, and general reproductive vitality."
        ),
    },
    {
        "source": "giloy_monograph",
        "plant": "Giloy",
        "content": (
            "Giloy (Tinospora cordifolia), of the family Menispermaceae, is a large climbing shrub native to India, often called 'Amrita' (the root of immortality). "
            "Medicinal Uses: Giloy is a highly potent immunomodulator and antipyretic. It is widely used to treat chronic fevers, boost white blood cell counts, regulate blood sugar, reduce stress, and support liver health during infections. "
            "Preparation Methods: The stem is boiled in water to prepare a concentrated decoction (Giloy Kwath), or consumed as fresh stem juice or extract tablets. "
            "Precautions: Giloy stimulates the immune system and should be used with caution by individuals with autoimmune diseases (lupus, rheumatoid arthritis). It lowers blood sugar, so diabetics should monitor their glucose levels. "
            "Common Misconceptions: Some think that Giloy can cure any viral fever instantly. While it helps build immunity and reduces symptoms, it should be used as a supportive treatment alongside standard clinical protocols."
        ),
    },
    {
        "source": "arjuna_monograph",
        "plant": "Arjuna",
        "content": (
            "Arjuna (Terminalia arjuna), belonging to the family Combretaceae, is a large deciduous tree whose bark is highly valued as a cardiovascular tonic. "
            "Medicinal Uses: Arjuna bark contains cardiac glycosides and flavonoids that strengthen heart muscles, improve blood circulation, regulate blood pressure, and help maintain healthy cholesterol profiles. It acts as a cardioprotective agent after cardiac strain. "
            "Preparation Methods: The bark powder is boiled in water or milk to prepare Arjuna milk decoction (Arjuna Ksheera Pak), or taken as capsules. "
            "Precautions: Arjuna should be used under medical supervision, especially if the patient is taking pharmaceutical cardiac medications (beta-blockers, digoxin). Not recommended during pregnancy. "
            "Common Misconceptions: Many assume Arjuna can replace prescription heart medications. In reality, it acts as a supportive botanical supplement and should never be used to replace prescribed cardiovascular drugs."
        ),
    },
    {
        "source": "bael_monograph",
        "plant": "Bael",
        "content": (
            "Bael (Aegle marmelos), belonging to the family Rutaceae, is a sacred deciduous tree native to India, bearing large, hard-shelled fruits with aromatic pulp. "
            "Medicinal Uses: Rich in tannins and pectin, Bael fruit pulp is highly effective for treating acute diarrhea, dysentery, and irritable bowel syndrome (IBS). It exerts protective effects on the gastric mucosa and aids digestion. "
            "Preparation Methods: The orange pulp of the semi-ripe or ripe fruit is consumed fresh, blended into juices, or the dried fruit powder is mixed with water. "
            "Precautions: Excessive consumption of ripe Bael fruit can lead to constipation due to high tannin content. The leaves and bark may have mild hypoglycemic and uterine-stimulating properties; avoid in pregnancy. "
            "Common Misconceptions: Some believe that Bael should only be eaten when fully ripe. However, for treating diarrhea and dysentery, the unripe or semi-ripe fruit is actually more effective due to its higher concentration of astringent tannins."
        ),
    },
    {
        "source": "bhringraj_monograph",
        "plant": "Bhringraj",
        "content": (
            "Bhringraj (Eclipta prostrata), of the family Asteraceae, is a creeping herb found in wet, waste areas and marshy lands, traditionally called the 'king of hair'. "
            "Medicinal Uses: Bhringraj is widely used to promote hair growth, prevent premature greying, treat dandruff, and support scalp health. Internally, it acts as a liver tonic, helping in detoxification, bile regulation, and skin healing. "
            "Preparation Methods: The fresh leaf juice is infused into a carrier oil (like coconut or sesame oil) for scalp application, or leaf paste is applied topically. "
            "Precautions: Bhringraj is considered to have a cooling effect. When applied to the scalp, it can cause a mild cooling sensation; avoid if suffering from acute chills or sinus congestion. Do not ingest without guidance. "
            "Common Misconceptions: Many believe that applying Bhringraj oil once will instantly stop hair fall. Hair rejuvenation is a gradual process, and consistent application over 4-8 weeks is usually necessary to see results."
        ),
    },
    {
        "source": "fenugreek_monograph",
        "plant": "Fenugreek",
        "content": (
            "Fenugreek (Trigonella foenum-graecum), of the family Fabaceae, is an annual Mediterranean herb producing slender pods with aromatic, yellowish-brown seeds. "
            "Medicinal Uses: The seeds are rich in mucilage and soluble fiber, which help regulate blood sugar levels in type 2 diabetes by slowing digestion. It is also a well-known galactagogue, stimulating milk production in lactating mothers, and aids in digestion. "
            "Preparation Methods: Seeds are soaked in water overnight and consumed raw, or ground into a powder. Soaked seed water can be drank as tea. "
            "Precautions: Fenugreek can lower blood sugar; monitor glucose if taking diabetic medicines. It may cause mild digestive side effects like bloating or gas in high doses. Avoid large therapeutic amounts during pregnancy as it may stimulate uterine contractions. "
            "Common Misconceptions: Some think that fenugreek will immediately cause dramatic weight loss. While the soluble fiber supports satiety and digestion, it is not a direct fat-burning agent."
        ),
    }
]


def build_index() -> None:
    """Build the FAISS vector index from sample documents."""
    print("=" * 60)
    print("Building FAISS Vector Index")
    print("=" * 60)

    # 1. Initialise services
    print("\n1. Loading embedding model...")
    t0 = time.time()
    emb_service = get_embedding_service()
    print(f"   Model loaded in {time.time() - t0:.1f}s (dim={emb_service.dimension})")

    # 2. Chunk documents
    print("\n2. Chunking documents...")
    all_chunks: list[str] = []
    all_metadatas: list[dict] = []
    all_ids: list[str] = []

    for doc in PLANT_DOCUMENTS:
        chunks = EmbeddingService.chunk_text(doc["content"], chunk_size=750, overlap=100)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadatas.append({
                "source": doc["source"],
                "plant": doc["plant"],
                "chunk_index": i,
                "total_chunks": len(chunks),
            })
            all_ids.append(f"{doc['source']}_chunk_{i}")

    print(f"   {len(PLANT_DOCUMENTS)} documents -> {len(all_chunks)} chunks")

    # 3. Generate embeddings
    print("\n3. Generating embeddings...")
    t0 = time.time()
    embeddings = emb_service.embed_documents(all_chunks)
    print(f"   {len(embeddings)} embeddings in {time.time() - t0:.1f}s")

    # 4. Build index
    print("\n4. Building FAISS index...")
    store = VectorStoreService(
        persist_directory="./data/embeddings",
        collection_name="medicinal_plants",
    )
    store.create_index(embeddings, all_chunks, all_metadatas, all_ids)
    print(f"   Index saved: {store.index_path}")
    print(f"   Metadata saved: {store.metadata_path}")

    # 5. Verify with a test query
    print("\n5. Verification search...")
    q_emb = emb_service.embed_text("What are the medicinal uses of Tulsi?")
    results = store.search(q_emb, n_results=3)
    for i, r in enumerate(results):
        meta = r["metadata"]
        print(f"   [{i+1}] {meta['plant']} (score={r['score']:.4f}): {r['document'][:80]}...")

    print(f"\n{'=' * 60}")
    print(f"Index built successfully: {store.count} chunks indexed")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    build_index()
