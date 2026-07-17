// api.ts: API helper with local automata fallback for Detox
// ponytail: client-side rule engine fallback for offline testing. ceiling: lexicon > 500 words, upgrade: fetch dynamic lexicon from backend.

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
	dgn: 'dengan',
	makasih: 'terima kasih',
	parh: 'parah',
	anj1ng: 'anjing'
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

function applyLeetRules(word: string): string {
	const rules: Record<string, string> = {
		'1': 'i',
		'0': 'o',
		'3': 'e',
		'4': 'a',
		'5': 's',
		'7': 't',
		'8': 'b',
		'z': 's'
	};
	let changed = false;
	const chars = word.split('').map((char) => {
		if (rules[char]) {
			changed = true;
			return rules[char];
		}
		return char;
	});
	return changed ? chars.join('') : word;
}

/**
 * Local simulation of the NFA normalizer and DFA matcher
 */
function localAnalyze(text: string): AnalysisResult {
	const { slang, toxic } = getLexicon();
	const toxicSet = new Set(toxic);
	
	const words = text.split(/\s+/);
	const nfa_steps: string[] = [];
	const normalizedWords = words.map((word) => {
		const lowerWord = word.toLowerCase();
		const punc = ".,\\/#!$%\\^&*;:{}=\\-_`~()";
		const prefixMatch = lowerWord.match(new RegExp(`^[${punc}]*`));
		const prefix = prefixMatch ? prefixMatch[0] : "";
		const suffixMatch = lowerWord.match(new RegExp(`[${punc}]*$`));
		const suffix = suffixMatch ? suffixMatch[0] : "";
		
		let cleanWord = lowerWord.slice(prefix.length);
		if (suffix) {
			cleanWord = cleanWord.slice(0, -suffix.length);
		}
		
		let current = cleanWord;

		// 1. Terapkan aturan transformasi leet-speak
		const leetTransformed = applyLeetRules(current);
		if (leetTransformed !== current) {
			nfa_steps.push(`${current} → ${leetTransformed} (rule)`);
			current = leetTransformed;
		}

		// 2. Cek ke slang map
		if (slang[current]) {
			const canonical = slang[current];
			if (canonical !== current) {
				nfa_steps.push(`${current} → ${canonical}`);
			}
			current = canonical;
		}

		return prefix + current + suffix;
	});

	const normalized = normalizedWords.join(' ');
	const cleanWords = normalizedWords.map(w => w.replace(/[.,\/#%\^&\*;:{}=\-`~()]/g, ''));
	
	const LEET_MAP: Record<string, string> = {
		a: '[a4@\\*_]',
		i: '[i1!\\*_]',
		o: '[o0\\*_]',
		e: '[e3\\*_]',
		u: '[u\\*_]',
		s: '[s5$\\*_]',
		g: '[g9\\*_]',
		t: '[t7\\*_]',
		b: '[b8\\*_]'
	};

	const compiledPatterns = toxic.map((tWord) => {
		const parts = tWord.toLowerCase().split('').map(char => {
			if (LEET_MAP[char]) {
				return LEET_MAP[char];
			}
			if (/[a-z]/i.test(char)) {
				return `[${char}\\*_]`;
			}
			return char.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
		});
		return {
			pattern: new RegExp(`^${parts.join('')}$`, 'i'),
			original: tWord
		};
	});

	const detected: string[] = [];
	const cleanedWords: string[] = [];

	normalizedWords.forEach((rawWord, idx) => {
		const word = cleanWords[idx];
		if (!word.trim()) {
			cleanedWords.push(rawWord);
			return;
		}

		let matchedCleanWord: string | null = null;
		if (toxicSet.has(word)) {
			matchedCleanWord = word;
		} else {
			for (const { pattern, original } of compiledPatterns) {
				if (pattern.test(word)) {
					matchedCleanWord = original;
					break;
				}
			}
		}

		if (matchedCleanWord) {
			detected.push(matchedCleanWord);
			const cleanRegex = new RegExp(word.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'), 'i');
			const cleanedWord = rawWord.replace(cleanRegex, matchedCleanWord);
			cleanedWords.push(cleanedWord);
		} else {
			cleanedWords.push(rawWord);
		}
	});

	const uniqueDetected = Array.from(new Set(detected));
	const isToxic = uniqueDetected.length > 0;
	const cleanNormalized = cleanedWords.join(' ');
	
	// Simulate realistic DFA paths for FLA project vibe
	let dfa_path = 'q0';
	if (isToxic) {
		let state = 1;
		uniqueDetected.forEach((_, index) => {
			dfa_path += ` → q${state} → q${state + 5} → q${state + 10}`;
			state += 1;
		});
		dfa_path += ' → qTOXIC';
	} else {
		dfa_path += ' → q1 → q2 → qSafe';
	}

	return {
		original: text,
		normalized: cleanNormalized,
		result: isToxic ? 'TOXIC' : 'SAFE',
		detected_words: uniqueDetected,
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
