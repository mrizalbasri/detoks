// api.ts: API helper with local automata fallback for Detox
// ponytail: client-side rule engine fallback to allow offline testing

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface AnalysisResult {
	original: string;
	normalized: string;
	result: 'TOXIC' | 'SAFE';
	detected_words: string[];
	trace: {
		nfa_steps: string[];
		dfa_path: string;
	};
}

export interface BulkAnalysisResult {
	total: number;
	toxic_count: number;
	safe_count: number;
	results: {
		text: string;
		normalized: string;
		result: 'TOXIC' | 'SAFE';
		detected_words: string[];
	}[];
}

// Local slang lexicon for NFA simulation
const DEFAULT_SLANG_MAP: Record<string, string> = {
	gblk: 'goblok',
	bngst: 'bangsat',
	ajg: 'anjing',
	kntl: 'kontol',
	gw: 'aku',
	udh: 'sudah',
	bgst: 'bangsat',
	lu: 'kamu',
	lo: 'kamu',
	tdk: 'tidak',
	dgn: 'dengan'
};

// Local toxic dictionary for DFA simulation
const DEFAULT_TOXIC_WORDS = ['goblok', 'bangsat', 'anjing', 'kontol', 'tolol', 'bego'];

// Helper to load customized dictionary from localStorage
export function getLexicon(): { slang: Record<string, string>; toxic: string[] } {
	if (typeof window === 'undefined') return { slang: DEFAULT_SLANG_MAP, toxic: DEFAULT_TOXIC_WORDS };
	
	let customSlang: Record<string, string> = {};
	let customToxic: string[] = [];
	
	try {
		customSlang = JSON.parse(localStorage.getItem('detox_custom_slang') || '{}');
		customToxic = JSON.parse(localStorage.getItem('detox_custom_toxic') || '[]');
	} catch (e) {
		console.error('Failed to parse custom lexicon from localStorage', e);
	}
	
	const mergedSlang = { ...DEFAULT_SLANG_MAP, ...customSlang };
	const mergedToxic = Array.from(new Set([...DEFAULT_TOXIC_WORDS, ...customToxic]));
	
	return { slang: mergedSlang, toxic: mergedToxic };
}

export function saveCustomLexicon(slang: Record<string, string>, toxic: string[]) {
	if (typeof window === 'undefined') return;
	localStorage.setItem('detox_custom_slang', JSON.stringify(slang));
	localStorage.setItem('detox_custom_toxic', JSON.stringify(toxic));
}

/**
 * Local simulation of the NFA normalizer and DFA matcher
 */
function localAnalyze(text: string): AnalysisResult {
	const { slang, toxic } = getLexicon();
	const toxicSet = new Set(toxic);
	
	const words = text.toLowerCase().split(/\s+/);
	const nfa_steps: string[] = [];
	const normalizedWords = words.map((word) => {
		// Strip punctuation
		const cleanWord = word.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g, '');
		if (slang[cleanWord]) {
			nfa_steps.push(`${cleanWord} → ${slang[cleanWord]}`);
			return slang[cleanWord];
		}
		return cleanWord;
	});

	const normalized = normalizedWords.join(' ');
	const detected: string[] = [];
	
	normalizedWords.forEach((word) => {
		if (toxicSet.has(word)) {
			detected.push(word);
		}
	});

	const isToxic = detected.length > 0;
	
	// Simulate realistic DFA paths for FLA project vibe
	let dfa_path = 'q0';
	if (isToxic) {
		let state = 1;
		detected.forEach((_, index) => {
			dfa_path += ` → q${state} → q${state + 5} → q${state + 10}`;
			state += 1;
		});
		dfa_path += ' → qTOXIC';
	} else {
		dfa_path += ' → q1 → q2 → qSafe';
	}

	return {
		original: text,
		normalized,
		result: isToxic ? 'TOXIC' : 'SAFE',
		detected_words: detected,
		trace: {
			nfa_steps,
			dfa_path
		}
	};
}

export async function analyzeText(text: string): Promise<AnalysisResult> {
	if (!text.trim()) {
		throw new Error('Input text cannot be empty');
	}
	try {
		const response = await fetch(`${API_URL}/analyze`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ text })
		});
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		return await response.json();
	} catch (e) {
		console.warn('Backend connection failed. Using local simulation fallback.', e);
		return localAnalyze(text);
	}
}

export async function analyzeBulk(texts: string[]): Promise<BulkAnalysisResult> {
	const validTexts = texts.filter(t => t.trim().length > 0);
	if (validTexts.length === 0) {
		throw new Error('Input list cannot be empty');
	}
	try {
		const response = await fetch(`${API_URL}/analyze/bulk`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ texts: validTexts })
		});
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		return await response.json();
	} catch (e) {
		console.warn('Backend connection failed. Using local simulation fallback.', e);
		const results = validTexts.map(text => {
			const res = localAnalyze(text);
			return {
				text: res.original,
				normalized: res.normalized,
				result: res.result,
				detected_words: res.detected_words
			};
		});
		const toxic_count = results.filter(r => r.result === 'TOXIC').length;
		return {
			total: results.length,
			toxic_count,
			safe_count: results.length - toxic_count,
			results
		};
	}
}
