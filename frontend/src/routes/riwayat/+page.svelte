<script lang="ts">
	import { onMount } from 'svelte';
	import { ChevronDown, History, Trash2 } from '@lucide/svelte';
	import AutomataVisualizer from '$lib/components/AutomataVisualizer.svelte';

	interface HistoryItem {
		id: string;
		timestamp: string;
		original: string;
		normalized: string;
		result: 'TOXIC' | 'SAFE';
		detected_words: string[];
		trace: {
			nfa_steps: string[];
			dfa_path: string;
		};
	}

	let history = $state<HistoryItem[]>([]);
	let expandedId = $state<string | null>(null);
	let filterStatus = $state<'ALL' | 'TOXIC' | 'SAFE'>('ALL');

	let filteredHistory = $derived(history.filter(item => filterStatus === 'ALL' || item.result === filterStatus));

	let stats = $derived.by(() => {
		const total = history.length;
		if (total === 0) return { total: 0, toxic: 0, safe: 0, toxicPct: 0, safePct: 0, strokeDash: 150.79 };
		const toxic = history.filter(item => item.result === 'TOXIC').length;
		const safe = total - toxic;
		const toxicPct = Math.round((toxic / total) * 100);
		const safePct = 100 - toxicPct;
		const strokeDash = 150.79 - (150.79 * toxicPct / 100);
		return { total, toxic, safe, toxicPct, safePct, strokeDash };
	});

	onMount(() => {
		loadHistory();
	});

	function loadHistory() {
		history = JSON.parse(localStorage.getItem('detox_history') || '[]');
	}

	function handleClearAll() {
		if (confirm('Apakah Anda yakin ingin menghapus semua riwayat analisis?')) {
			localStorage.removeItem('detox_history');
			history = [];
			expandedId = null;
		}
	}

	function handleDeleteItem(id: string, e: Event) {
		e.stopPropagation();
		if (confirm('Apakah Anda yakin ingin menghapus riwayat analisis ini?')) {
			history = history.filter(item => item.id !== id);
			localStorage.setItem('detox_history', JSON.stringify(history));
			if (expandedId === id) expandedId = null;
		}
	}

	function toggleExpand(id: string) {
		expandedId = expandedId === id ? null : id;
	}

	function formatDate(isoString: string) {
		const d = new Date(isoString);
		return d.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' - ' + d.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' });
	}
</script>

<div class="container animate-fade-in">
	<div class="hero-section">
		<h1>Riwayat Analisis</h1>
		<p class="subtitle">Log histori pengecekan dan jejak transisi automata sebelumnya</p>
	</div>

	<div class="history-layout">
		{#if history.length > 0}
			<!-- Dashboard Statistik Riwayat -->
			<div class="glass-card stats-dashboard animate-fade-in">
				<div class="stats-chart-wrapper">
					<!-- SVG Donut Chart -->
					<svg width="80" height="80" viewBox="0 0 64 64" class="donut-svg">
						<!-- Base background circle (Safe - Green) -->
						<circle cx="32" cy="32" r="24" fill="transparent" stroke="var(--color-safe)" stroke-width="8" opacity="0.15" />
						<circle cx="32" cy="32" r="24" fill="transparent" stroke="var(--color-safe)" stroke-width="8" stroke-dasharray="150.79" stroke-dashoffset="0" />
						
						<!-- Top layer circle (Toxic - Red) -->
						{#if stats.toxicPct > 0}
							<circle cx="32" cy="32" r="24" fill="transparent" 
									stroke="var(--color-toxic)" stroke-width="8" 
									stroke-dasharray="150.79" 
									stroke-dashoffset={stats.strokeDash} 
									transform="rotate(-90 32 32)" 
									stroke-linecap="round"
									class="donut-segment" />
						{/if}
						
						<!-- Center Text -->
						<text x="32" y="36" text-anchor="middle" class="chart-text">
							{stats.safePct}%
						</text>
					</svg>
					<div class="chart-legend-center">
						<span class="legend-title">Indeks Aman</span>
					</div>
				</div>

				<div class="stats-cards-grid">
					<div class="stat-mini-card">
						<span class="stat-mini-label">Total Pengujian</span>
						<span class="stat-mini-val">{stats.total}</span>
					</div>
					<div class="stat-mini-card">
						<span class="stat-mini-label text-safe">Aman</span>
						<span class="stat-mini-val text-safe">{stats.safe} <small>({stats.safePct}%)</small></span>
					</div>
					<div class="stat-mini-card">
						<span class="stat-mini-label text-toxic">Toksik</span>
						<span class="stat-mini-val text-toxic">{stats.toxic} <small>({stats.toxicPct}%)</small></span>
					</div>
				</div>
			</div>
		{/if}

		<div class="history-header-row">
			<div class="header-left">
				<span class="count-badge">{filteredHistory.length} Total</span>
			</div>
			
			<div class="filter-wrapper glass-card">
				<button onclick={() => filterStatus = 'ALL'} class="filter-btn" class:active={filterStatus === 'ALL'}>Semua</button>
				<button onclick={() => filterStatus = 'TOXIC'} class="filter-btn" class:active={filterStatus === 'TOXIC'}>Toxic</button>
				<button onclick={() => filterStatus = 'SAFE'} class="filter-btn" class:active={filterStatus === 'SAFE'}>Aman</button>
			</div>

			{#if history.length > 0}
				<button onclick={handleClearAll} class="btn-danger-outline">
					Hapus Semua
				</button>
			{/if}
		</div>

		{#if filteredHistory.length > 0}
			<div class="history-list">
				{#each filteredHistory as item}
					{@const isExpanded = expandedId === item.id}
					<div class="glass-card history-card" class:expanded={isExpanded}>
						<!-- Summary Header (Clickable) -->
						<!-- svelte-ignore a11y_click_events_have_key_events -->
						<!-- svelte-ignore a11y_no_static_element_interactions -->
						<div class="card-summary" onclick={() => toggleExpand(item.id)}>
							<div class="summary-left">
								<span class="timestamp">{formatDate(item.timestamp)}</span>
								<p class="original-preview">{item.original}</p>
							</div>
							<div class="summary-right">
								<span class="badge {item.result === 'TOXIC' ? 'badge-toxic' : 'badge-safe'}">
									{item.result}
								</span>
								<button onclick={(e) => handleDeleteItem(item.id, e)} class="btn-delete-single" aria-label="Hapus riwayat">
									<Trash2 size={16} />
								</button>
								<span class="chevron" class:rotated={isExpanded} style="display: flex; align-items: center;"><ChevronDown size={16} /></span>
							</div>
						</div>

						<!-- Expanded Details -->
						{#if isExpanded}
							<div class="card-details animate-fade-in">
								<div class="details-grid">
									<div class="detail-item">
										<span class="label">Teks Normalisasi</span>
										<p class="val-box">{item.normalized}</p>
									</div>

									{#if item.detected_words.length > 0}
										<div class="detail-item">
											<span class="label">Kata Toksik</span>
											<div class="tags">
												{#each item.detected_words as word}
													<span class="tag-toxic">{word}</span>
												{/each}
											</div>
										</div>
									{/if}
								</div>

								<!-- Traces -->
								<div class="details-trace">
									<div class="trace-group">
										<span class="label">Transisi NFA (Slang Normalization)</span>
										{#if item.trace.nfa_steps.length > 0}
											<div class="nfa-steps">
												{#each item.trace.nfa_steps as step}
													<span class="nfa-badge">{step}</span>
												{/each}
											</div>
										{:else}
											<p class="empty-trace">Tidak ada slang yang dinormalisasi.</p>
										{/if}
									</div>

									<div class="trace-group">
										<span class="label">Jalur Status DFA</span>
										<AutomataVisualizer dfaPath={item.trace.dfa_path} normalizedText={item.normalized} />
									</div>
								</div>
							</div>
						{/if}
					</div>
				{/each}
			</div>
		{:else}
			<div class="glass-card empty-card">
				<div class="empty-icon"><History size={28} color="var(--color-accent)" /></div>
				<h3>Belum Ada Riwayat</h3>
				<p>{filterStatus === 'ALL' ? 'Kalimat yang Anda analisis di halaman utama atau bulk checker akan otomatis disimpan di sini.' : 'Tidak ada entri riwayat dengan status pencarian ini.'}</p>
			</div>
		{/if}
	</div>
</div>

<style>
	.hero-section {
		text-align: center;
		margin-bottom: 32px;
		margin-top: 16px;
	}

	.hero-section h1 {
		font-size: 2.2rem;
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

	.history-layout {
		display: flex;
		flex-direction: column;
		gap: 16px;
	}

	.history-header-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0 4px;
		gap: 16px;
		flex-wrap: wrap;
	}

	.header-left {
		display: flex;
		align-items: center;
	}

	.filter-wrapper {
		display: flex;
		padding: 4px;
		border-radius: 9999px;
		gap: 4px;
		border: 1px solid var(--card-border);
	}

	.filter-btn {
		background: transparent;
		color: var(--text-secondary);
		border: none;
		outline: none;
		font-family: var(--font-sans);
		font-size: 0.85rem;
		font-weight: 500;
		padding: 6px 16px;
		border-radius: 9999px;
		cursor: pointer;
		transition: var(--transition-smooth);
	}

	.filter-btn:hover {
		color: var(--text-primary);
	}

	.filter-btn.active {
		background: var(--color-accent-light);
		color: var(--color-accent);
		font-weight: 600;
	}

	.count-badge {
		font-size: 0.9rem;
		font-weight: 500;
		color: var(--text-secondary);
	}

	.btn-danger-outline {
		background: transparent;
		border: 1px solid var(--color-toxic);
		color: var(--color-toxic);
		padding: 6px 16px;
		border-radius: var(--radius-md);
		font-size: 0.88rem;
		transition: var(--transition-smooth);
	}

	.btn-danger-outline:hover {
		background: var(--color-toxic-light);
		transform: translateY(-1px);
	}

	.history-list {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.history-card {
		overflow: hidden;
		transition: var(--transition-smooth);
	}

	.history-card.expanded {
		border-color: rgba(255, 255, 255, 0.2);
	}

	:root[data-theme='light'] .history-card.expanded {
		border-color: rgba(0, 0, 0, 0.15);
	}

	.card-summary {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 16px 20px;
		cursor: pointer;
		user-select: none;
	}

	.summary-left {
		display: flex;
		flex-direction: column;
		gap: 4px;
		flex: 1;
		margin-right: 20px;
	}

	.timestamp {
		font-size: 0.72rem;
		font-weight: 600;
		color: var(--text-secondary);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.original-preview {
		font-size: 0.95rem;
		font-weight: 500;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		max-width: 450px;
	}

	@media (max-width: 640px) {
		.original-preview {
			max-width: 180px;
		}
	}

	.summary-right {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.chevron {
		font-size: 0.75rem;
		color: var(--text-secondary);
		transition: transform 0.3s ease;
	}

	.chevron.rotated {
		transform: rotate(180deg);
	}

	.card-details {
		border-top: 1px solid var(--card-border);
		padding: 20px;
		background: rgba(0, 0, 0, 0.1);
	}

	:root[data-theme='light'] .card-details {
		background: rgba(0, 0, 0, 0.02);
	}

	.details-grid {
		display: grid;
		grid-template-columns: 1fr;
		gap: 14px;
		margin-bottom: 16px;
	}

	.detail-item {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.label {
		font-size: 0.75rem;
		font-weight: 600;
		color: var(--text-secondary);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.val-box {
		background: rgba(0, 0, 0, 0.2);
		border: 1px solid var(--card-border);
		padding: 10px 14px;
		border-radius: 8px;
		font-size: 0.92rem;
	}

	:root[data-theme='light'] .val-box {
		background: rgba(0, 0, 0, 0.03);
	}

	.tags {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
	}

	.tag-toxic {
		background: var(--color-toxic-light);
		color: var(--color-toxic);
		border: 1px solid rgba(244, 63, 94, 0.2);
		padding: 3px 8px;
		border-radius: 6px;
		font-size: 0.8rem;
		font-weight: 600;
	}

	/* Trace logs inside card details */
	.details-trace {
		border-top: 1px dashed var(--card-border);
		padding-top: 14px;
		display: flex;
		flex-direction: column;
		gap: 14px;
	}

	.nfa-steps {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
	}

	.nfa-badge {
		background: var(--color-accent-light);
		color: var(--color-accent);
		border: 1px solid rgba(6, 182, 212, 0.15);
		padding: 3px 8px;
		border-radius: 4px;
		font-family: var(--font-mono);
		font-size: 0.78rem;
	}

	.empty-trace {
		font-size: 0.82rem;
		color: var(--text-secondary);
		font-style: italic;
	}


	/* Empty History state */
	.empty-card {
		padding: 60px 20px;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		text-align: center;
	}

	.empty-icon {
		width: 60px;
		height: 60px;
		border-radius: 50%;
		background: rgba(255, 255, 255, 0.03);
		color: var(--text-secondary);
		border: 1px dashed var(--card-border);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 1.8rem;
		margin-bottom: 16px;
	}

	.empty-card h3 {
		font-size: 1.1rem;
		font-weight: 600;
		margin-bottom: 6px;
	}

	.empty-card p {
		font-size: 0.85rem;
		color: var(--text-secondary);
		max-width: 320px;
	}

	/* Stats Dashboard & Delete button styles */
	.stats-dashboard {
		display: flex;
		align-items: center;
		gap: 32px;
		padding: 24px;
		margin-bottom: 24px;
	}

	.stats-chart-wrapper {
		display: flex;
		align-items: center;
		gap: 16px;
	}

	.donut-svg {
		filter: drop-shadow(0 0 6px rgba(16, 185, 129, 0.15));
	}

	.donut-segment {
		transition: stroke-dashoffset 0.6s ease-in-out;
		filter: drop-shadow(0 0 6px rgba(244, 63, 94, 0.2));
	}

	.chart-text {
		fill: var(--text-primary);
		font-size: 0.88rem;
		font-weight: 700;
		font-family: var(--font-sans);
	}

	.chart-legend-center {
		display: flex;
		flex-direction: column;
	}

	.legend-title {
		font-size: 0.85rem;
		font-weight: 600;
		color: var(--text-secondary);
	}

	.stats-cards-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 16px;
		flex: 1;
	}

	.stat-mini-card {
		background: rgba(0, 0, 0, 0.15);
		border: 1px solid var(--card-border);
		border-radius: var(--radius-md);
		padding: 12px 16px;
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	:root[data-theme='light'] .stat-mini-card {
		background: rgba(0, 0, 0, 0.01);
	}

	.stat-mini-label {
		font-size: 0.78rem;
		font-weight: 600;
		color: var(--text-secondary);
	}

	.stat-mini-val {
		font-size: 1.25rem;
		font-weight: 700;
		color: var(--text-primary);
	}

	.stat-mini-val small {
		font-size: 0.8rem;
		font-weight: 500;
		opacity: 0.85;
	}

	.btn-delete-single {
		background: transparent;
		border: none;
		color: var(--text-secondary);
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 6px;
		border-radius: 6px;
		margin-right: 8px;
		transition: var(--transition-smooth);
	}

	.btn-delete-single:hover {
		color: var(--color-toxic);
		background: var(--color-toxic-light);
	}

	@media (max-width: 768px) {
		.stats-dashboard {
			flex-direction: column;
			gap: 20px;
			align-items: stretch;
		}

		.stats-chart-wrapper {
			justify-content: center;
		}

		.stats-cards-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
