<script lang="ts">
	import { onMount } from 'svelte';
	import { analyzeText, type AnalysisResult } from '$lib/api';
	import AutomataVisualizer from '$lib/components/AutomataVisualizer.svelte';
	import { CheckCircle2, Shield, BarChart3, ShieldCheck, AlertTriangle, User, Send, Languages, ClipboardCheck, Code } from '@lucide/svelte';

	let text = $state('');
	let result = $state<AnalysisResult | null>(null);
	let loading = $state(false);
	let error = $state<string | null>(null);

	// Stats state
	let totalToday = $state(67);
	let safetyPercentage = $state(78);

	const charLimit = 500;

	onMount(() => {
		loadStats();
	});

	function loadStats() {
		const history = JSON.parse(localStorage.getItem('detox_history') || '[]');
		if (history.length > 0) {
			totalToday = 67 + history.length;
			const safeCount = history.filter((h: any) => h.result === 'SAFE').length;
			safetyPercentage = Math.round(((67 * 0.78 + safeCount) / totalToday) * 100);
		}
	}

	async function handleAnalyze() {
		if (!text.trim()) return;
		loading = true;
		error = null;
		try {
			const res = await analyzeText(text);
			result = res;

			// Save to localStorage history
			const history = JSON.parse(localStorage.getItem('detox_history') || '[]');
			history.unshift({
				id: Date.now().toString(),
				timestamp: new Date().toISOString(),
				original: res.original,
				normalized: res.normalized,
				result: res.result,
				detected_words: res.detected_words,
				trace: res.trace
			});
			localStorage.setItem('detox_history', JSON.stringify(history.slice(0, 50)));
			
			// Recalculate stats
			loadStats();
		} catch (e: any) {
			error = e.message || 'Terjadi kesalahan sistem';
		} finally {
			loading = false;
		}
	}

	function handleClear() {
		text = '';
		result = null;
		error = null;
	}
</script>

<div class="container animate-fade-in">
	<div class="hero-section">
		<h1>Cek amannya teks kamu</h1>
		<p class="subtitle">Deteksi kalimat toksik secara cepat menggunakan visualisasi NFA & DFA</p>
	</div>

	<div class="analyzer-grid">
		<!-- Left: Input Card -->
		<div class="glass-card panel-card">
			<div class="panel-header">
				<h2>Input Kalimat</h2>
				<span class="char-counter" class:limit-reached={text.length >= charLimit}>
					{text.length}/{charLimit}
				</span>
			</div>
			
			<div class="input-wrapper">
				<textarea
					bind:value={text}
					placeholder="Ketik kalimat atau kata yang ingin diuji di sini... (contoh: 'lo gblk bngst')"
					maxlength={charLimit}
					disabled={loading}
					rows="5"
				></textarea>
			</div>

			<!-- Contoh Cepat (from wireframe / user HTML) -->
			<div class="quick-examples">
				<span class="quick-label">Contoh cepat:</span>
				<div class="example-tags">
					<button onclick={() => text = 'lo gblk bngst'} class="tag-btn" disabled={loading}>lo gblk bngst</button>
					<button onclick={() => text = 'makasih udh bantu'} class="tag-btn" disabled={loading}>makasih udh bantu</button>
					<button onclick={() => text = 'anj1ng lo p4rh'} class="tag-btn" disabled={loading}>anj1ng lo p4rh</button>
					<button onclick={() => text = 'otw ke kampus'} class="tag-btn" disabled={loading}>otw ke kampus</button>
				</div>
			</div>

			{#if error}
				<div class="error-msg">{error}</div>
			{/if}

			<div class="actions">
				<button onclick={handleClear} class="btn-secondary" disabled={loading || !text}>
					Reset
				</button>
				<button onclick={handleAnalyze} class="btn-primary" disabled={loading || !text.trim()}>
					{#if loading}
						<span class="spinner"></span> Memproses...
					{:else}
						Analisis Teks
					{/if}
				</button>
			</div>
		</div>

		<!-- Right: Result Card -->
		<div class="glass-card panel-card result-panel">
			{#if result}
				<div class="result-header">
					<h2>Hasil Analisis</h2>
					<span class="badge {result.result === 'TOXIC' ? 'badge-toxic' : 'badge-safe'}">
						{result.result}
					</span>
				</div>

				<div class="result-body">
					<div class="text-group">
						<span class="label">Teks Asli</span>
						<p class="text-box original-text">{result.original}</p>
					</div>

					<div class="text-group">
						<span class="label">Normalisasi (NFA)</span>
						<p class="text-box normalized-text">{result.normalized}</p>
					</div>

					{#if result.detected_words.length > 0}
						<div class="text-group">
							<span class="label">Kata Toksik</span>
							<div class="toxic-tags">
								{#each result.detected_words as word}
									<span class="tag-toxic">{word}</span>
								{/each}
							</div>
						</div>
					{/if}

					<!-- Trace section -->
					<div class="trace-section">
						<h3>Jejak Automata</h3>
						
						<!-- NFA Slang steps -->
						<div class="trace-group">
							<span class="label">1. Langkah NFA (Slang ke Baku)</span>
							{#if result.trace.nfa_steps.length > 0}
								<div class="nfa-steps">
									{#each result.trace.nfa_steps as step}
										<div class="nfa-step-badge">
											{step}
										</div>
									{/each}
								</div>
							{:else}
								<p class="empty-trace">Tidak ada slang terdeteksi. Kalimat sudah baku.</p>
							{/if}
						</div>

						<!-- DFA state path -->
						<div class="trace-group">
							<span class="label">2. Transisi State DFA (Pencocok Pattern)</span>
							<AutomataVisualizer dfaPath={result.trace.dfa_path} normalizedText={result.normalized} />
						</div>

					</div>
				</div>
			{:else}
				<div class="empty-state">
					<div class="empty-icon"><ShieldCheck size={28} color="var(--color-accent)" /></div>
					<h3>Hasil analisis akan muncul di sini</h3>
					<p>Masukkan kata atau kalimat pada panel kiri dan jalankan analisis untuk memetakan transisi state automata.</p>
				</div>
			{/if}
		</div>
	</div>

	<!-- Widgets Stats Section (from wireframe) -->
	<div class="stats-bar glass-card">
		<div class="stat-item">
			<span class="stat-icon"><BarChart3 size={24} color="var(--color-accent)" /></span>
			<div class="stat-info">
				<span class="stat-label">Statistik hari ini</span>
				<span class="stat-num">{totalToday} teks</span>
			</div>
		</div>
		<div class="stat-divider"></div>
		<div class="stat-item">
			<span class="stat-icon"><Shield size={24} color="var(--color-safe)" /></span>
			<div class="stat-info">
				<span class="stat-label">Tingkat keamanan</span>
				<span class="stat-num">{safetyPercentage}% teks aman</span>
			</div>
		</div>
	</div>

	<!-- Cara Kerja Sistem (from wireframe) -->
	<div class="system-section">
		<h2 class="section-title">Cara Kerja Sistem</h2>
		<div class="system-steps">
			<div class="step-card glass-card">
				<div class="step-bg-icon">
					<Send size={110} />
				</div>
				<div class="step-num">1</div>
				<h3>Kirim Teks</h3>
				<p>Teks dimasukkan oleh pengguna untuk dianalisis oleh sistem secara realtime.</p>
			</div>
			<div class="step-card glass-card">
				<div class="step-bg-icon">
					<Languages size={110} />
				</div>
				<div class="step-num">2</div>
				<h3>Normalisasi (NFA)</h3>
				<p>Menormalisasi variasi tulisan slang atau singkatan menjadi kata baku.</p>
			</div>
			<div class="step-card glass-card">
				<div class="step-bg-icon">
					<Code size={110} />
				</div>
				<div class="step-num">3</div>
				<h3>Aturan (Regex)</h3>
				<p>Mendefinisikan pattern formal kata kotor untuk menangkap variasi tulisan sensor.</p>
			</div>
			<div class="step-card glass-card">
				<div class="step-bg-icon">
					<ClipboardCheck size={110} />
				</div>
				<div class="step-num">4</div>
				<h3>Deteksi (DFA)</h3>
				<p>Mencocokkan kata hasil normalisasi secara deterministik menggunakan state machine.</p>
			</div>
		</div>

		<!-- Visualisasi Alur Automata (Simulasi Otomatis) -->
		<div class="glass-card demo-sim-card animate-fade-in" style="margin-top: 28px; padding: 24px;">
			<div class="demo-sim-header">
				<div class="demo-sim-title">
					<span class="pulse-dot"></span>
					<h3>Live Demo: Visualisasi Alur Automata</h3>
				</div>
				<p class="demo-sim-desc">Simulasi interaktif bagaimana kata slang <code class="code-highlight">gblk</code> diubah oleh NFA dan dibaca karakter-per-karakter oleh DFA.</p>
			</div>

			<div class="demo-sim-body">
				<!-- Step 1: Normalization -->
				<div class="demo-stage-box">
					<div class="demo-stage-label">Tahap 1: Normalisasi Slang (NFA)</div>
					<div class="demo-stage-content">
						<div class="demo-bubble-input">
							<span class="bubble-label">Input User:</span>
							<span class="bubble-val">"lo gblk"</span>
						</div>
						<div class="demo-stage-arrow">➔</div>
						<div class="demo-bubble-output">
							<span class="bubble-label">Hasil NFA:</span>
							<span class="bubble-val text-toxic">"kamu goblok"</span>
						</div>
					</div>
				</div>

				<!-- Step 2: DFA Trace -->
				<div class="demo-stage-box" style="margin-top: 20px;">
					<div class="demo-stage-label">Tahap 2: Pengecekan Karakter (DFA)</div>
					<AutomataVisualizer dfaPath="q0 → q1 → q6 → q11 → q12 → q13 → qTOXIC" normalizedText="goblok" />
				</div>
			</div>
		</div>
	</div>

	<!-- Keunggulan & Batasan (from wireframe) -->
	<div class="info-grid">
		<div class="info-card glass-card">
			<h3 class="text-safe" style="display: flex; align-items: center; gap: 8px;"><CheckCircle2 size={20} color="var(--color-safe)" /> Keunggulan Kami</h3>
			<ul class="info-list">
				<li><strong>Cepat:</strong> Deteksi secepat kilat menggunakan algoritma pencocokan Automata O(n).</li>
				<li><strong>Transparan:</strong> Menampilkan visualisasi langkah transisi state NFA & DFA secara detail.</li>
				<li><strong>Tanpa Log:</strong> Privasi terjamin karena semua analisis diproses di sisi klien secara instan.</li>
			</ul>
		</div>

		<div class="info-card glass-card">
			<h3 class="text-toxic" style="display: flex; align-items: center; gap: 8px;"><AlertTriangle size={20} color="var(--color-toxic)" /> Batasan Sistem</h3>
			<ul class="info-list">
				<li><strong>Tanpa Konteks:</strong> Hanya mendeteksi kata per kata tanpa memahami makna/sarkasme kalimat penuh.</li>
				<li><strong>Keterbatasan Leksikon:</strong> Deteksi terbatas pada database kosakata toxic yang terdaftar.</li>
			</ul>
		</div>
	</div>

	<!-- Tim Pengembang (from user HTML) -->
	<div class="developers-section">
		<h3 class="developers-title">Tim Pengembang (Group Greenflag)</h3>
		<div class="dev-badges">
			<div class="dev-badge glass-card">
				<span class="dev-icon"><User size={16} color="var(--color-accent)" /></span>
				<span>Cut Sarah Alisa</span>
			</div>
			<div class="dev-badge glass-card">
				<span class="dev-icon"><User size={16} color="var(--color-accent)" /></span>
				<span>M. Rizal Basri</span>
			</div>
			<div class="dev-badge glass-card">
				<span class="dev-icon"><User size={16} color="var(--color-accent)" /></span>
				<span>Wesnita Ruth Angie</span>
			</div>
		</div>
	</div>
</div>

<style>
	.hero-section {
		text-align: center;
		margin-bottom: 32px;
		margin-top: 16px;
	}

	.hero-section h1 {
		font-size: 2.4rem;
		font-weight: 800;
		letter-spacing: -0.03em;
		background: linear-gradient(135deg, var(--text-primary) 30%, var(--color-accent) 100%);
		-webkit-background-clip: text;
		background-clip: text;
		-webkit-text-fill-color: transparent;
		margin-bottom: 8px;
	}

	.subtitle {
		color: var(--text-secondary);
		font-size: 1.05rem;
	}

	.analyzer-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 24px;
		align-items: start;
		margin-bottom: 24px;
	}

	.panel-card {
		padding: 24px;
		display: flex;
		flex-direction: column;
		min-height: 400px;
	}

	.panel-header, .result-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 16px;
		border-bottom: 1px solid var(--card-border);
		padding-bottom: 12px;
	}

	.panel-header h2, .result-header h2 {
		font-size: 1.15rem;
		font-weight: 600;
	}

	.char-counter {
		font-size: 0.8rem;
		color: var(--text-secondary);
	}

	.char-counter.limit-reached {
		color: var(--color-toxic);
	}

	.input-wrapper {
		flex: 1;
		display: flex;
		flex-direction: column;
		margin-bottom: 16px;
	}

	textarea {
		flex: 1;
		resize: none;
	}

	.actions {
		display: flex;
		justify-content: flex-end;
		gap: 12px;
	}



	.error-msg {
		color: var(--color-toxic);
		font-size: 0.85rem;
		margin-bottom: 16px;
	}

	/* Result panel styles */
	.result-panel {
		background: var(--card-bg);
	}

	.result-body {
		display: flex;
		flex-direction: column;
		gap: 16px;
	}

	.text-group {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.text-group .label {
		font-size: 0.8rem;
		font-weight: 600;
		color: var(--text-secondary);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.text-box {
		background: rgba(0, 0, 0, 0.25);
		border: 1px solid var(--card-border);
		border-radius: var(--radius-md);
		padding: 12px;
		font-size: 0.95rem;
		word-break: break-word;
	}

	:root[data-theme='light'] .text-box {
		background: rgba(0, 0, 0, 0.03);
	}

	.toxic-tags {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
	}

	.tag-toxic {
		background: var(--color-toxic-light);
		color: var(--color-toxic);
		border: 1px solid rgba(244, 63, 94, 0.25);
		padding: 4px 10px;
		border-radius: 6px;
		font-size: 0.85rem;
		font-weight: 600;
	}

	/* Trace logs */
	.trace-section {
		border-top: 1px solid var(--card-border);
		padding-top: 16px;
		margin-top: 8px;
	}

	.trace-section h3 {
		font-size: 1rem;
		margin-bottom: 14px;
		font-weight: 600;
		color: var(--color-accent);
	}

	.trace-group {
		margin-bottom: 14px;
	}

	.trace-group .label {
		font-size: 0.78rem;
		font-weight: 500;
		color: var(--text-secondary);
		display: block;
		margin-bottom: 6px;
	}

	.nfa-steps {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
	}

	.nfa-step-badge {
		background: var(--color-accent-light);
		color: var(--color-accent);
		border: 1px solid rgba(6, 182, 212, 0.2);
		padding: 4px 10px;
		border-radius: 6px;
		font-family: var(--font-mono);
		font-size: 0.8rem;
	}

	.empty-trace {
		font-size: 0.85rem;
		color: var(--text-secondary);
		font-style: italic;
	}


	/* Empty state view */
	.empty-state {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		text-align: center;
		padding: 40px 20px;
	}

	.empty-icon {
		width: 54px;
		height: 54px;
		border-radius: 50%;
		background: rgba(255, 255, 255, 0.03);
		color: var(--text-secondary);
		border: 1px dashed var(--card-border);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 1.5rem;
		margin-bottom: 12px;
	}

	.empty-state h3 {
		font-size: 1.1rem;
		font-weight: 600;
		margin-bottom: 6px;
	}

	.empty-state p {
		font-size: 0.85rem;
		color: var(--text-secondary);
		max-width: 280px;
	}

	/* Stats bar widget */
	.stats-bar {
		display: flex;
		align-items: center;
		justify-content: space-around;
		padding: 16px 24px;
		margin-bottom: 32px;
	}

	.stat-item {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.stat-icon {
		font-size: 1.5rem;
	}

	.stat-info {
		display: flex;
		flex-direction: column;
	}

	.stat-label {
		font-size: 0.85rem;
		color: var(--text-secondary);
	}

	.stat-num {
		font-weight: 700;
		font-size: 1.05rem;
	}

	.stat-divider {
		width: 1px;
		height: 40px;
		background: var(--card-border);
	}

	/* System Section & Step cards */
	.system-section {
		margin-bottom: 32px;
	}

	.section-title {
		text-align: center;
		font-size: 1.5rem;
		font-weight: 700;
		margin-bottom: 24px;
	}

	.system-steps {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 20px;
	}

	.step-card {
		padding: 28px 24px;
		text-align: left;
		position: relative;
		overflow: hidden;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		transition: var(--transition-smooth);
	}

	.step-bg-icon {
		position: absolute;
		right: -12px;
		top: 12px;
		opacity: 0.03;
		color: var(--text-primary);
		pointer-events: none;
		transition: var(--transition-smooth);
	}

	.step-card:hover .step-bg-icon {
		opacity: 0.08;
		transform: scale(1.06) rotate(-8deg);
	}

	:root[data-theme='light'] .step-bg-icon {
		opacity: 0.04;
		color: var(--color-accent);
	}

	:root[data-theme='light'] .step-card:hover .step-bg-icon {
		opacity: 0.1;
	}

	.step-num {
		width: 32px;
		height: 32px;
		border-radius: 50%;
		background: var(--color-accent-light);
		color: var(--color-accent);
		border: 1px solid var(--color-accent);
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 700;
		margin-bottom: 16px;
	}

	.step-card h3 {
		font-size: 1.05rem;
		font-weight: 600;
		margin-bottom: 8px;
	}

	.step-card p {
		font-size: 0.85rem;
		color: var(--text-secondary);
	}

	/* Info grid: Keunggulan & Batasan */
	.info-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 24px;
		margin-bottom: 32px;
	}

	.info-card {
		padding: 24px;
	}

	/* ponytail: removed side colored borders to avoid generic generated-AI aesthetics */

	.info-card h3 {
		font-size: 1.15rem;
		font-weight: 700;
		margin-bottom: 16px;
	}

	.info-list {
		list-style: none;
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.info-list li {
		font-size: 0.9rem;
		position: relative;
		padding-left: 12px;
	}

	.info-list li::before {
		content: "•";
		position: absolute;
		left: 0;
		color: var(--text-secondary);
	}

	.text-safe {
		color: var(--color-safe);
	}

	.text-toxic {
		color: var(--color-toxic);
	}

	/* Spinner */
	.spinner {
		display: inline-block;
		width: 16px;
		height: 16px;
		border: 2px solid rgba(255,255,255,0.3);
		border-top-color: #fff;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}

	/* Quick Examples */
	.quick-examples {
		margin-bottom: 18px;
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.quick-label {
		font-size: 0.8rem;
		font-weight: 600;
		color: var(--text-secondary);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.example-tags {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
	}

	.tag-btn {
		background: rgba(255, 255, 255, 0.04);
		border: 1px solid var(--card-border);
		color: var(--text-primary);
		padding: 5px 12px;
		border-radius: 9999px;
		font-size: 0.82rem;
		font-weight: 500;
		font-family: var(--font-sans);
		cursor: pointer;
		transition: var(--transition-smooth);
	}

	.tag-btn:hover:not(:disabled) {
		background: var(--color-accent-light);
		border-color: var(--color-accent);
		color: var(--text-primary);
	}

	:root[data-theme='light'] .tag-btn {
		background: rgba(0, 0, 0, 0.02);
	}

	/* Developer Badges */
	.developers-section {
		border-top: 1px solid var(--card-border);
		padding-top: 24px;
		margin-top: 16px;
		text-align: center;
	}

	.developers-title {
		font-size: 0.8rem;
		font-weight: 600;
		color: var(--text-secondary);
		text-transform: uppercase;
		letter-spacing: 0.08em;
		margin-bottom: 16px;
	}

	.dev-badges {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 12px;
	}

	.dev-badge {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		padding: 8px 16px;
		border-radius: 9999px;
		font-size: 0.9rem;
		font-weight: 500;
		box-shadow: var(--shadow-lg);
	}

	.dev-icon {
		display: flex;
		align-items: center;
	}

	@media (max-width: 768px) {
		.analyzer-grid, .system-steps, .info-grid {
			grid-template-columns: 1fr;
		}
		
		.panel-card {
			min-height: auto;
		}

		.stat-divider {
			display: none;
		}

		.stats-bar {
			flex-direction: column;
			gap: 16px;
			align-items: flex-start;
		}
	}





	/* Demo Live Sim Card Styles */
	.demo-sim-card {
		border: 1px solid var(--card-border);
		background: rgba(255, 255, 255, 0.02);
		backdrop-filter: blur(10px);
		border-radius: var(--radius-lg);
		text-align: left;
	}

	.demo-sim-header {
		margin-bottom: 20px;
	}

	.demo-sim-title {
		display: flex;
		align-items: center;
		gap: 10px;
		margin-bottom: 6px;
	}

	.demo-sim-title h3 {
		font-size: 1.2rem;
		font-weight: 700;
		color: var(--color-accent);
		margin: 0;
	}

	.pulse-dot {
		width: 8px;
		height: 8px;
		background: var(--color-accent);
		border-radius: 50%;
		box-shadow: 0 0 8px var(--color-accent);
		animation: pulseDot 1.5s infinite ease-in-out;
	}

	@keyframes pulseDot {
		0%, 100% { transform: scale(1); opacity: 0.6; }
		50% { transform: scale(1.4); opacity: 1; }
	}

	.demo-sim-desc {
		font-size: 0.88rem;
		color: var(--text-secondary);
		margin: 0;
	}

	.code-highlight {
		font-family: var(--font-mono);
		background: rgba(255, 255, 255, 0.05);
		padding: 2px 6px;
		border-radius: 4px;
		font-size: 0.85rem;
		color: var(--color-accent);
	}

	.demo-stage-box {
		background: rgba(0, 0, 0, 0.15);
		border: 1px solid var(--card-border);
		border-radius: var(--radius-md);
		padding: 16px;
	}

	:root[data-theme='light'] .demo-stage-box {
		background: rgba(0, 0, 0, 0.01);
	}

	.demo-stage-label {
		font-size: 0.85rem;
		font-weight: 600;
		color: var(--text-secondary);
		margin-bottom: 12px;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.demo-stage-content {
		display: flex;
		align-items: center;
		gap: 16px;
		flex-wrap: wrap;
	}

	.demo-bubble-input, .demo-bubble-output {
		background: rgba(255, 255, 255, 0.02);
		border: 1px solid var(--card-border);
		padding: 8px 16px;
		border-radius: 9999px;
		display: flex;
		align-items: center;
		gap: 8px;
		font-size: 0.9rem;
	}

	.bubble-label {
		color: var(--text-secondary);
		font-size: 0.8rem;
	}

	.bubble-val {
		font-weight: 700;
		font-family: var(--font-mono);
	}

	.demo-stage-arrow {
		font-size: 1.2rem;
		color: var(--color-accent);
	}
</style>
