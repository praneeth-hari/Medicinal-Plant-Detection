"""
Seed Medicinal Plants
=====================
Script to seed the SQLite database with 10 core medicinal plants.
"""
from __future__ import annotations

import asyncio
import sys
import os

# Append current directory to sys.path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.future import select
from config.database import async_session_maker
from models.plant import Plant

PLANTS_SEED_DATA = [
    {
        "common_name": "Tulsi",
        "scientific_name": "Ocimum tenuiflorum",
        "family": "Lamiaceae",
        "description": "Also known as Holy Basil, Tulsi is a sacred aromatic herb in Indian culture, widely used in traditional medicine for its adaptogenic, anti-inflammatory, and antimicrobial properties.",
        "medicinal_uses": "Used for respiratory infections, stress management, immune boosting, fever reduction, and digestive health.",
        "habitat": "Grows widely in tropical and subtropical regions of Asia, commonly cultivated in Indian households and gardens.",
        "preparation_methods": "Infusion (Tulsi tea) made by boiling leaves in water, fresh leaf juice, or chewing raw leaves.",
        "precautions": "May lower blood sugar levels. Avoid excessive use during pregnancy and before surgeries due to potential mild blood-thinning properties.",
        "image_url": "https://images.unsplash.com/photo-1600880292089-90a7e086ee0c?w=640&auto=format&fit=crop"
    },
    {
        "common_name": "Neem",
        "scientific_name": "Azadirachta indica",
        "family": "Meliaceae",
        "description": "Known as the 'village pharmacy', Neem is a fast-growing evergreen tree famous for its exceptionally bitter leaves and extensive antiseptic, antifungal, and antiviral qualities.",
        "medicinal_uses": "Used for skin disorders (acne, eczema), wound healing, dental hygiene, immune enhancement, and blood purification.",
        "habitat": "Native to the Indian subcontinent, thriving in dry, hot climates and sandy soils.",
        "preparation_methods": "Neem leaf paste for topical application, decoction of boiled leaves, neem oil extracts, or neem twigs for teeth cleaning.",
        "precautions": "Extremely bitter. Excessive internal consumption can lead to liver or kidney strain. Avoid in infants and pregnant women.",
        "image_url": "https://images.unsplash.com/photo-1585814611803-6d8f4b5a9dcc?w=640&auto=format&fit=crop"
    },
    {
        "common_name": "Ashwagandha",
        "scientific_name": "Withania somnifera",
        "family": "Solanaceae",
        "description": "Ashwagandha, or Indian Ginseng, is a prominent adaptogenic shrub whose root extracts are highly valued in Ayurveda for countering physical and mental stress.",
        "medicinal_uses": "Reducing anxiety and stress, boosting stamina and energy levels, improving sleep quality, and strengthening immunity.",
        "habitat": "Thrives in dry, subtropical regions of India, the Middle East, and parts of Africa.",
        "preparation_methods": "Root powder mixed with warm milk or honey, or consumed as standardized capsule extracts.",
        "precautions": "May stimulate thyroid hormones. Avoid during pregnancy as large doses can trigger uterine contractions.",
        "image_url": "https://images.unsplash.com/photo-1611241893603-3c359704e0ee?w=640&auto=format&fit=crop"
    },
    {
        "common_name": "Aloe Vera",
        "scientific_name": "Aloe barbadensis miller",
        "family": "Asphodelaceae",
        "description": "A succulent plant species with thick, fleshy green leaves containing a cooling gelatinous substance widely prized for skin care and digestive healing.",
        "medicinal_uses": "Soothes burns, sunburns, and skin wounds; aids in digestion and alleviates occasional constipation; hydrates skin.",
        "habitat": "Grows in arid and semi-arid climates, widely cultivated as a potted ornamental and medicinal crop globally.",
        "preparation_methods": "Fresh inner leaf gel applied topically, or diluted inner gel juice consumed orally.",
        "precautions": "Avoid consuming the yellow latex (aloin) layer right under the leaf skin, as it acts as a harsh laxative and can cause severe abdominal cramping.",
        "image_url": "https://images.unsplash.com/photo-1509423350716-97f9360b4e09?w=640&auto=format&fit=crop"
    },
    {
        "common_name": "Brahmi",
        "scientific_name": "Bacopa monnieri",
        "family": "Plantaginaceae",
        "description": "A creeping, perennial herb that grows in wet, marshy environments. Highly regarded as a cognitive enhancer ('medhya rasayana') in traditional medicine.",
        "medicinal_uses": "Enhancing memory and cognitive functions, reducing anxiety and mental fatigue, and improving concentration.",
        "habitat": "Wet wetlands, shallow waters, and marshy shores of tropical regions globally.",
        "preparation_methods": "Leaf juice, infusion of dried herb, or dried herb powder mixed with clarified butter (ghee).",
        "precautions": "May cause mild stomach upset or nausea if consumed on an empty stomach. Standard precautions apply for pregnant women.",
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=640&auto=format&fit=crop"
    },
    {
        "common_name": "Turmeric",
        "scientific_name": "Curcuma longa",
        "family": "Zingiberaceae",
        "description": "A rhizomatous herbaceous plant containing curcumin, a yellow pigment with outstanding antioxidant, anti-inflammatory, and healing capabilities.",
        "medicinal_uses": "Treating joint pain and arthritis inflammation, boosting digestive health, cleansing wounds, and supporting cardiovascular health.",
        "habitat": "Requires warm temperatures and significant annual rainfall to thrive; widely cultivated in Southern Asia.",
        "preparation_methods": "Rhizome powder used in culinary dishes, mixed with warm milk (golden milk), or applied topically as a paste.",
        "precautions": "Generally safe, but therapeutic doses should be avoided by individuals with gallstones or bile duct obstructions.",
        "image_url": "https://images.unsplash.com/photo-1615485500704-8e990f9900f7?w=640&auto=format&fit=crop"
    },
    {
        "common_name": "Amla",
        "scientific_name": "Phyllanthus emblica",
        "family": "Phyllanthaceae",
        "description": "Also known as Indian Gooseberry, Amla is a deciduous tree yielding translucent green round fruits that are one of the richest natural sources of Vitamin C.",
        "medicinal_uses": "Boosts immunity, aids digestion, acts as a potent antioxidant, and promotes hair and skin vitality.",
        "habitat": "Grows throughout subtropical forests in India and neighboring Asian countries.",
        "preparation_methods": "Fresh juice of fruits, dried fruit powder, or consumed raw/pickled.",
        "precautions": "High acidity may cause discomfort in individuals prone to acid reflux. Mild antiplatelet effects.",
        "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=640&auto=format&fit=crop"
    },
    {
        "common_name": "Mint",
        "scientific_name": "Mentha spicata",
        "family": "Lamiaceae",
        "description": "A popular aromatic perennial herb containing menthol, widely recognized for its cooling sensation, digestive relief, and refreshing scent.",
        "medicinal_uses": "Alleviating indigestion, nausea, gas, and irritable bowel syndrome; soothing minor tension headaches when applied as oil.",
        "habitat": "Prefers damp soils and partial shade, spreading rapidly in temperate climates.",
        "preparation_methods": "Infusion of fresh leaves (mint tea), essential oil inhalations, or fresh leaf paste.",
        "precautions": "May worsen symptoms of gastroesophageal reflux disease (GERD) by relaxing the lower esophageal sphincter.",
        "image_url": "https://images.unsplash.com/photo-1628556270448-4d4e4148e1b1?w=640&auto=format&fit=crop"
    },
    {
        "common_name": "Curry Leaves",
        "scientific_name": "Murraya koenigii",
        "family": "Rutaceae",
        "description": "An aromatic tropical tree whose highly scented leaves are staple ingredients in South Asian cuisine and are traditionally used to manage blood sugar and hair health.",
        "medicinal_uses": "Supporting digestion, lowering blood glucose levels, boosting hair growth/strength, and exhibiting antioxidant activity.",
        "habitat": "Native to India and Sri Lanka, grows in subtropical and tropical climates.",
        "preparation_methods": "Raw leaves added to foods, boiled infusion of leaves, or leaves infused in hair oils.",
        "precautions": "Generally extremely safe in food amounts. Ensure seeds are discarded as they are toxic.",
        "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=640&auto=format&fit=crop"
    },
    {
        "common_name": "Hibiscus",
        "scientific_name": "Hibiscus rosa-sinensis",
        "family": "Malvaceae",
        "description": "A showy, tropical evergreen shrub famous for its vibrant trumpet-shaped flowers, widely used in teas and hair care formulations.",
        "medicinal_uses": "Regulating high blood pressure, strengthening hair roots, cooling the body, and providing rich antioxidants.",
        "habitat": "Cultivated extensively as an ornamental plant in tropical and subtropical regions.",
        "preparation_methods": "Tea infusion of dried red petals, or flower/leaf paste used as a hair mask.",
        "precautions": "Large medicinal doses may lower blood pressure significantly. Consult a physician if taking antihypertensive drugs.",
        "image_url": "https://images.unsplash.com/photo-1597848212624-a19eb35e2651?w=640&auto=format&fit=crop"
    },
    {
        "common_name": "Ginger",
        "scientific_name": "Zingiber officinale",
        "family": "Zingiberaceae",
        "description": "A warm, pungent herbaceous perennial whose underground rhizome is globally renowned as a spice and digestive remedy.",
        "medicinal_uses": "Alleviates nausea, morning sickness, motion sickness, digestive distress, and exhibits anti-inflammatory effects for arthritis.",
        "habitat": "Prefers warm, humid, tropical regions with rich, well-draining soil and partial shade.",
        "preparation_methods": "Decoction (ginger tea) of fresh rhizome slices, powdered rhizome capsules, or fresh ginger juice.",
        "precautions": "May exhibit mild antiplatelet effects. Avoid large doses if taking blood thinners or prior to major surgery.",
        "image_url": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?w=640&auto=format&fit=crop"
    },
    {
        "common_name": "Garlic",
        "scientific_name": "Allium sativum",
        "family": "Amaryllidaceae",
        "description": "A bulbous flowering plant closely related to onions, chives, and leeks, containing allicin which delivers robust antimicrobial and cardiovascular benefits.",
        "medicinal_uses": "Regulates blood pressure and cholesterol levels, supports immune response against common colds, and acts as a natural antioxidant.",
        "habitat": "Native to Central Asia and northeastern Iran, widely cultivated in temperate and subtropical climates.",
        "preparation_methods": "Raw crushed cloves, garlic oil infusion, or standardized aged garlic extract tablets.",
        "precautions": "Can cause bad breath and body odor. May increase risk of bleeding when taken with anticoagulants. May irritate gastrointestinal tract if consumed raw in excess.",
        "image_url": "https://images.unsplash.com/photo-1501200291289-c5a76c232e5f?w=640&auto=format&fit=crop"
    },
    {
        "common_name": "Moringa",
        "scientific_name": "Moringa oleifera",
        "family": "Moringaceae",
        "description": "Often called the 'drumstick tree' or 'miracle tree', Moringa is a fast-growing, drought-resistant tree highly valued for its nutrient-rich leaves and anti-inflammatory properties.",
        "medicinal_uses": "Enhances nutritional intake, fights fatigue, lowers blood sugar and cholesterol, and provides potent antioxidant support.",
        "habitat": "Native to northwestern India, widely cultivated in tropical and subtropical regions of Asia, Africa, and South America.",
        "preparation_methods": "Dried leaf powder in capsules or smoothies, fresh leaves cooked as a vegetable, or seed oil.",
        "precautions": "Avoid consuming root extracts as they may contain toxic alkaloids. Consult a doctor during pregnancy due to potential uterine contractions.",
        "image_url": "https://images.unsplash.com/photo-1591381245185-c3cae4be0e71?w=640&auto=format&fit=crop"
    },
    {
        "common_name": "Lemongrass",
        "scientific_name": "Cymbopogon citratus",
        "family": "Poaceae",
        "description": "A tall, perennial grass with a fresh, lemony scent, widely used as a culinary herb and in essential oil aromatherapy.",
        "medicinal_uses": "Relieves digestive spasms, bloating, and stomach aches; reduces fever; exhibits mild sedative and anti-anxiety effects.",
        "habitat": "Tropical regions of Asia, particularly India and Southeast Asia, thriving in full sun and moist, sandy loam soils.",
        "preparation_methods": "Hot water infusion (lemongrass tea) of fresh or dried stalks, or essential oil aromatherapy.",
        "precautions": "Essential oil must be diluted in carrier oil before skin application to avoid contact dermatitis. Avoid internal consumption of essential oil.",
        "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=640&auto=format&fit=crop"
    },
    {
        "common_name": "Shatavari",
        "scientific_name": "Asparagus racemosus",
        "family": "Asparagaceae",
        "description": "A climbing species of asparagus native to India, renowned as a rejuvenating female tonic for supporting reproductive health and vitality.",
        "medicinal_uses": "Acts as a galactagogue to promote lactation; balances female hormones; acts as a cooling demulcent for stomach ulcers.",
        "habitat": "Tropical and subtropical regions of India, growing in rocky, gravelly soils and shaded forest areas.",
        "preparation_methods": "Root powder mixed with warm milk and honey, or root extracts in capsule form.",
        "precautions": "Mild diuretic properties. Avoid if you have a known allergy to asparagus species or severe kidney congestion.",
        "image_url": "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=640&auto=format&fit=crop"
    },
    {
        "common_name": "Giloy",
        "scientific_name": "Tinospora cordifolia",
        "family": "Menispermaceae",
        "description": "A large, deciduous climbing shrub known as 'Amrita' (the root of immortality) due to its highly potent immunomodulatory and antipyretic properties.",
        "medicinal_uses": "Reduces chronic fevers, enhances immune response, helps regulate blood sugar, and acts as an adaptogen to reduce stress.",
        "habitat": "Throughout tropical regions of India, climbing up large trees in dry forests.",
        "preparation_methods": "Decoction of the stem (Giloy Kwath), stem juice, or extract capsules/tablets.",
        "precautions": "May lower blood glucose; monitor levels if on antidiabetic drugs. May stimulate immune system, so exercise caution with autoimmune conditions.",
        "image_url": "https://images.unsplash.com/photo-1592502712628-10d5d7f1ca6b?w=640&auto=format&fit=crop"
    },
    {
        "common_name": "Arjuna",
        "scientific_name": "Terminalia arjuna",
        "family": "Combretaceae",
        "description": "A large deciduous tree whose pinkish-grey bark is highly revered in traditional medicine as a cardioprotective agent.",
        "medicinal_uses": "Strengthens cardiac muscles, improves blood circulation, manages hypertension, and helps maintain healthy cholesterol levels.",
        "habitat": "Native to the Indian subcontinent, commonly found growing along riverbanks and dry river beds.",
        "preparation_methods": "Bark powder boiled in water or milk (Arjuna Ksheera Pak), or bark extract capsules.",
        "precautions": "Use under medical supervision if taking pharmaceutical cardiac drugs. Not recommended during pregnancy.",
        "image_url": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=640&auto=format&fit=crop"
    },
    {
        "common_name": "Bael",
        "scientific_name": "Aegle marmelos",
        "family": "Rutaceae",
        "description": "A sacred tree native to India, yielding large, hard-shelled fruits with aromatic, orange pulp rich in tannins and pectin, ideal for digestive disorders.",
        "medicinal_uses": "Highly effective for treating diarrhea, dysentery, IBS, and flatulence; exhibits antimicrobial and gastroprotective properties.",
        "habitat": "Dry, open forests of India, Nepal, and Southeast Asia, highly drought-resistant.",
        "preparation_methods": "Fruit pulp consumed fresh, dried fruit slice decoction, or fruit powder mixed with water or yogurt.",
        "precautions": "Consuming ripe fruit in large quantities may cause constipation. Avoid excessive consumption of bark/leaves during pregnancy.",
        "image_url": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=640&auto=format&fit=crop"
    },
    {
        "common_name": "Bhringraj",
        "scientific_name": "Eclipta prostrata",
        "family": "Asteraceae",
        "description": "A creeping herb with small white flowers, widely celebrated in traditional medicine as the 'king of hair' due to its powerful hair growth and liver supporting traits.",
        "medicinal_uses": "Promotes hair growth, prevents premature greying, supports liver detoxification, and aids in skin healing.",
        "habitat": "Commonly found in wet, waste areas and marshy lands throughout tropical and subtropical countries.",
        "preparation_methods": "Hair oil infusion of leaf juices, leaf paste for topical application, or juice of fresh leaves.",
        "precautions": "May cause a cooling sensation; use with caution if prone to chills. Avoid internal use during pregnancy.",
        "image_url": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=640&auto=format&fit=crop"
    },
    {
        "common_name": "Fenugreek",
        "scientific_name": "Trigonella foenum-graecum",
        "family": "Fabaceae",
        "description": "An annual Mediterranean herb producing slender pods with aromatic, yellowish-brown seeds rich in soluble fiber and saponins.",
        "medicinal_uses": "Regulates blood glucose levels in diabetes, stimulates breast milk production, improves digestion, and supports cholesterol reduction.",
        "habitat": "Native to Southern Europe and Western Asia, widely cultivated in dry, semi-arid regions.",
        "preparation_methods": "Soaked seeds consumed raw, seed powder mixed with water, or tea infusion of seeds.",
        "precautions": "May lower blood sugar and interact with diabetic medicines. Can cause mild flatulence or diarrhea in sensitive individuals.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=640&auto=format&fit=crop"
    }
]

async def seed_plants():
    print("Connecting to database...")
    async with async_session_maker() as session:
        for plant_data in PLANTS_SEED_DATA:
            # Check if plant already exists to avoid duplicates
            query = select(Plant).where(Plant.scientific_name == plant_data["scientific_name"])
            res = await session.execute(query)
            existing = res.scalars().first()
            if existing:
                for key, value in plant_data.items():
                    setattr(existing, key, value)
                print(f"Updating {plant_data['common_name']}...")
                continue

            plant = Plant(**plant_data)
            session.add(plant)
            print(f"Seeding {plant_data['common_name']}...")
        
        await session.commit()
    print("Database seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed_plants())
