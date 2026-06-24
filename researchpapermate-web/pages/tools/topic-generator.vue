<script setup lang="ts">
useSeoMeta({
  title: 'Free Essay Topic Generator — Get Ideas for Any Subject',
  description: 'Generate 8 specific essay topic ideas for any subject and essay type. Choose from 16 subjects and 7 essay types. Free, instant, no sign-up required.',
})

type Subject =
  | 'Psychology'
  | 'Sociology'
  | 'History'
  | 'Literature & English'
  | 'Business & Management'
  | 'Technology & Computer Science'
  | 'Environmental Science'
  | 'Political Science'
  | 'Philosophy'
  | 'Education'
  | 'Health & Medicine'
  | 'Economics'
  | 'Law'
  | 'Art & Music'
  | 'Biology'
  | 'Chemistry & Physics'

type EssayType =
  | 'Argumentative'
  | 'Analytical'
  | 'Compare & Contrast'
  | 'Cause & Effect'
  | 'Expository'
  | 'Persuasive'
  | 'Research Paper'

type Level = 'High School' | 'Undergraduate' | 'Graduate'

const SUBJECTS: Subject[] = [
  'Psychology', 'Sociology', 'History', 'Literature & English',
  'Business & Management', 'Technology & Computer Science', 'Environmental Science',
  'Political Science', 'Philosophy', 'Education', 'Health & Medicine',
  'Economics', 'Law', 'Art & Music', 'Biology', 'Chemistry & Physics',
]
const ESSAY_TYPES: EssayType[] = [
  'Argumentative', 'Analytical', 'Compare & Contrast', 'Cause & Effect',
  'Expository', 'Persuasive', 'Research Paper',
]
const LEVELS: Level[] = ['High School', 'Undergraduate', 'Graduate']

// ── TOPIC BANK ────────────────────────────────────────────────────────────────
// Record<Subject, Record<EssayType, string[]>>
// Each array has 10 entries; 8 will be shown per generation cycle.
const TOPICS: Record<Subject, Record<EssayType, string[]>> = {
  'Psychology': {
    'Argumentative': [
      'Social media use is a primary driver of anxiety and depression in adolescents',
      'Childhood trauma permanently alters adult attachment styles',
      'Cognitive behavioural therapy is more effective than medication for treating mild depression',
      'The bystander effect explains widespread inaction in modern-day emergencies',
      'Standardised testing fails to capture true student intelligence',
      'Implicit bias in hiring decisions perpetuates systemic inequality',
      'Violent video games do not cause real-world aggression in most players',
      'The pharmaceutical industry over-medicalises normal human emotions',
      'Parenting styles have a greater influence on personality than genetic factors',
      'Mindfulness-based interventions should be standard practice in mental health treatment',
    ],
    'Analytical': [
      'An analysis of Milgram\'s obedience experiments and their implications for authority',
      'Examining the role of unconscious bias in clinical diagnosis',
      'How attachment theory explains romantic relationship patterns in adulthood',
      'The psychological mechanisms underlying confirmation bias in political discourse',
      'Analysing the effectiveness of exposure therapy for phobia treatment',
      'The interplay between neuroplasticity and trauma recovery in clinical populations',
      'How cognitive dissonance theory explains self-justifying behaviour in moral lapses',
      'Examining Maslow\'s hierarchy of needs as a framework for organisational motivation',
      'The role of social identity theory in intergroup conflict and prejudice',
      'Analysing the long-term psychological effects of solitary confinement',
    ],
    'Compare & Contrast': [
      'Freudian psychoanalysis vs cognitive behavioural therapy in treating anxiety disorders',
      'Intrinsic motivation vs extrinsic motivation in academic achievement',
      'Classical conditioning vs operant conditioning in behaviour modification',
      'Individual therapy vs group therapy for treating social anxiety',
      'Nature vs nurture in the development of personality disorders',
      'Western psychological models vs Indigenous healing practices',
      'Positive psychology vs traditional deficit-focused psychology',
      'Self-report measures vs neuroimaging in studying emotion regulation',
      'Authoritative parenting vs authoritarian parenting and child outcomes',
      'Short-term vs long-term memory consolidation mechanisms',
    ],
    'Cause & Effect': [
      'The causes and effects of chronic stress on hippocampal volume and memory',
      'The causes and effects of sleep deprivation on executive functioning',
      'The causes and effects of early childhood neglect on emotional regulation',
      'The causes and effects of social isolation on cognitive decline in elderly adults',
      'The causes and effects of smartphone overuse on adolescent attention spans',
      'The causes and effects of workplace burnout on long-term career trajectories',
      'The causes and effects of perfectionism on academic and professional performance',
      'The causes and effects of trauma exposure on the development of PTSD',
      'The causes and effects of positive reinforcement on intrinsic learning motivation',
      'The causes and effects of peer pressure on adolescent risk-taking behaviour',
    ],
    'Expository': [
      'An examination of how the human brain processes fear and threat responses',
      'An examination of the stages of grief as described in Kübler-Ross\'s model',
      'An examination of how operant conditioning shapes everyday human behaviour',
      'An examination of the main theories explaining the psychology of persuasion',
      'An examination of how memory consolidation occurs during REM sleep',
      'An examination of the psychological principles underlying effective leadership',
      'An examination of emotional intelligence and its components',
      'An examination of how cognitive load theory informs instructional design',
      'An examination of the psychological basis of placebo effects in clinical trials',
      'An examination of self-efficacy theory and its applications in education',
    ],
    'Persuasive': [
      'Schools should incorporate mental health literacy into core curricula',
      'Employers must provide mandatory mental health days as part of employee benefits',
      'Social media platforms should be legally required to protect adolescent mental health',
      'Prison systems should prioritise psychological rehabilitation over punitive measures',
      'Therapy should be covered in full by national health insurance programmes',
      'Psychology-informed policies are essential for reducing recidivism rates',
      'Mandatory workplace mental health screenings would save lives and reduce costs',
      'Universities should provide free unlimited counselling sessions to all students',
      'Advertising standards should prohibit campaigns that exploit psychological vulnerabilities',
      'Early childhood trauma intervention programmes deserve greater government funding',
    ],
    'Research Paper': [
      'The neurobiological basis of addiction: dopamine pathways and reward circuitry',
      'Predictors of treatment dropout in cognitive behavioural therapy for depression',
      'The relationship between childhood adversity scores and adult chronic illness',
      'Cross-cultural differences in the expression and recognition of basic emotions',
      'The efficacy of EMDR therapy compared to prolonged exposure therapy in PTSD',
      'Psychological factors mediating the relationship between poverty and academic achievement',
      'The role of self-compassion in recovery from eating disorders: a systematic review',
      'Attentional bias modification as an intervention for generalised anxiety disorder',
      'The impact of parental mental illness on child psychological development outcomes',
      'Social network analysis of isolation patterns in individuals with social anxiety disorder',
    ],
  },

  'Sociology': {
    'Argumentative': [
      'Systemic racism, not individual prejudice, is the primary driver of racial inequality',
      'Social media accelerates the fragmentation of shared community identity',
      'Economic inequality is a more powerful predictor of crime than cultural factors',
      'Gender pay gaps persist primarily due to structural discrimination, not individual choice',
      'The nuclear family model is no longer a valid framework for modern social policy',
      'Gentrification invariably harms the existing residents of urban communities',
      'Mass incarceration functions as a form of racial social control in the United States',
      'Globalisation has deepened rather than reduced social inequality worldwide',
      'Religion remains a primary source of social cohesion in secular societies',
      'Universal basic income would fundamentally reshape social class dynamics',
    ],
    'Analytical': [
      'Analysing Bourdieu\'s concept of cultural capital in educational attainment disparities',
      'How Goffman\'s dramaturgical framework explains identity performance in digital spaces',
      'Examining the sociology of deviance through the lens of labelling theory',
      'The role of social institutions in reproducing class inequality across generations',
      'Analysing food deserts as a product of spatial inequality and institutional neglect',
      'How intersectionality theory complicates single-axis frameworks of discrimination',
      'The sociological dimensions of moral panic in media representations of youth crime',
      'Examining migration as a structural response to global economic asymmetries',
      'How Durkheim\'s concept of anomie explains social cohesion breakdown in modern cities',
      'The role of social movements in reshaping normative gender expectations',
    ],
    'Compare & Contrast': [
      'Structural functionalism vs conflict theory in explaining social inequality',
      'Formal social control mechanisms vs informal social control mechanisms',
      'Urban community solidarity vs suburban social atomisation',
      'Social mobility in the United States vs social mobility in Scandinavian countries',
      'Collectivist societies vs individualist societies in managing social welfare',
      'Traditional gender role socialisation vs contemporary gender-fluid socialisation',
      'Integration policies in Europe vs multiculturalism policies in Canada',
      'Digital social networks vs face-to-face community in fostering civic engagement',
      'Symbolic interactionism vs structural sociology in explaining everyday behaviour',
      'Social stratification in feudal societies vs contemporary class systems',
    ],
    'Cause & Effect': [
      'The causes and effects of residential segregation on educational opportunity gaps',
      'The causes and effects of social media echo chambers on political polarisation',
      'The causes and effects of deindustrialisation on working-class community cohesion',
      'The causes and effects of mass urbanisation on traditional family structures',
      'The causes and effects of social stigma on mental health help-seeking behaviour',
      'The causes and effects of digital surveillance capitalism on social trust',
      'The causes and effects of immigration waves on host country labour market dynamics',
      'The causes and effects of declining union membership on wage inequality',
      'The causes and effects of single-parent household prevalence on child outcomes',
      'The causes and effects of third-wave feminism on workplace policy reforms',
    ],
    'Expository': [
      'An examination of how social norms are created, maintained, and enforced',
      'An examination of the sociological dimensions of poverty in post-industrial cities',
      'An examination of how identity is constructed through social interaction',
      'An examination of the key theoretical contributions of Max Weber to social theory',
      'An examination of how race is socially constructed rather than biologically fixed',
      'An examination of the sociology of religion and its role in modern life',
      'An examination of how social capital shapes access to resources and opportunity',
      'An examination of the main types of social mobility and the barriers to each',
      'An examination of how social media has changed public sphere dynamics',
      'An examination of secondary socialisation and its role in identity formation',
    ],
    'Persuasive': [
      'Housing policy must address structural racism to close the racial wealth gap',
      'Universal pre-kindergarten is a sociological necessity, not a luxury',
      'The criminal justice system must be redesigned around rehabilitation and restorative justice',
      'Corporate diversity programmes must move beyond symbolic gestures to structural change',
      'Educational curricula should include critical race theory to address historical inequities',
      'Social workers need stronger legal protections to serve marginalised communities effectively',
      'The gig economy exploits workers and must be regulated as standard employment',
      'Schools should eliminate zero-tolerance discipline policies that disproportionately harm minority students',
      'Community-based violence prevention programmes outperform policing in reducing crime',
      'Governments must legislate wage transparency to narrow structural pay inequality',
    ],
    'Research Paper': [
      'Socioeconomic determinants of food insecurity in urban versus rural communities',
      'The relationship between neighbourhood poverty concentration and educational attainment',
      'Social media use and its effects on political participation among Generation Z',
      'Racial disparities in maternal mortality rates and the role of implicit bias in healthcare',
      'The sociology of homelessness: structural pathways and service system responses',
      'Gender socialisation in early childhood: a content analysis of contemporary children\'s media',
      'The impact of mass incarceration on Black family structures in the United States',
      'Social capital and its mediating role in immigrant economic integration outcomes',
      'Intersectionality of race, class, and gender in occupational segregation patterns',
      'The sociology of conspiracy theory adoption in low-trust institutional environments',
    ],
  },

  'History': {
    'Argumentative': [
      'The atomic bombings of Hiroshima and Nagasaki were not militarily necessary',
      'Colonial powers bear ongoing moral and financial responsibility for post-colonial instability',
      'The Treaty of Versailles was the primary cause of the rise of Nazism in Germany',
      'The transatlantic slave trade was the foundational driver of Western economic development',
      'The Cold War was primarily caused by American imperial ambitions, not Soviet aggression',
      'Christopher Columbus\'s legacy should be re-evaluated as one of exploitation, not discovery',
      'The Industrial Revolution increased human suffering before it created widespread prosperity',
      'The Roman Empire\'s fall was caused more by internal decay than external pressure',
      'The French Revolution failed to achieve its core ideals of liberty, equality, and fraternity',
      'Appeasement policies toward Hitler were reasonable given the constraints of 1930s diplomacy',
    ],
    'Analytical': [
      'Analysing the role of propaganda in sustaining public support for World War I',
      'How economic interests shaped British imperial policy in India during the 19th century',
      'Examining the historiography of the American Civil War and its contested legacies',
      'The role of gender in determining participation and exclusion from the French Revolution',
      'How the Black Death reshaped European social and economic structures in the 14th century',
      'Analysing the ideological contradictions within the American founding documents',
      'The role of trade routes in facilitating cultural exchange in the medieval Islamic world',
      'How the Enlightenment both enabled and constrained the anti-slavery movement',
      'Examining the Ottoman Empire\'s decline through administrative, military, and economic lenses',
      'The role of technological change in shifting military strategy during World War II',
    ],
    'Compare & Contrast': [
      'The American Revolution vs the French Revolution: causes, methods, and outcomes',
      'The Roman Empire vs the British Empire in governance, expansion, and decline',
      'Fascism in Italy under Mussolini vs National Socialism under Hitler',
      'The causes and conduct of World War I vs World War II',
      'Gandhi\'s non-violent resistance vs Mandela\'s evolving strategy in South Africa',
      'The Bolshevik Revolution vs the Chinese Communist Revolution',
      'The Reconquista in Spain vs the Crusades in the Middle East',
      'Ottoman administrative methods vs British colonial methods in the Middle East',
      'The Korean War vs the Vietnam War: strategy, outcome, and American public response',
      'Indigenous resistance to colonialism in the Americas vs in sub-Saharan Africa',
    ],
    'Cause & Effect': [
      'The causes and effects of the Black Death on European feudal society and labour relations',
      'The causes and effects of the printing press on religious reformation in Europe',
      'The causes and effects of the Great Depression on global political stability',
      'The causes and effects of the partition of India on the subcontinent\'s political geography',
      'The causes and effects of the Haitian Revolution on Atlantic slavery debates',
      'The causes and effects of the Berlin Wall\'s construction on East-West Cold War dynamics',
      'The causes and effects of the Opium Wars on Chinese sovereignty and nationalism',
      'The causes and effects of the 1973 oil crisis on Western economic and energy policy',
      'The causes and effects of decolonisation on intra-African border conflicts',
      'The causes and effects of the Meiji Restoration on Japan\'s emergence as a world power',
    ],
    'Expository': [
      'An examination of the key factors that enabled the Mongol Empire\'s rapid expansion',
      'An examination of how the Renaissance transformed European thought and artistic production',
      'An examination of the major turning points in the American Civil Rights Movement',
      'An examination of how the Silk Road facilitated economic and cultural exchange',
      'An examination of the main ideological foundations of the Soviet Communist state',
      'An examination of how the Reformation permanently altered the religious landscape of Europe',
      'An examination of the role of women in the resistance movements of World War II',
      'An examination of the primary causes of the collapse of the Roman Western Empire',
      'An examination of how the Marshall Plan shaped post-war European economic recovery',
      'An examination of the historical development of democracy from Athens to modernity',
    ],
    'Persuasive': [
      'Historical education must include Indigenous perspectives alongside settler-colonial narratives',
      'Reparations for the descendants of enslaved people are a moral and economic necessity',
      'Colonial-era artefacts must be returned to their countries of origin',
      'History curricula should present multiple national perspectives, not a single dominant narrative',
      'The legacy of colonialism must inform contemporary foreign aid and development policy',
      'War crimes must be prosecuted regardless of whether the perpetrator won the conflict',
      'Monuments to Confederate leaders must be removed from public spaces',
      'The United Nations needs structural reform to reflect the post-colonial world order',
      'History should be taught as an interpretive discipline, not a set of memorised facts',
      'Governments should issue formal apologies for state-sanctioned historical atrocities',
    ],
    'Research Paper': [
      'The role of economic competition in triggering the First World War: a revisionist analysis',
      'Gender and memory: how women\'s wartime contributions were erased from official histories',
      'The transatlantic slave trade and its demographic effects on West African societies',
      'Propaganda techniques in Nazi Germany: content analysis of Der Stürmer 1933–1938',
      'Decolonisation and state formation in sub-Saharan Africa: comparing Ghana and Congo',
      'The historiography of the Holocaust: from perpetrator-centred to victim-centred accounts',
      'Imperial rivalry and the origins of the Scramble for Africa at the Berlin Conference',
      'The social history of the Industrial Revolution: working conditions and labour activism',
      'Cold War proxy conflicts in Latin America and their long-term democratic implications',
      'The role of disease in the Spanish conquest of the Americas: demographic catastrophe and agency',
    ],
  },

  'Literature & English': {
    'Argumentative': [
      'The Great Gatsby is ultimately a critique of the American Dream, not a celebration of it',
      'Dystopian fiction serves as a more effective social warning than political journalism',
      'Postcolonial literature must be read through an awareness of the language of the coloniser',
      'The literary canon systematically excludes women\'s and minority voices and must be reformed',
      'Shakespeare\'s plays are more relevant to contemporary life than any modern equivalent',
      'The rise of autofiction has blurred the ethical boundary between lived experience and art',
      'Unreliable narrators are more truthful about human experience than omniscient narrators',
      'Toni Morrison\'s Beloved is the definitive American novel on the trauma of slavery',
      'Genre fiction deserves as much critical attention as literary fiction',
      'The death of the author as a critical position overstates the irrelevance of biographical context',
    ],
    'Analytical': [
      'Analysing the function of the green light as a symbol in The Great Gatsby',
      'How Orwell uses the manipulation of language in 1984 to depict totalitarian control',
      'Examining the role of setting as a character in Emily Brontë\'s Wuthering Heights',
      'How Mary Shelley uses the Prometheus myth to interrogate scientific ambition in Frankenstein',
      'The function of silence and absence in Harold Pinter\'s dramatic technique',
      'Analysing the narrative structure of One Hundred Years of Solitude as magical realism',
      'How Virginia Woolf\'s stream-of-consciousness technique constructs subjective experience',
      'Examining feminist subversion in Charlotte Perkins Gilman\'s The Yellow Wallpaper',
      'The role of intertextuality in T.S. Eliot\'s The Waste Land',
      'How Chinua Achebe uses dual narrative perspectives to deconstruct colonial discourse in Things Fall Apart',
    ],
    'Compare & Contrast': [
      'Hamlet vs Macbeth: ambition, hesitation, and moral collapse in Shakespearean tragedy',
      'George Orwell\'s 1984 vs Aldous Huxley\'s Brave New World as dystopian visions',
      'Romanticism vs Realism as literary responses to industrialisation',
      'The unreliable narrator in Gone Girl vs The Tell-Tale Heart',
      'Jane Austen\'s satirical method vs Charles Dickens\'s social critique',
      'Magical realism in Gabriel García Márquez vs Isabel Allende',
      'The hero\'s journey in The Odyssey vs Beowulf',
      'Modernist poetry vs Romantic poetry: form, subject, and the role of the self',
      'Indigenous Australian literature vs Indigenous North American literature in themes of land and identity',
      'Ernest Hemingway\'s minimalism vs William Faulkner\'s maximalism',
    ],
    'Cause & Effect': [
      'The causes and effects of censorship on the development of underground literary movements',
      'The causes and effects of the Harlem Renaissance on African American literary identity',
      'The causes and effects of World War I on the disillusionment visible in modernist literature',
      'The causes and effects of colonialism on the themes of post-colonial Anglophone fiction',
      'The causes and effects of the rise of digital publishing on literary authorship and gatekeeping',
      'The causes and effects of feminist literary criticism on the re-evaluation of the canon',
      'The causes and effects of exile on the creative output of James Joyce and Samuel Beckett',
      'The causes and effects of social media on the reading habits of Generation Z',
      'The causes and effects of the Beat Generation on the content and form of American poetry',
      'The causes and effects of Gothic literature on contemporary horror writing',
    ],
    'Expository': [
      'An examination of the defining characteristics of the Romantic movement in British poetry',
      'An examination of how narrative perspective shapes reader sympathy in crime fiction',
      'An examination of the key features of magical realism and their cultural origins',
      'An examination of how metaphor functions as a vehicle for thematic meaning in poetry',
      'An examination of the role of the antihero in postmodern American fiction',
      'An examination of how the Bildungsroman genre explores identity formation',
      'An examination of the conventions and subversions of the Gothic novel',
      'An examination of how satire functions as social criticism in Jonathan Swift',
      'An examination of the major thematic concerns of post-apartheid South African literature',
      'An examination of how dialect and vernacular voice challenge linguistic authority in literature',
    ],
    'Persuasive': [
      'Reading literary fiction should be a mandatory component of university education',
      'Schools must include more diverse and non-Western texts in English literature curricula',
      'The study of poetry builds critical thinking skills that are irreplaceable by any other form',
      'Publishers have an obligation to amplify underrepresented literary voices',
      'Book banning in schools is an act of political censorship that harms critical development',
      'Literary prizes should include independent and small-press publications on equal footing',
      'Students should have the right to study contemporary literature alongside classical texts',
      'Graphic novels deserve institutional recognition as a legitimate literary form',
      'Libraries must remain publicly funded as essential institutions for literary democracy',
      'Translation matters: the world\'s best literature is being lost in English-language markets',
    ],
    'Research Paper': [
      'Ecocriticism and climate anxiety in contemporary British fiction 2010–2025',
      'The representation of mental illness in confessional poetry: Plath, Sexton, and Lowell',
      'Narrative identity and trauma in Caribbean women\'s autobiographical fiction',
      'Disability as metaphor versus disability as identity in Victorian and neo-Victorian fiction',
      'The politics of translation: whose stories get told in the Anglophone literary marketplace',
      'Queer temporality and non-linear narrative in contemporary LGBTQ+ fiction',
      'The function of silence in post-Holocaust literature: Wiesel, Levi, and Kertész',
      'Afrofuturism as genre and politics in contemporary African American speculative fiction',
      'Intertextuality in postmodern fiction: Borges, Calvino, and the reflexive text',
      'The economics of literary prestige: how cultural capital is assigned to canonical texts',
    ],
  },

  'Business & Management': {
    'Argumentative': [
      'Corporate social responsibility is primarily a reputational strategy, not genuine ethics',
      'Remote work permanently improves productivity and should replace office-first policies',
      'Shareholder primacy is a flawed doctrine that harms stakeholders and long-term value',
      'Gig economy platforms must be legally reclassified as employers, not marketplaces',
      'Diversity quotas in corporate leadership produce better business outcomes',
      'Artificial intelligence will replace middle management within the next decade',
      'Startup culture romanticises overwork and harms employee wellbeing at scale',
      'Flat organisational structures outperform hierarchical ones in innovative industries',
      'Family-owned businesses are more resilient than publicly traded corporations during economic downturns',
      'Environmental, Social, and Governance (ESG) investing is more than a trend — it is the future of capitalism',
    ],
    'Analytical': [
      'Analysing the strategic failures that led to the collapse of Enron Corporation',
      'How Amazon\'s operational efficiency model reshaped global supply chain expectations',
      'Examining the role of organisational culture in Google\'s competitive advantage',
      'An analysis of blue ocean strategy in disrupting established industries',
      'How the balanced scorecard framework improves strategic alignment in large organisations',
      'Examining the principal-agent problem in executive compensation design',
      'The role of emotional intelligence in transformational leadership effectiveness',
      'How disruptive innovation theory explains the rise and fall of Blockbuster vs Netflix',
      'Analysing the strategic rationale behind Apple\'s vertical integration model',
      'The role of organisational ambidexterity in balancing exploration and exploitation',
    ],
    'Compare & Contrast': [
      'Autocratic leadership vs democratic leadership in crisis management contexts',
      'Transactional leadership vs transformational leadership in employee motivation',
      'Startup agile methodology vs corporate waterfall project management',
      'B2B marketing strategy vs B2C marketing strategy: approaches and metrics',
      'Corporate entrepreneurship vs independent entrepreneurship in innovation outcomes',
      'Japanese Kaizen management philosophy vs Western lean management practices',
      'Public sector management vs private sector management in service delivery',
      'Vertical integration strategy vs outsourcing strategy in supply chain management',
      'Intrinsic employee motivation vs extrinsic financial incentives in performance',
      'Western corporate governance models vs East Asian stakeholder-centred models',
    ],
    'Cause & Effect': [
      'The causes and effects of the 2008 financial crisis on corporate governance reform',
      'The causes and effects of digital transformation on brick-and-mortar retail viability',
      'The causes and effects of high employee turnover on organisational knowledge retention',
      'The causes and effects of monopolistic market structures on consumer welfare',
      'The causes and effects of toxic workplace culture on long-term brand equity',
      'The causes and effects of supply chain globalisation on domestic manufacturing employment',
      'The causes and effects of aggressive price competition on industry profit margins',
      'The causes and effects of corporate mergers and acquisitions on innovation capacity',
      'The causes and effects of poor change management on organisational transformation failure',
      'The causes and effects of algorithmic pricing on consumer trust in e-commerce platforms',
    ],
    'Expository': [
      'An examination of Porter\'s Five Forces framework and its application to modern industries',
      'An examination of how organisational learning theory applies to knowledge management',
      'An examination of the main models of corporate social responsibility',
      'An examination of how the marketing mix (4Ps) has evolved in the digital era',
      'An examination of the key drivers of entrepreneurial success in emerging markets',
      'An examination of how change management frameworks guide organisational transitions',
      'An examination of the role of corporate culture in mergers and acquisitions outcomes',
      'An examination of ethical decision-making frameworks in business leadership',
      'An examination of how supply chain resilience is built through diversification',
      'An examination of the theoretical foundations of strategic human resource management',
    ],
    'Persuasive': [
      'Corporations must be legally required to disclose their carbon footprint and reduction targets',
      'Mental health support must become a standard line item in corporate benefits packages',
      'Business schools must integrate ethics and sustainability into every core course',
      'Minimum wage laws should be indexed to inflation to protect worker purchasing power',
      'Companies should be required by law to have at least 40% female representation on boards',
      'Data privacy regulation must keep pace with the expansion of personalised advertising',
      'Small business tax relief is more economically efficient than corporate tax cuts',
      'Algorithmic hiring tools must be independently audited for discriminatory bias',
      'The four-day work week should be adopted as standard across professional industries',
      'Companies that offshore jobs should face import tariffs proportional to employment displacement',
    ],
    'Research Paper': [
      'The relationship between board diversity and firm financial performance: a meta-analysis',
      'Digital leadership competencies in the age of artificial intelligence and organisational change',
      'Corporate greenwashing: measuring the gap between ESG claims and measurable outcomes',
      'The impact of remote work adoption on employee engagement and organisational commitment',
      'Strategic alliances in the pharmaceutical industry: knowledge transfer and competitive dynamics',
      'Venture capital investment patterns and their correlation with startup survival rates',
      'The role of psychological safety in fostering innovation within cross-functional teams',
      'Ethical leadership and its mediating role in reducing unethical employee behaviour',
      'Platform business model scalability: comparing Uber, Airbnb, and Amazon Marketplace',
      'The effect of CEO narcissism on strategic risk-taking and long-term firm performance',
    ],
  },

  'Technology & Computer Science': {
    'Argumentative': [
      'Artificial intelligence poses an existential risk that demands urgent international regulation',
      'Social media algorithms are designed to maximise engagement at the expense of mental health',
      'The right to digital privacy is more fundamental than national security surveillance needs',
      'Open-source software is a more secure and democratising model than proprietary software',
      'Cryptocurrency lacks the fundamental qualities needed to replace fiat currency systems',
      'Facial recognition technology should be banned from public law enforcement use',
      'The digital divide is widening global inequality rather than narrowing it',
      'Automation will not create enough new jobs to offset the roles it eliminates',
      'Big Tech monopolies must be broken up using antitrust law to restore market competition',
      'Algorithmic bias in machine learning systems reflects and amplifies societal discrimination',
    ],
    'Analytical': [
      'Analysing the cybersecurity vulnerabilities created by the Internet of Things ecosystem',
      'How neural network architectures enable large language models to generate coherent text',
      'Examining the ethical frameworks applied in autonomous vehicle decision-making systems',
      'How platform lock-in strategies prevent competition in cloud computing markets',
      'Analysing the role of network effects in determining winner-take-all outcomes in tech markets',
      'Examining the technical and social challenges of achieving robust explainable AI',
      'How zero-day vulnerabilities are discovered, exploited, and patched in cybersecurity practice',
      'Analysing the data governance frameworks of GDPR and CCPA and their enforcement gaps',
      'The role of distributed ledger technology beyond cryptocurrency applications',
      'Examining the ethical implications of predictive policing algorithms',
    ],
    'Compare & Contrast': [
      'Machine learning vs rule-based AI systems in medical diagnostic accuracy',
      'Centralised vs decentralised internet architecture in resilience and censorship resistance',
      'Agile software development methodology vs traditional waterfall in complex projects',
      'Public cloud infrastructure vs on-premise data centres in security and cost',
      'Python vs JavaScript as introductory programming languages for computer science education',
      'Supervised learning vs unsupervised learning approaches in pattern recognition tasks',
      'Open-source operating systems vs proprietary operating systems in enterprise adoption',
      'Social media content moderation by human reviewers vs automated AI systems',
      'Quantum computing vs classical computing in solving optimisation problems',
      'Silicon Valley startup culture vs European tech startup culture in approach and outcomes',
    ],
    'Cause & Effect': [
      'The causes and effects of the Cambridge Analytica data breach on public trust in social media',
      'The causes and effects of automation on middle-skill employment in manufacturing and logistics',
      'The causes and effects of smartphone ubiquity on human spatial memory and navigation',
      'The causes and effects of net neutrality repeal on internet access equity',
      'The causes and effects of dark pattern design on consumer decision-making and autonomy',
      'The causes and effects of ransomware attacks on healthcare infrastructure and patient safety',
      'The causes and effects of algorithmic content recommendation on political radicalisation',
      'The causes and effects of open-source AI model releases on dual-use risk',
      'The causes and effects of data localisation laws on global technology market fragmentation',
      'The causes and effects of the semiconductor shortage on global supply chain vulnerability',
    ],
    'Expository': [
      'An examination of how convolutional neural networks process and classify visual data',
      'An examination of the core principles of zero-trust cybersecurity architecture',
      'An examination of how blockchain technology enables trustless transactions',
      'An examination of the main programming paradigms and their appropriate use cases',
      'An examination of how recommendation algorithms use collaborative filtering',
      'An examination of the technical architecture of distributed cloud computing systems',
      'An examination of how public key cryptography underpins internet security',
      'An examination of the key features and limitations of transformer-based language models',
      'An examination of how agile sprints and scrum ceremonies structure software delivery',
      'An examination of the human-computer interaction principles behind accessible interface design',
    ],
    'Persuasive': [
      'Governments must mandate algorithmic transparency for AI systems used in public decisions',
      'Computer science education should be compulsory from primary school through secondary school',
      'Technology companies must be held legally liable for harms caused by their algorithms',
      'Digital literacy education is as critical as traditional literacy in the 21st century',
      'Universal broadband internet access must be classified as a public utility and human right',
      'Children under 13 should be legally banned from creating social media accounts',
      'AI development labs must be subject to independent safety audits before model deployment',
      'Ethical AI principles must be enforced by law, not left to voluntary corporate commitments',
      'Data collected about citizens should remain the legal property of those citizens',
      'The tech industry must do more to address gender and racial disparities in hiring and advancement',
    ],
    'Research Paper': [
      'Adversarial attacks on deep learning image classifiers: vulnerabilities and defensive strategies',
      'The effectiveness of differential privacy in protecting individual data in machine learning pipelines',
      'Bias detection and mitigation in natural language processing models trained on web corpora',
      'The correlation between open-source contribution activity and software security outcomes',
      'Federated learning architectures for privacy-preserving medical image analysis',
      'Human factors in cybersecurity: social engineering susceptibility and training interventions',
      'The scalability limits of Proof-of-Work consensus mechanisms in public blockchain networks',
      'Measuring the environmental cost of large language model training and inference',
      'Explainability vs accuracy trade-offs in clinical decision support systems',
      'The effects of algorithmic curation on information diversity consumption on social platforms',
    ],
  },

  'Environmental Science': {
    'Argumentative': [
      'Carbon taxes are the most economically efficient mechanism for reducing greenhouse gas emissions',
      'Nuclear energy must be part of any credible net-zero transition strategy',
      'Individual consumer choices are insufficient to address the systemic causes of climate change',
      'Developed nations bear a disproportionate moral responsibility for funding climate adaptation',
      'Fast fashion is one of the most damaging industries for global environmental sustainability',
      'Single-use plastic bans are a symbolic solution that ignores far larger industrial polluters',
      'Geoengineering proposals carry unacceptable geopolitical and ecological risks',
      'Biodiversity loss poses a greater immediate threat to human welfare than climate change alone',
      'International climate agreements consistently fail because they lack binding enforcement mechanisms',
      'Industrial agriculture is the leading driver of deforestation and must be fundamentally reformed',
    ],
    'Analytical': [
      'Analysing the feedback loops between Arctic sea ice loss and global temperature amplification',
      'How the tragedy of the commons explains the failure of international fisheries management',
      'Examining the environmental justice implications of toxic waste facility siting decisions',
      'The role of wetland ecosystems in carbon sequestration and flood risk mitigation',
      'Analysing the effectiveness of marine protected areas in halting coral reef degradation',
      'How planetary boundary theory provides a framework for assessing ecological overshoot',
      'Examining the lifecycle environmental impact of electric vehicles vs internal combustion vehicles',
      'The ecological and economic dimensions of pollinators decline in agricultural systems',
      'Analysing corporate greenwashing: how to distinguish substantive from performative sustainability',
      'The role of indigenous ecological knowledge in biodiversity conservation strategies',
    ],
    'Compare & Contrast': [
      'Cap-and-trade emissions systems vs carbon tax policies in reducing industrial emissions',
      'Renewable energy transition strategies in Germany vs Denmark',
      'Urban heat island effects in developed vs developing world megacities',
      'Proactive climate adaptation strategies vs reactive disaster response approaches',
      'Protected natural reserves vs community-based conservation in preserving biodiversity',
      'Electric vehicles vs hydrogen fuel cell vehicles as pathways to transport decarbonisation',
      'Ocean-based carbon capture vs direct air capture technologies',
      'Climate change policy under market-liberal vs social-democratic governance models',
      'Deforestation rates and drivers in the Amazon vs the Congo Basin',
      'Environmental impact assessments in developed vs developing country regulatory contexts',
    ],
    'Cause & Effect': [
      'The causes and effects of ocean acidification on marine food chain biodiversity',
      'The causes and effects of deforestation in the Amazon on regional precipitation patterns',
      'The causes and effects of plastic pollution accumulation in ocean gyres on marine life',
      'The causes and effects of urban sprawl on local watershed water quality',
      'The causes and effects of melting permafrost on methane release and climate feedback',
      'The causes and effects of nitrogen runoff from agriculture on freshwater eutrophication',
      'The causes and effects of declining insect populations on global food security',
      'The causes and effects of air pollution on public health outcomes in urban centres',
      'The causes and effects of water scarcity on political conflict in the Middle East',
      'The causes and effects of invasive species introduction on native ecosystem stability',
    ],
    'Expository': [
      'An examination of how the carbon cycle regulates atmospheric CO2 concentrations',
      'An examination of the main renewable energy technologies and their scalability constraints',
      'An examination of how biodiversity supports ecosystem resilience and services',
      'An examination of the scientific evidence underpinning consensus on anthropogenic climate change',
      'An examination of how climate models simulate future warming scenarios',
      'An examination of the role of peatlands in global carbon storage',
      'An examination of the causes and consequences of soil degradation in agricultural regions',
      'An examination of the key principles of circular economy models',
      'An examination of how environmental legislation has evolved in the European Union',
      'An examination of how climate change disproportionately affects low-income communities',
    ],
    'Persuasive': [
      'Governments must ban the sale of petrol and diesel vehicles by 2030 to meet climate targets',
      'Meat consumption must be taxed to reflect its full environmental and public health costs',
      'Every country must legally enshrine the right to a clean and healthy environment',
      'Corporations must be required to publish independently verified sustainability reports',
      'Environmental education should be a core and examinable subject in all school curricula',
      'Rewilding programmes deserve far greater government funding and legal protection',
      'Developed nations must honour climate finance commitments to developing countries immediately',
      'Planned obsolescence in consumer electronics should be made illegal to reduce e-waste',
      'The fossil fuel industry must pay reparations for knowingly suppressing climate science',
      'International flights should be taxed at a level that reflects their full climate cost',
    ],
    'Research Paper': [
      'The effectiveness of REDD+ forest conservation payments in reducing tropical deforestation',
      'Microplastic accumulation in freshwater ecosystems: pathways, concentrations, and ecological effects',
      'The role of urban green infrastructure in mitigating heat stress and surface runoff',
      'Climate migration projections for low-elevation coastal zones under 2°C and 4°C scenarios',
      'The relationship between air quality index and respiratory disease hospital admissions in cities',
      'Carbon footprint accounting methods in corporate supply chains: gaps and standardisation needs',
      'Effectiveness of environmental impact assessment frameworks in preventing ecosystem degradation',
      'The intersection of biodiversity conservation and indigenous land rights in protected area governance',
      'Solar geoengineering governance gaps: equity, legitimacy, and termination risk',
      'Life cycle analysis of offshore wind energy versus natural gas electricity generation',
    ],
  },

  'Political Science': {
    'Argumentative': [
      'Liberal democracy is facing a genuine and structural crisis, not a temporary disruption',
      'Electoral systems based on proportional representation produce more stable governance',
      'Economic inequality is the primary driver of democratic backsliding worldwide',
      'The United Nations Security Council veto system is incompatible with global justice',
      'Political party systems in Western democracies no longer represent the median voter',
      'Populism is a symptom of institutional failure, not the cause of democratic erosion',
      'Ranked-choice voting would reduce political polarisation in two-party systems',
      'National sovereignty must be limited in cases of mass atrocity and genocide',
      'Social media has fundamentally undermined deliberative democracy',
      'Compulsory voting increases democratic legitimacy and produces better policy outcomes',
    ],
    'Analytical': [
      'Analysing how Gramsci\'s concept of cultural hegemony explains ideological consent',
      'How realist theory accounts for the behaviour of great powers in great-power competition',
      'Examining the conditions under which transitions from authoritarianism to democracy succeed',
      'The role of civil society organisations in counterbalancing state power',
      'Analysing how ethnic nationalism is mobilised in electoral competition',
      'How institutional veto players shape the pace and scope of policy reform',
      'Examining the democratic backsliding in Hungary under Orbán through the lens of competitive authoritarianism',
      'The role of judicial review in protecting minority rights in majoritarian democracies',
      'Analysing how soft power functions as a tool of Chinese foreign policy',
      'The relationship between economic crisis and the rise of far-right political parties in Europe',
    ],
    'Compare & Contrast': [
      'Presidential vs parliamentary systems in democratic stability and accountability',
      'Left-wing populism vs right-wing populism in rhetoric, base, and policy agenda',
      'American federalism vs German federalism in intergovernmental policy coordination',
      'Realism vs liberalism in explaining international conflict and cooperation',
      'Electoral authoritarian regimes vs consolidated democracies in political competition',
      'NATO\'s collective security model vs ASEAN\'s non-interference norm',
      'The welfare state models of Scandinavia vs the liberal welfare state of the United States',
      'Soft power vs hard power as instruments of foreign policy influence',
      'The British first-past-the-post system vs Dutch proportional representation',
      'Revolutionary socialism vs democratic socialism as pathways to social transformation',
    ],
    'Cause & Effect': [
      'The causes and effects of political polarisation on legislative gridlock and governance quality',
      'The causes and effects of gerrymandering on minority political representation',
      'The causes and effects of campaign finance deregulation on policy responsiveness',
      'The causes and effects of social media disinformation on electoral outcomes',
      'The causes and effects of economic sanctions as a foreign policy instrument',
      'The causes and effects of declining voter turnout on the representativeness of democracies',
      'The causes and effects of constitutional court packing on judicial independence',
      'The causes and effects of refugee crises on host-country political dynamics',
      'The causes and effects of party fragmentation on coalition government stability',
      'The causes and effects of corruption on state capacity and citizen trust',
    ],
    'Expository': [
      'An examination of the major theoretical traditions in international relations',
      'An examination of how electoral systems shape party system development',
      'An examination of the key institutions and functions of the European Union',
      'An examination of the concept of state sovereignty and its evolution in international law',
      'An examination of how checks and balances operate in the United States government',
      'An examination of the political philosophy underlying social contract theories',
      'An examination of how authoritarian regimes maintain political control',
      'An examination of the role of interest groups in shaping legislative outcomes',
      'An examination of how foreign aid functions as an instrument of political influence',
      'An examination of the main theories explaining ethnic conflict in divided societies',
    ],
    'Persuasive': [
      'Voting rights must be expanded and protected as the foundational act of democratic participation',
      'The Electoral College is an obsolete institution that must be abolished in favour of the popular vote',
      'Political campaign donations from corporations must be banned to restore democratic integrity',
      'Citizens\' assemblies should be given binding decision-making power on constitutional questions',
      'Global governance institutions must be reformed to reflect 21st-century power distributions',
      'Term limits should apply to all elected officials to prevent entrenchment and corruption',
      'Low voter turnout is a policy failure that demands structural intervention, not civic shame',
      'The media has a democratic obligation to prioritise policy coverage over political theatre',
      'International election observers must have greater authority to sanction fraudulent elections',
      'Environmental policy must be protected from electoral cycles through independent oversight bodies',
    ],
    'Research Paper': [
      'Explaining democratic backsliding: a comparative analysis of Hungary, Poland, and Turkey',
      'The determinants of voter turnout in Western European parliamentary elections 2000–2024',
      'Electoral integrity and its relationship to post-election violence in sub-Saharan Africa',
      'The policy effects of gender quotas in national legislatures: a cross-national comparison',
      'Populist parties and their effects on immigration policy in EU member states',
      'The role of constitutional courts in resisting executive power grabs in hybrid regimes',
      'Social trust, institutional confidence, and political participation: a multilevel analysis',
      'The effectiveness of international sanctions in changing authoritarian state behaviour',
      'Campaign finance regulation and its correlation with political corruption indices',
      'Digital propaganda and computational politics: the automation of influence operations',
    ],
  },

  'Philosophy': {
    'Argumentative': [
      'Moral relativism cannot provide a coherent foundation for condemning atrocities',
      'Free will is incompatible with a fully deterministic account of brain function',
      'Utilitarianism fails as an ethical theory because it permits the persecution of minorities',
      'Kant\'s categorical imperative provides a stronger foundation for ethics than consequentialism',
      'The existence of evil is logically incompatible with a perfectly good, omnipotent god',
      'Personal identity over time cannot be grounded in physical or psychological continuity alone',
      'Animal cognition research obligates us to extend significant moral status to non-human animals',
      'Plato\'s allegory of the cave remains the most accurate metaphor for ideological delusion',
      'Nihilism, honestly confronted, provides a more honest starting point for ethics than religion',
      'The trolley problem demonstrates that deontological ethics is counterintuitive and unworkable',
    ],
    'Analytical': [
      'Analysing Wittgenstein\'s private language argument and its implications for subjective experience',
      'How Rawls\'s veil of ignorance thought experiment grounds principles of distributive justice',
      'Examining Hegel\'s dialectical method as a framework for understanding historical change',
      'The role of phenomenology in challenging Cartesian mind-body dualism',
      'Analysing Nietzsche\'s concept of the will to power as a critique of Enlightenment morality',
      'How Sartre\'s existentialism grounds radical freedom and absolute responsibility',
      'Examining the philosophical presuppositions embedded in scientific reductionism',
      'The relationship between epistemic injustice and political marginalisation in Miranda Fricker\'s work',
      'Analysing Buddhist concepts of non-self in relation to Western personal identity theories',
      'How applied ethics frameworks navigate genuine moral dilemmas in medical decision-making',
    ],
    'Compare & Contrast': [
      'Kantian deontology vs utilitarian consequentialism in resolving ethical dilemmas',
      'Plato\'s theory of Forms vs Aristotle\'s empirical approach to knowledge',
      'Eastern philosophical traditions vs Western analytical philosophy in concepts of self',
      'Locke\'s liberalism vs Rousseau\'s general will in social contract theory',
      'Existentialism vs absurdism in responding to the problem of meaninglessness',
      'Moral realism vs moral anti-realism in metaethics',
      'Stoic philosophy vs Epicurean philosophy in the pursuit of the good life',
      'Compatibilism vs hard determinism on the question of free will and responsibility',
      'Feminist philosophy vs liberal philosophy in theories of justice and autonomy',
      'Continental philosophy vs analytic philosophy in method and subject matter',
    ],
    'Cause & Effect': [
      'The causes and effects of Enlightenment rationalism on the secularisation of moral philosophy',
      'The causes and effects of postmodern philosophy on the authority of truth claims',
      'The causes and effects of Darwin\'s evolutionary theory on philosophical accounts of human nature',
      'The causes and effects of Descartes\'s mind-body dualism on subsequent philosophy of mind',
      'The causes and effects of logical positivism on the scope of meaningful philosophical discourse',
      'The causes and effects of phenomenology on 20th-century existentialist thought',
      'The causes and effects of global poverty on duties of justice in cosmopolitan philosophy',
      'The causes and effects of technological acceleration on philosophical accounts of human agency',
      'The causes and effects of the linguistic turn on 20th-century analytic philosophy',
      'The causes and effects of feminist critiques on traditional canon-dominated philosophy curricula',
    ],
    'Expository': [
      'An examination of Plato\'s theory of Forms and its epistemological implications',
      'An examination of the main arguments for and against the existence of God in analytic philosophy',
      'An examination of how Aristotle\'s virtue ethics defines human flourishing',
      'An examination of the problem of induction and Hume\'s sceptical conclusion',
      'An examination of how Rawls constructs principles of justice from the original position',
      'An examination of the philosophical debate between free will and determinism',
      'An examination of the concept of consciousness and the hard problem as defined by Chalmers',
      'An examination of Wittgenstein\'s later philosophy and the concept of language games',
      'An examination of what it means to live authentically according to existentialist thought',
      'An examination of the philosophical foundations of human rights',
    ],
    'Persuasive': [
      'Philosophy should be taught as a core subject in secondary schools, not an elective',
      'Bioethics committees must be given genuine decision-making authority in medical research governance',
      'The philosophy of race must be central to any comprehensive account of social justice',
      'Applied ethics education is more valuable to professional training than abstract theory',
      'Philosophers have a public obligation to engage with political and social controversies',
      'Animal rights philosophy demands we move immediately toward plant-based food systems',
      'The philosophy of education must prioritise critical thinking over content transmission',
      'Environmental ethics requires a non-anthropocentric foundation to be coherent',
      'AI ethics must be grounded in explicit philosophical frameworks, not corporate values statements',
      'Philosophy of mind insights must inform how we treat patients with disorders of consciousness',
    ],
    'Research Paper': [
      'Extended mind theory and its implications for personal identity in a digital age',
      'Epistemic injustice and the credibility deficit: structural disadvantage in knowledge production',
      'Moral status gradualism and the ethics of early embryo research in bioethics',
      'The philosophy of forgiveness: conditions, limits, and its role in transitional justice',
      'Non-identity problem in climate ethics: obligations to future persons we could harm',
      'Rawlsian justice applied to global climate negotiations and differentiated responsibilities',
      'Phenomenological accounts of chronic pain experience and the limits of third-person medicine',
      'The philosophy of luck and its implications for desert-based theories of distributive justice',
      'Consciousness and moral status: what neuroscience can and cannot contribute to the question',
      'Dignity, autonomy, and paternalism in public health ethics: a philosophical analysis',
    ],
  },

  'Education': {
    'Argumentative': [
      'Standardised testing narrows the curriculum and harms educational equity',
      'University education is overpriced relative to the labour market returns it delivers',
      'Project-based learning is a more effective pedagogy than direct instruction for the 21st century',
      'School choice and voucher programmes exacerbate educational inequality rather than reduce it',
      'Teachers are undervalued and underpaid relative to their social and economic contribution',
      'Homework should be abolished for primary school students — it causes stress with minimal benefit',
      'Single-sex schools produce measurable academic benefits compared to co-educational settings',
      'Technology in classrooms enhances rather than distracts from meaningful learning when used purposefully',
      'Critical thinking skills cannot be taught as a standalone subject — they must be embedded in content',
      'The school-to-prison pipeline disproportionately harms Black and Latino students through zero-tolerance policies',
    ],
    'Analytical': [
      'Analysing how Paulo Freire\'s Pedagogy of the Oppressed challenges banking model education',
      'Examining the evidence base for differentiated instruction in mixed-ability classrooms',
      'How Vygotsky\'s zone of proximal development informs scaffolded learning approaches',
      'Analysing the role of formative assessment in improving student learning outcomes',
      'Examining the systemic factors that produce teacher attrition in under-resourced schools',
      'How trauma-informed pedagogy changes classroom management and relationship-building',
      'Analysing the Matthew effect in reading acquisition: why early literacy gaps compound over time',
      'The role of implicit teacher expectations in producing differential academic outcomes',
      'Examining how international education rankings (PISA) shape national policy without adequate validity',
      'How universal design for learning principles improve access for students with disabilities',
    ],
    'Compare & Contrast': [
      'The Finnish education model vs the South Korean education model in outcomes and wellbeing',
      'Montessori pedagogy vs traditional structured schooling in early childhood development',
      'Charter schools vs public schools in academic performance and demographic access',
      'In-person education vs hybrid online education in higher education engagement outcomes',
      'Phonics-based reading instruction vs whole language reading instruction',
      'Teacher-centred instruction vs student-centred inquiry learning',
      'Vocational education vs university pathways in labour market outcomes',
      'Rural school resource provision vs urban school resource provision in developed countries',
      'High-stakes testing regimes in the USA vs competency-based assessment in Canada',
      'Boys\' academic underachievement vs girls\' academic underachievement across subjects',
    ],
    'Cause & Effect': [
      'The causes and effects of chronic underfunding on educational outcomes in low-income districts',
      'The causes and effects of class size on student achievement and teacher effectiveness',
      'The causes and effects of early childhood education access on long-term economic outcomes',
      'The causes and effects of the COVID-19 pandemic on global learning loss and inequality',
      'The causes and effects of zero-tolerance school discipline on dropout rates',
      'The causes and effects of teacher professional development quality on student performance',
      'The causes and effects of parental involvement in schooling on student academic confidence',
      'The causes and effects of bilingual education on cognitive flexibility and academic outcomes',
      'The causes and effects of curriculum content bias on racial and ethnic minority student engagement',
      'The causes and effects of school counsellor availability on student mental health outcomes',
    ],
    'Expository': [
      'An examination of the main theories of intelligence and their implications for schooling',
      'An examination of how inclusive education practices benefit all students in mixed classrooms',
      'An examination of the research evidence on the most effective teaching strategies',
      'An examination of how social-emotional learning programmes are implemented in schools',
      'An examination of the role of school leadership in driving instructional quality',
      'An examination of how curriculum is developed, contested, and revised in national systems',
      'An examination of the main approaches to measuring and improving school effectiveness',
      'An examination of how educational technology has been integrated into modern classrooms',
      'An examination of the major global initiatives targeting educational access and quality',
      'An examination of how adult literacy programmes are designed and evaluated',
    ],
    'Persuasive': [
      'Universal pre-primary education must be publicly funded and guaranteed as a right',
      'Higher education must be made tuition-free to remove class as a determinant of access',
      'Schools must teach media literacy and critical evaluation of digital sources as core skills',
      'Sex education must be comprehensive, evidence-based, and taught in all public schools',
      'Teacher pay must be increased substantially to attract and retain talented professionals',
      'Academic testing culture in schools is damaging children\'s mental health and must be reformed',
      'Schools have a responsibility to teach civic participation as an active, not passive, skill',
      'Special education services must be fully resourced and legally enforceable for all qualifying students',
      'Schools should eliminate letter grades in favour of competency-based feedback systems',
      'Cultural and Indigenous languages must be protected and supported within national education systems',
    ],
    'Research Paper': [
      'The effect of class size reduction on student achievement: a systematic review of randomised evidence',
      'Growth mindset interventions in secondary schools: effect sizes and implementation fidelity',
      'The relationship between teacher cultural competency and minority student academic outcomes',
      'Flipped classroom pedagogy and its effects on student engagement and deep learning',
      'Reading recovery programmes and long-term literacy outcomes in at-risk early readers',
      'The impact of school meal programmes on student concentration and academic performance',
      'Socioeconomic segregation in urban public schools and its effect on educational opportunity',
      'Professional learning communities and their role in reducing teacher isolation and improving practice',
      'The effects of technology integration policies on digital literacy and subject-area achievement',
      'Assessment design and its influence on higher-order thinking skill development in secondary education',
    ],
  },

  'Health & Medicine': {
    'Argumentative': [
      'Universal healthcare is both morally imperative and economically superior to market-based systems',
      'The pharmaceutical industry\'s profit motive is incompatible with equitable drug access',
      'Preventive medicine deserves far more funding than acute care in national health budgets',
      'Mental health must be treated with the same urgency and resourcing as physical health',
      'Sugar and ultra-processed food advertising to children should be prohibited by law',
      'Vaccine hesitancy is a public health crisis driven by institutional trust failures, not ignorance',
      'The opioid epidemic is a direct consequence of pharmaceutical company negligence and misconduct',
      'Gender bias in medical research has produced systematic gaps in women\'s healthcare',
      'Telemedicine has permanently improved healthcare accessibility and should be standardised',
      'Fat-shaming in clinical settings causes measurable harm and must be addressed by medical education',
    ],
    'Analytical': [
      'Analysing the social determinants of health and their role in producing health inequalities',
      'How implicit racial bias in healthcare providers affects Black patient diagnostic outcomes',
      'Examining the evidence base for mindfulness-based stress reduction in chronic pain management',
      'The role of the gut microbiome in regulating immune function and mental health',
      'Analysing the ethical challenges of rationing scarce medical resources in crisis conditions',
      'How evidence-based medicine has transformed clinical practice and its remaining limitations',
      'Examining the health effects of air pollution on cardiovascular and respiratory morbidity',
      'The role of health literacy in determining patient engagement and chronic disease management',
      'Analysing the opioid crisis through pharmaceutical marketing, prescribing, and regulatory failure',
      'How structural racism shapes disparate maternal mortality rates by race in the United States',
    ],
    'Compare & Contrast': [
      'Single-payer healthcare systems vs multi-payer private insurance systems in cost and outcomes',
      'Eastern holistic medicine vs Western biomedical approaches in chronic disease management',
      'Infectious disease burden in low-income vs high-income countries: drivers and responses',
      'Surgical intervention vs lifestyle modification in managing type 2 diabetes',
      'Mental health treatment models in Scandinavia vs the United States',
      'Palliative care approaches in hospice settings vs acute hospital settings',
      'Primary care-led health systems vs specialist-led systems in preventive outcomes',
      'Pharmaceutical regulation in the FDA vs the European Medicines Agency',
      'Public health communication during COVID-19: comparing effective vs ineffective national responses',
      'Addiction treatment via harm reduction vs abstinence-only approaches',
    ],
    'Cause & Effect': [
      'The causes and effects of healthcare worker burnout on patient safety and care quality',
      'The causes and effects of food insecurity on childhood development and health outcomes',
      'The causes and effects of antibiotic overuse on the emergence of drug-resistant infections',
      'The causes and effects of social isolation in elderly populations on mortality risk',
      'The causes and effects of sedentary lifestyle on cardiometabolic disease prevalence',
      'The causes and effects of medical misinformation on vaccination coverage rates',
      'The causes and effects of occupational chemical exposure on long-term worker health',
      'The causes and effects of healthcare privatisation on access equity in mixed systems',
      'The causes and effects of chronic sleep deprivation on metabolic and immune function',
      'The causes and effects of maternal malnutrition on foetal development and infant outcomes',
    ],
    'Expository': [
      'An examination of how the immune system responds to viral infection',
      'An examination of the main risk factors for cardiovascular disease and evidence-based prevention',
      'An examination of how cancer immunotherapy works and its current clinical applications',
      'An examination of the global burden of non-communicable diseases and policy responses',
      'An examination of how CRISPR gene editing technology is applied in medical research',
      'An examination of the principles of medical ethics: autonomy, beneficence, non-maleficence, justice',
      'An examination of how health disparities are measured and monitored in population data',
      'An examination of the stages of clinical drug development from discovery to approval',
      'An examination of the role of public health infrastructure in pandemic preparedness',
      'An examination of how chronic inflammation is linked to major modern diseases',
    ],
    'Persuasive': [
      'Mental health parity laws must be enforced rigorously to end insurance discrimination',
      'Pharmaceutical price transparency laws are necessary to protect patients and public budgets',
      'Sugar-sweetened beverage taxes are an effective and justified public health intervention',
      'Medical schools must train students in cultural competency as a core clinical skill',
      'Doctors have a moral obligation to counsel patients on climate change as a health risk',
      'Palliative care should be integrated into standard treatment from the point of serious diagnosis',
      'Robust public health investment delivers better returns than increased hospital spending',
      'Structural racism in healthcare must be addressed through targeted institutional reform',
      'Healthcare data interoperability must be mandated to improve care coordination and safety',
      'Dental care must be integrated into standard national health coverage — oral health is systemic health',
    ],
    'Research Paper': [
      'The association between social determinants of health and preventable hospitalisation rates',
      'Effectiveness of motivational interviewing in improving adherence to chronic disease treatment',
      'Racial and ethnic disparities in COVID-19 mortality: structural causes and policy implications',
      'Long COVID syndrome: prevalence, risk factors, and mechanisms — a systematic review',
      'The role of primary care visit frequency in reducing emergency department overutilisation',
      'Impacts of hospital mergers on health service quality, access, and pricing',
      'Caregiver burden in dementia care: risk factors, health consequences, and support interventions',
      'Maternal mortality disparities by race: a structural analysis of contributing health system factors',
      'The effectiveness of community health worker programmes in reducing health inequalities',
      'Telemedicine adoption barriers and facilitators in rural and underserved populations',
    ],
  },

  'Economics': {
    'Argumentative': [
      'Austerity measures during recessions deepen economic damage rather than restore fiscal stability',
      'The minimum wage should be raised to reflect living costs, not depressed to protect employment rates',
      'Free trade agreements disproportionately benefit corporations at the expense of domestic workers',
      'Universal basic income is economically feasible and would reduce poverty without disincentivising work',
      'Financial deregulation, not individual irresponsibility, caused the 2008 global financial crisis',
      'Central bank independence is essential to preventing politically motivated inflationary policy',
      'Trickle-down economics has failed empirically and must be abandoned as a policy framework',
      'Cryptocurrency markets are fundamentally speculative and will not replace monetary systems',
      'Patent monopolies on essential medicines create an unjust trade-off between profit and lives',
      'Degrowth economics offers a more sustainable framework than green growth for addressing climate change',
    ],
    'Analytical': [
      'Analysing how Keynesian demand management theory informed post-2008 fiscal stimulus programmes',
      'Examining the role of information asymmetry in creating adverse selection in insurance markets',
      'How game theory explains strategic behaviour in oligopolistic market structures',
      'Analysing the economics of platform markets and why winner-take-all dynamics emerge',
      'The role of behavioural economics in explaining deviations from rational choice theory',
      'Examining how exchange rate movements affect trade balances in open economies',
      'Analysing the economic effects of immigration on host country labour markets and fiscal outcomes',
      'How the Gini coefficient measures income inequality and the limits of this approach',
      'Examining the economics of climate externalities and optimal carbon pricing design',
      'The role of property rights and institutions in explaining cross-country income differences',
    ],
    'Compare & Contrast': [
      'Keynesian economic theory vs monetarist economic theory in explaining business cycles',
      'Socialist economic planning vs market capitalism in resource allocation efficiency',
      'Expansionary fiscal policy vs contractionary fiscal policy in managing inflation',
      'The Nordic social market economy vs the Anglo-American liberal market economy',
      'Microeconomic policy tools vs macroeconomic policy tools in addressing unemployment',
      'Supply-side tax reform vs demand-side spending stimulus in economic recovery',
      'Developing economy structural adjustment policies vs heterodox development strategies',
      'Fixed exchange rate regimes vs floating exchange rate regimes in macroeconomic stability',
      'Economic growth in East Asian developmental states vs sub-Saharan African economies',
      'Free market healthcare economics vs regulated healthcare systems in efficiency and equity',
    ],
    'Cause & Effect': [
      'The causes and effects of income inequality on aggregate consumer demand and growth',
      'The causes and effects of quantitative easing on asset prices and wealth distribution',
      'The causes and effects of trade deficit accumulation on a nation\'s long-term creditworthiness',
      'The causes and effects of hyperinflation on savings, investment, and social stability',
      'The causes and effects of corporate tax avoidance on public revenue and service provision',
      'The causes and effects of automation on skill-biased technological unemployment',
      'The causes and effects of public debt accumulation on sovereign bond market confidence',
      'The causes and effects of housing price inflation on inequality and intergenerational mobility',
      'The causes and effects of remittance flows on economic development in origin countries',
      'The causes and effects of capital flight on developing country investment capacity',
    ],
    'Expository': [
      'An examination of how supply and demand curves determine market equilibrium prices',
      'An examination of the main causes and remedies for market failure in economics',
      'An examination of how central banks use interest rate policy to control inflation',
      'An examination of the key components of gross domestic product and their measurement',
      'An examination of how comparative advantage theory explains the benefits of international trade',
      'An examination of the main features and causes of economic recessions',
      'An examination of public goods theory and the justification for government provision',
      'An examination of how labour markets function and what causes wage differentials',
      'An examination of the role of financial institutions in allocating capital in market economies',
      'An examination of the economic theory of externalities and the Pigouvian tax solution',
    ],
    'Persuasive': [
      'Wealth taxes on extreme fortunes are necessary to fund public goods and reduce inequality',
      'Student loan debt cancellation would produce measurable macroeconomic stimulus benefits',
      'The WTO must be reformed to give developing countries a fairer voice in trade rule-setting',
      'Central banks must incorporate inequality into their mandate alongside inflation and employment',
      'Corporate monopolies in digital markets must be broken up to restore competitive pricing',
      'Offshore tax havens must be eliminated through binding international tax cooperation agreements',
      'Living wage legislation produces more equitable growth than trickle-down tax incentives',
      'Environmental externalities must be priced into GDP accounting to reflect true economic costs',
      'Immigration is a net economic benefit and policies that restrict it harm long-term growth',
      'Gig economy platforms must bear the full employment costs of the workers they depend on',
    ],
    'Research Paper': [
      'The macroeconomic effects of universal basic income: evidence from pilot programmes in Finland and Kenya',
      'Labour market polarisation and the hollowing out of middle-skill employment in OECD economies',
      'The relationship between central bank independence and long-run inflation performance',
      'Foreign direct investment and economic development: evidence from sub-Saharan Africa 2000–2020',
      'The incidence of corporate tax cuts on wages, investment, and profit distribution',
      'Housing supply constraints and affordability crises in major metropolitan areas',
      'Price elasticity of demand for sugar-sweetened beverages and the policy case for taxation',
      'The economic impact of remittances on household consumption and education investment in developing countries',
      'Monopsony power in low-wage labour markets and its effect on wage determination',
      'The fiscal multiplier in low- vs high-interest-rate environments: evidence from OECD countries',
    ],
  },

  'Law': {
    'Argumentative': [
      'The death penalty violates fundamental human rights and must be abolished globally',
      'Mass surveillance programmes violate constitutional privacy rights even when judicially authorised',
      'International human rights law lacks effective enforcement and remains largely aspirational',
      'Corporate liability laws are inadequate to hold corporations accountable for human rights abuses',
      'The criminalisation of drug use is counterproductive and should be replaced by a health approach',
      'Mandatory minimum sentencing removes judicial discretion and produces unjust outcomes',
      'Immigration detention of asylum seekers violates international refugee law principles',
      'Intellectual property rights have been extended beyond their original social justification',
      'Restorative justice programmes produce better victim and offender outcomes than punitive sentencing',
      'The burden of proof in sexual assault cases should be reformed to reflect evidentiary realities',
    ],
    'Analytical': [
      'Analysing how the doctrine of judicial precedent (stare decisis) creates legal certainty and rigidity',
      'Examining the legal framework governing the use of force in international law',
      'How corporate personhood doctrine has expanded First Amendment protections in US law',
      'Analysing the legal challenges of regulating artificial intelligence under existing liability frameworks',
      'The role of constitutional review in protecting fundamental rights from majority overreach',
      'Examining the intersection of domestic criminal law and international humanitarian law',
      'How class action litigation functions as a mechanism for holding corporations accountable',
      'Analysing the legal definition and evidentiary standards for proving discrimination claims',
      'The role of prosecutorial discretion in producing racial disparities in criminal justice outcomes',
      'Examining how international arbitration has reshaped dispute resolution in cross-border commerce',
    ],
    'Compare & Contrast': [
      'Common law legal systems vs civil law legal systems in judicial reasoning and flexibility',
      'Adversarial vs inquisitorial court systems in truth-finding and procedural justice',
      'Domestic human rights protection vs international human rights treaty enforcement',
      'Criminal law standards (beyond reasonable doubt) vs civil law standards (balance of probabilities)',
      'Restorative justice frameworks vs retributive justice frameworks in criminal sentencing',
      'Constitutional monarchy legal systems vs republican constitutional systems in rights protection',
      'Legal aid provision in the UK vs the United States in access to justice outcomes',
      'European Union legal supremacy vs national sovereignty in member state law',
      'Jury trial systems vs professional judge panel systems in verdict accuracy',
      'Corporate criminal liability vs individual executive criminal liability',
    ],
    'Cause & Effect': [
      'The causes and effects of mandatory minimum sentencing on prison population growth and composition',
      'The causes and effects of legal aid funding cuts on access to justice for low-income litigants',
      'The causes and effects of corporate regulatory capture on enforcement effectiveness',
      'The causes and effects of plea bargaining practices on the right to a fair trial',
      'The causes and effects of inadequate legal representation on wrongful conviction rates',
      'The causes and effects of cybercrime legislation gaps on digital fraud prevalence',
      'The causes and effects of judicial appointment politicisation on court independence',
      'The causes and effects of landmark anti-discrimination rulings on workplace equality outcomes',
      'The causes and effects of mass incarceration policies on community-level social capital',
      'The causes and effects of international sanctions on state compliance with international law',
    ],
    'Expository': [
      'An examination of the sources and hierarchy of norms in international law',
      'An examination of how constitutional rights are balanced against competing state interests',
      'An examination of the legal principles governing criminal responsibility and mens rea',
      'An examination of how tort law assigns liability and compensates harm',
      'An examination of the key provisions and enforcement mechanisms of the Geneva Conventions',
      'An examination of how intellectual property law balances creator rights and public access',
      'An examination of the legal frameworks governing environmental liability',
      'An examination of how data protection law operates under GDPR',
      'An examination of the legal concepts of jurisdiction and sovereign immunity',
      'An examination of how contract law principles apply to digital agreements',
    ],
    'Persuasive': [
      'The death penalty must be abolished as incompatible with the right to life',
      'Legal aid must be fully restored and funded to guarantee equal access to justice',
      'Corporate executives must face personal criminal liability for corporate wrongdoing',
      'The age of criminal responsibility must be raised to reflect child developmental science',
      'Sexual history evidence should be permanently excluded from rape trials',
      'International criminal courts need greater enforcement powers to deter atrocity crimes',
      'Drug law reform must shift resources from criminalisation to treatment and harm reduction',
      'Environmental litigation rights must be extended to give nature legal standing',
      'Prison overcrowding is a legal and moral emergency demanding immediate legislative reform',
      'Algorithmic decision-making systems used in courts must be subject to full legal scrutiny',
    ],
    'Research Paper': [
      'Racial disparities in prosecutorial charging decisions: a quantitative analysis of federal cases',
      'The effectiveness of international criminal tribunals in deterring mass atrocity crimes',
      'Corporate liability for supply chain human rights abuses under due diligence legislation',
      'The legal regulation of artificial intelligence in high-stakes decision-making in the EU',
      'Wrongful convictions and the role of forensic evidence reform in reducing miscarriages of justice',
      'The impact of mandatory arbitration clauses on consumer access to judicial remedies',
      'Climate change litigation as a tool for enforcing corporate and governmental climate commitments',
      'The legal status of stateless persons under international refugee law and domestic frameworks',
      'Prison privatisation and the legal accountability gap in private detention facility oversight',
      'Cybercrime jurisdiction challenges in cross-border criminal investigations and prosecutions',
    ],
  },

  'Art & Music': {
    'Argumentative': [
      'Street art and graffiti deserve the same institutional recognition as gallery-based fine art',
      'The music industry\'s streaming royalty model exploits musicians and must be reformed',
      'Artificial intelligence cannot produce genuine art because creativity requires conscious experience',
      'Public arts funding is an economic necessity, not a luxury in times of austerity',
      'Cultural appropriation in music harms marginalised communities when profit replaces acknowledgment',
      'The dominance of Western art history in global education perpetuates cultural imperialism',
      'NFT art is primarily a speculative market, not a genuine revolution in artistic creation',
      'Commercial success is not a legitimate measure of artistic merit',
      'The canon of classical music must be diversified to include non-European and women composers',
      'Music education is one of the most effective interventions for cognitive development and social inclusion',
    ],
    'Analytical': [
      'Analysing how Picasso\'s Guernica functions as both aesthetic object and political statement',
      'How blues music\'s harmonic and structural innovations underpinned 20th-century popular music',
      'Examining the role of the male gaze in shaping representation in the Western painting tradition',
      'How Beethoven\'s late string quartets challenge Classical-era formal conventions',
      'Analysing how abstract expressionism responded to the trauma of post-World War II modernity',
      'The role of patronage systems in shaping artistic production during the Italian Renaissance',
      'How music functions as a form of cultural resistance in contexts of political oppression',
      'Examining the aesthetics of wabi-sabi in Japanese visual arts and ceramics',
      'The political economy of the contemporary art market and the role of speculation',
      'How hip-hop sampling practice created a new legal and aesthetic discourse on originality',
    ],
    'Compare & Contrast': [
      'Baroque musical composition vs Classical-era musical composition in structure and affect',
      'Impressionism in painting vs Impressionism in music: parallel and divergent aesthetic concerns',
      'Traditional analogue music production vs digital audio workstation production',
      'Western tonal harmonic language vs non-Western modal and microtonal traditions',
      'Romanticism in visual art vs Romanticism in literary and musical culture',
      'Street art as public art vs institutional gallery art in accessibility and audience',
      'The Renaissance artistic ideal of the universal genius vs modern specialised artistic practice',
      'Abstract art vs representational art in communicating emotional and political content',
      'Western classical concert traditions vs improvisational jazz performance traditions',
      'Indigenous art as cultural practice vs Indigenous art as commercially traded commodity',
    ],
    'Cause & Effect': [
      'The causes and effects of the digital streaming era on the economics of music production',
      'The causes and effects of the Harlem Renaissance on the global visibility of Black artistic culture',
      'The causes and effects of photography on the evolution of painting from representation to abstraction',
      'The causes and effects of the music industry\'s shift from album to single-driven consumption',
      'The causes and effects of social media platforms on independent artist visibility and income',
      'The causes and effects of colonialism on the erasure and commercialisation of Indigenous art forms',
      'The causes and effects of the AIDS crisis on the content and politics of 1980s contemporary art',
      'The causes and effects of the printing press on the mass reproduction and democratisation of visual art',
      'The causes and effects of cultural censorship regimes on underground artistic movements',
      'The causes and effects of globalisation on the homogenisation of popular music aesthetics',
    ],
    'Expository': [
      'An examination of the defining characteristics of the Impressionist movement in French painting',
      'An examination of how Western music notation systems represent and constrain musical ideas',
      'An examination of the key features of Modernist art across painting, sculpture, and architecture',
      'An examination of how music theory concepts of harmony, rhythm, and melody interact',
      'An examination of the social and cultural context that produced the Harlem Renaissance',
      'An examination of how digital technology has transformed the creation and distribution of music',
      'An examination of the principles of colour theory and their application in visual art practice',
      'An examination of how cinema music functions to direct emotional response',
      'An examination of the main movements in 20th-century contemporary visual art',
      'An examination of how traditional folk music traditions are preserved and transmitted',
    ],
    'Persuasive': [
      'Music education must be protected from budget cuts — it produces measurable academic and social benefits',
      'Public arts funding generates stronger economic returns than the subsidies given to large industries',
      'Museums must actively decolonise their collections by returning contested cultural artefacts',
      'Live music venues are cultural infrastructure and deserve the same protection as public parks',
      'Art therapy programmes must be integrated into mental health treatment as an evidence-based practice',
      'Music streaming platforms must increase royalty rates to ensure musicians can earn a living wage',
      'Art education builds creative and critical thinking skills that are irreplaceable by STEM-only approaches',
      'The commercial music industry must do more to promote music from non-English-speaking traditions',
      'Cultural institutions must do more to make art accessible to people from all socioeconomic backgrounds',
      'Indigenous art forms must be legally protected from commercial exploitation without community consent',
    ],
    'Research Paper': [
      'Gender representation among principal conductors of major orchestras 1990–2024',
      'The economic impact of music streaming royalty models on independent musician income',
      'Decolonising museum collections: case studies in repatriation negotiations and outcomes',
      'The role of arts education in supporting academic resilience in at-risk youth populations',
      'Algorithmic curation on music platforms and its effects on genre diversity and discovery',
      'The commodification of Indigenous art forms and its impact on cultural sovereignty',
      'Music therapy interventions in Alzheimer\'s disease: neurological mechanisms and clinical evidence',
      'Authenticity and commercialism in hip-hop: a discourse analysis of genre identity debates',
      'The economics of cultural heritage preservation in post-conflict societies',
      'Artificial intelligence in music composition: aesthetic, legal, and labour market implications',
    ],
  },

  'Biology': {
    'Argumentative': [
      'Human germline gene editing should be subject to an immediate international moratorium',
      'Rewilding large predators is necessary for restoring damaged ecosystem function',
      'The sixth mass extinction is primarily anthropogenic and demands urgent systemic change',
      'De-extinction via cloning should be pursued for recently extinct keystone species',
      'GMO crops are safe, necessary, and unjustly stigmatised in developed country regulations',
      'Antibiotic use in livestock agriculture must be banned to address antimicrobial resistance',
      'Stem cell research should face fewer regulatory barriers given its therapeutic promise',
      'Biodiversity conservation must prioritise ecosystem function over individual flagship species',
      'Synthetic biology poses biosecurity risks that current governance frameworks are unequipped to manage',
      'Evolutionary theory fully explains human moral psychology without requiring supernatural explanation',
    ],
    'Analytical': [
      'Analysing how CRISPR-Cas9 gene editing enables targeted genetic modification at the molecular level',
      'How epigenetic modifications regulate gene expression without altering DNA sequence',
      'Examining the evolutionary mechanisms underlying antibiotic resistance in bacterial populations',
      'The role of horizontal gene transfer in accelerating bacterial evolution and pathogen emergence',
      'Analysing how keystone species regulate the structure and stability of ecological communities',
      'How oncogene activation and tumour suppressor gene silencing drive carcinogenesis',
      'Examining the molecular basis of neurodegenerative diseases including Alzheimer\'s and Parkinson\'s',
      'The role of the innate immune system in initial pathogen recognition and inflammatory response',
      'Analysing how natural selection shapes population-level variation over generational time',
      'The ecological and evolutionary consequences of invasive species introductions',
    ],
    'Compare & Contrast': [
      'Prokaryotic vs eukaryotic cell structure, function, and gene regulation',
      'Mitosis vs meiosis in cell division purpose, process, and genetic outcome',
      'Active transport vs passive transport across biological membranes',
      'Aerobic respiration vs anaerobic fermentation in energy yield and metabolic context',
      'RNA virus replication strategies vs DNA virus replication strategies',
      'Lamarckian inheritance theory vs Darwinian natural selection',
      'Adaptive immunity vs innate immunity in pathogen defence strategies',
      'Symbiotic vs parasitic ecological relationships in evolutionary outcomes',
      'Convergent evolution vs divergent evolution in producing biological diversity',
      'Sexual reproduction vs asexual reproduction in genetic diversity and evolutionary advantage',
    ],
    'Cause & Effect': [
      'The causes and effects of habitat fragmentation on species genetic diversity and extinction risk',
      'The causes and effects of coral bleaching on reef ecosystem biodiversity',
      'The causes and effects of antibiotic overuse on the evolution of multi-drug-resistant bacteria',
      'The causes and effects of endocrine-disrupting chemicals on amphibian reproductive biology',
      'The causes and effects of nitrogen deposition from agriculture on grassland plant diversity',
      'The causes and effects of overharvesting apex predators on trophic cascade dynamics',
      'The causes and effects of climate change on the timing of biological phenomena such as migration and flowering',
      'The causes and effects of gut microbiome dysbiosis on immune function and metabolic health',
      'The causes and effects of invasive plant species on native animal habitat and food availability',
      'The causes and effects of genetic bottleneck events on long-term species recovery potential',
    ],
    'Expository': [
      'An examination of how DNA replication ensures genetic fidelity and manages replication errors',
      'An examination of the stages of mitosis and how chromosomal segregation is regulated',
      'An examination of how the human immune system distinguishes self from non-self',
      'An examination of the role of photosynthesis in global carbon and oxygen cycles',
      'An examination of how natural selection acts on heritable variation to drive evolution',
      'An examination of the structure and function of the human nervous system',
      'An examination of how viruses exploit host cell machinery to replicate',
      'An examination of the mechanisms of enzyme catalysis and enzyme kinetics',
      'An examination of how the human endocrine system regulates homeostasis through hormone signalling',
      'An examination of how population genetics models predict allele frequency change over time',
    ],
    'Persuasive': [
      'Human germline gene editing must be globally prohibited until governance frameworks are established',
      'Wildlife corridors must be legally protected as essential infrastructure for species conservation',
      'Antibiotic use in factory farming must be banned to prevent a post-antibiotic health crisis',
      'Greater public funding must be directed toward neglected tropical disease research',
      'Biology curricula must integrate evolutionary medicine to prepare students for health challenges',
      'Biodiversity offsets in development projects should be replaced by avoidance-first obligations',
      'The scientific consensus on vaccine safety must be reflected in all public health communications',
      'Ocean protection zones must cover at least 30% of global marine territory by 2030',
      'GMO labelling laws must be scientifically accurate and not conflate safety with preference',
      'Synthetic biology research must be conducted within a robust international biosecurity governance framework',
    ],
    'Research Paper': [
      'CRISPR-Cas9 off-target effects: detection methods, risk assessment, and therapeutic implications',
      'The role of epigenetic inheritance in transgenerational transmission of stress responses',
      'Gut microbiome composition and its association with major depressive disorder: a systematic review',
      'Antibiotic resistance gene dissemination through horizontal gene transfer in agricultural environments',
      'The effectiveness of wildlife corridor restoration in supporting metapopulation persistence',
      'Long non-coding RNA functions in post-transcriptional gene expression regulation',
      'The immunological basis of autoimmune disease: mechanisms of self-tolerance breakdown',
      'Phenotypic plasticity as an adaptive response to rapid environmental change',
      'Trophic cascade effects of wolf reintroduction in Yellowstone: long-term ecosystem recovery data',
      'The genetics of cancer immunotherapy resistance: tumour immune evasion mechanisms',
    ],
  },

  'Chemistry & Physics': {
    'Argumentative': [
      'Nuclear fusion energy is the only technology capable of meeting long-term global energy demand sustainably',
      'Quantum computing will make current encryption standards obsolete within a decade',
      'Carbon capture and storage technology is insufficient as a primary climate solution',
      'The standard model of particle physics is incomplete and will require a paradigm shift',
      'Green hydrogen produced by renewable electrolysis is the most viable fossil fuel replacement',
      'Pharmaceutical chemistry research priorities are distorted by profit rather than therapeutic need',
      'The privatisation of space exploration undermines the scientific commons and international cooperation',
      'Chemistry education\'s emphasis on memorisation over problem-solving must be fundamentally reformed',
      'Perovskite solar cells will surpass silicon in commercial viability within five years',
      'The scientific community\'s response to replication failures in chemistry research is inadequate',
    ],
    'Analytical': [
      'Analysing how catalytic converters reduce vehicular emissions through heterogeneous catalysis',
      'How quantum tunnelling explains reaction rates in enzyme-catalysed biochemical processes',
      'Examining the thermodynamic principles governing the efficiency limits of heat engines',
      'The role of chirality in pharmaceutical drug design and the consequences of racemic mixtures',
      'Analysing how semiconductor band gap engineering enables LED and solar cell design',
      'How wave-particle duality challenges classical intuitions about the nature of light and matter',
      'Examining the physical chemistry of lithium-ion battery charging and degradation mechanisms',
      'The role of hydrogen bonding in determining the anomalous properties of water',
      'Analysing how the Pauli exclusion principle underpins the structure of the periodic table',
      'Examining how spectroscopic techniques reveal molecular structure and composition',
    ],
    'Compare & Contrast': [
      'Nuclear fission energy vs nuclear fusion energy in safety, waste, and scalability',
      'Ionic bonding vs covalent bonding in determining compound physical properties',
      'Classical Newtonian mechanics vs quantum mechanics in describing sub-atomic systems',
      'Homogeneous catalysis vs heterogeneous catalysis in industrial chemical processes',
      'Organic chemistry synthesis routes vs inorganic chemistry approaches in materials science',
      'Special relativity vs general relativity in scope, assumptions, and physical predictions',
      'Oxidation-reduction reactions vs acid-base reactions in energy transfer and chemical change',
      'Crystalline solid vs amorphous solid in structural order and physical properties',
      'Endothermic vs exothermic reactions in thermodynamic energy profiles',
      'Classical wave behaviour vs quantum wave function behaviour in predicting particle position',
    ],
    'Cause & Effect': [
      'The causes and effects of ozone layer depletion on ultraviolet radiation flux and public health',
      'The causes and effects of heavy metal contamination in freshwater on aquatic organisms',
      'The causes and effects of greenhouse gas molecular properties on atmospheric heat retention',
      'The causes and effects of acid rain on freshwater pH and biodiversity',
      'The causes and effects of thermodynamic irreversibility on entropy in isolated systems',
      'The causes and effects of catalyst poisoning on industrial chemical process efficiency',
      'The causes and effects of superconductivity on electrical resistance and energy transmission losses',
      'The causes and effects of photochemical smog formation on urban air quality',
      'The causes and effects of nuclear reactor coolant failure on chain reaction control',
      'The causes and effects of polymer degradation mechanisms on plastic waste persistence',
    ],
    'Expository': [
      'An examination of how the periodic table organises elements by atomic structure and chemical behaviour',
      'An examination of how quantum mechanics describes the electron configuration of atoms',
      'An examination of the principles of chemical thermodynamics: enthalpy, entropy, and Gibbs free energy',
      'An examination of how electromagnetic radiation interacts with matter across the spectrum',
      'An examination of how chemical equilibrium is established and perturbed in reversible reactions',
      'An examination of the standard model of particle physics and the fundamental forces',
      'An examination of how nuclear magnetic resonance spectroscopy identifies organic molecular structure',
      'An examination of the physical principles underlying superconductivity and its applications',
      'An examination of how reaction kinetics is studied and how rate laws are determined',
      'An examination of how modern drug molecules are designed using principles of medicinal chemistry',
    ],
    'Persuasive': [
      'Investment in nuclear fusion research must be dramatically increased to accelerate commercial viability',
      'Chemistry education should be reoriented toward green chemistry principles from introductory level',
      'Governments must fund materials science research for next-generation battery storage technology',
      'Physics literacy should be a requirement for all STEM graduates, not only physics majors',
      'The scientific community must address the reproducibility crisis in experimental chemistry',
      'Space agencies must prioritise planetary defence research as an existential risk mitigation strategy',
      'Renewable energy storage remains the critical bottleneck that demands the greatest research investment',
      'Physics research funding must not be determined solely by short-term commercial application prospects',
      'Chemical weapons must be subject to stronger international prohibition and enforcement mechanisms',
      'Science communicators have a responsibility to present nuclear energy fairly, not emotively',
    ],
    'Research Paper': [
      'Photocatalytic water splitting for hydrogen production: efficiency and materials science challenges',
      'The electrochemical mechanisms of lithium dendrite formation and its implications for battery safety',
      'Quantum error correction: current approaches, scalability barriers, and fault-tolerant thresholds',
      'Green chemistry metrics for evaluating synthetic route sustainability in pharmaceutical manufacturing',
      'The physical chemistry of aerosol particles and their role in climate radiative forcing',
      'Perovskite solar cell stability degradation mechanisms and encapsulation strategies',
      'Superconducting qubit coherence time limitations and materials engineering approaches',
      'Microplastic degradation pathways and the chemistry of secondary microplastic formation',
      'The role of computational density functional theory in accelerating catalyst design',
      'Synthesis and characterisation of metal-organic frameworks for selective gas capture applications',
    ],
  },
}

// ── State ─────────────────────────────────────────────────────────────────────
const subject = ref<Subject>('Psychology')
const essayType = ref<EssayType>('Argumentative')
const level = ref<Level>('Undergraduate')
const generated = ref(false)
const pageOffset = ref(0)
const copiedIdx = ref<number | null>(null)

const currentTopics = computed<string[]>(() => {
  const pool = TOPICS[subject.value]?.[essayType.value] ?? []
  return pool
})

const displayedTopics = computed(() => {
  const pool = currentTopics.value
  if (pool.length === 0) return []
  const start = (pageOffset.value * 8) % pool.length
  const result: string[] = []
  for (let i = 0; i < 8; i++) {
    result.push(pool[(start + i) % pool.length])
  }
  return result
})

function generate() {
  pageOffset.value = 0
  generated.value = true
}
function refresh() {
  pageOffset.value = pageOffset.value + 1
}

async function copyTopic(text: string, i: number) {
  await navigator.clipboard.writeText(text)
  copiedIdx.value = i
  setTimeout(() => { copiedIdx.value = null }, 2000)
}

function topicLink(topic: string) {
  return `/tools/thesis-generator?topic=${encodeURIComponent(topic)}`
}
</script>

<template>
  <div class="bg-slate-50 min-h-screen">
    <!-- Breadcrumb -->
    <div class="max-w-5xl mx-auto px-4 pt-6 pb-2">
      <nav class="text-sm text-slate-500 flex items-center gap-1.5">
        <NuxtLink to="/tools" class="hover:text-brand-600 transition-colors">Tools</NuxtLink>
        <span>/</span>
        <span class="text-slate-700 font-medium">Essay Topic Generator</span>
      </nav>
    </div>

    <div class="max-w-5xl mx-auto px-4 pb-4">
      <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-800 mb-1">Essay Topic Generator</h1>
      <p class="text-slate-500 text-sm">Choose your subject and essay type to get 8 specific, academically appropriate topic ideas.</p>
    </div>

    <div class="max-w-5xl mx-auto px-4 pb-16 space-y-6">

      <!-- Form -->
      <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6 space-y-6">

        <!-- Subject -->
        <div>
          <label class="block text-sm font-bold text-slate-700 mb-2">Subject Area</label>
          <select v-model="subject" class="w-full sm:w-80 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none">
            <option v-for="s in SUBJECTS" :key="s">{{ s }}</option>
          </select>
        </div>

        <!-- Essay type -->
        <div>
          <label class="block text-sm font-bold text-slate-700 mb-2">Essay Type</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="et in ESSAY_TYPES"
              :key="et"
              type="button"
              @click="essayType = et"
              :class="[
                'rounded-full px-4 py-2 text-sm font-semibold border transition-all',
                essayType === et
                  ? 'bg-brand-600 text-white border-brand-600'
                  : 'border-slate-200 text-slate-600 hover:border-brand-400 hover:text-brand-600'
              ]"
            >{{ et }}</button>
          </div>
        </div>

        <!-- Level -->
        <div>
          <label class="block text-sm font-bold text-slate-700 mb-2">Academic Level</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="l in LEVELS"
              :key="l"
              type="button"
              @click="level = l"
              :class="[
                'rounded-full px-4 py-2 text-sm font-semibold border transition-all',
                level === l
                  ? 'bg-brand-600 text-white border-brand-600'
                  : 'border-slate-200 text-slate-600 hover:border-brand-400 hover:text-brand-600'
              ]"
            >{{ l }}</button>
          </div>
        </div>

        <button
          type="button"
          @click="generate"
          class="rounded-xl bg-brand-600 px-8 py-3 text-sm font-bold text-white hover:bg-brand-700 transition-colors"
        >
          Generate Topics →
        </button>
      </div>

      <!-- Results -->
      <template v-if="generated">
        <div class="flex items-center justify-between flex-wrap gap-3">
          <h2 class="text-base font-bold text-slate-700">
            8 {{ essayType }} Topics — {{ subject }}
            <span class="text-sm font-normal text-slate-400 ml-2">{{ level }}</span>
          </h2>
          <button
            type="button"
            @click="refresh"
            class="flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 hover:border-brand-400 hover:text-brand-600 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"/></svg>
            Refresh topics
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div
            v-for="(topic, i) in displayedTopics"
            :key="topic"
            class="rounded-2xl bg-white border border-slate-100 shadow-sm p-5 flex flex-col gap-3"
          >
            <div class="flex-1">
              <p class="text-sm text-slate-700 leading-relaxed font-medium">{{ topic }}</p>
            </div>
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-[11px] font-semibold rounded-full bg-brand-50 text-brand-700 border border-brand-100 px-2.5 py-1">{{ level }}</span>
              <span class="text-[11px] font-semibold rounded-full bg-slate-50 text-slate-600 border border-slate-100 px-2.5 py-1">{{ essayType }}</span>
              <div class="flex-1" />
              <button
                type="button"
                @click="copyTopic(topic, i)"
                class="text-xs font-semibold rounded-lg border border-slate-200 px-3 py-1.5 text-slate-600 hover:bg-slate-50 transition-colors"
              >{{ copiedIdx === i ? 'Copied!' : 'Copy' }}</button>
              <NuxtLink
                :to="topicLink(topic)"
                class="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1"
              >
                Start with this →
              </NuxtLink>
            </div>
          </div>
        </div>
      </template>

      <!-- CTA -->
      <div class="rounded-2xl bg-white border border-slate-100 shadow-sm p-6 text-center">
        <p class="text-sm text-slate-600 mb-3">Need a full essay written by experts? We deliver custom, plagiarism-free papers from <strong>$10/page</strong>.</p>
        <NuxtLink to="/order" class="inline-block rounded-xl bg-brand-600 px-6 py-3 text-sm font-bold text-white hover:bg-brand-700 transition-colors">
          Order a paper →
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
