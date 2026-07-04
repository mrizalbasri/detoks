<script lang="ts">
	import { analyzeBulk, type BulkAnalysisResult } from '$lib/api';
	import { FileUp, Download } from '@lucide/svelte';

	let textInput = $state('');
	let result = $state<BulkAnalysisResult | null>(null);
	let loading = $state(false);
	let error = $state<string | null>(null);
	
	let fileName = $state('');
	let isDragOver = $state(false);

	async function handleBulkAnalyze() {
		const lines = textInput.split('\n').map((line) => line.trim()).filter((line) => line.length > 0);
		if (lines.length === 0) {
			error = 'Masukkan teks terlebih dahulu atau unggah file .txt';
			return;
		}
		loading = true;
		error = null;
		try {
			const res = await analyzeBulk(lines);
			result = res;

			// Save individual results to localStorage history
			const history = JSON.parse(localStorage.getItem('detox_history') || '[]');
			res.results.forEach((row) => {
				history.unshift({
					id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
					timestamp: new Date().toISOString(),
					original: row.text,
					normalized: row.normalized,
					result: row.result,
					detected_words: row.detected_words,
					trace: {
						nfa_steps: row.text !== row.normalized ? [`${row.text} → ${row.normalized}`] : [],
						dfa_path: row.result === 'TOXIC' ? 'q0 → q_bulk → qTOXIC' : 'q0 → q_bulk → qSafe'
					}
				});
			});
			localStorage.setItem('detox_history', JSON.stringify(history.slice(0, 50)));
		} catch (e: any) {
			error = e.message || 'Gagal memproses analisis masal';
		} finally {
			loading = false;
		}
	}

	// FileReader API logic for drag-and-drop / file select
	async function handleFileUpload(file: File) {
		error = null;
		fileName = file.name;
		
		const ext = file.name.split('.').pop()?.toLowerCase();
		
		if (ext === 'txt') {
			const reader = new FileReader();
			reader.onload = (e) => {
				textInput = e.target?.result as string;
			};
			reader.readAsText(file);
		} else if (ext === 'docx') {
			const reader = new FileReader();
			reader.onload = async (e) => {
				const arrayBuffer = e.target?.result as ArrayBuffer;
				try {
					// @ts-ignore
					if (typeof window !== 'undefined' && window.mammoth) {
						// @ts-ignore
						const res = await window.mammoth.convertToText({ arrayBuffer });
						textInput = res.value;
					} else {
						error = 'Library Word converter belum siap. Silakan coba sesaat lagi.';
					}
				} catch (err) {
					console.error(err);
					error = 'Gagal membaca isi berkas Word (.docx)';
				}
			};
			reader.readAsArrayBuffer(file);
		} else if (ext === 'pdf') {
			const reader = new FileReader();
			reader.onload = async (e) => {
				const arrayBuffer = e.target?.result as ArrayBuffer;
				try {
					// @ts-ignore
					if (typeof window !== 'undefined' && window.pdfjsLib) {
						// @ts-ignore
						window.pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';
						// @ts-ignore
						const loadingTask = window.pdfjsLib.getDocument({ data: arrayBuffer });
						const pdf = await loadingTask.promise;
						let textContent = '';
						for (let i = 1; i <= pdf.numPages; i++) {
							const page = await pdf.getPage(i);
							const textObj = await page.getTextContent();
							// @ts-ignore
							const pageText = textObj.items.map(item => item.str).join(' ');
							textContent += pageText + '\n';
						}
						textInput = textContent;
					} else {
						error = 'Library PDF converter belum siap. Silakan coba sesaat lagi.';
					}
				} catch (err) {
					console.error(err);
					error = 'Gagal membaca isi berkas PDF';
				}
			};
			reader.readAsArrayBuffer(file);
		} else {
			error = 'Format file tidak didukung. Gunakan file format .txt, .docx, atau .pdf';
			fileName = '';
		}
	}

	function handleFileSelect(e: Event) {
		const input = e.target as HTMLInputElement;
		if (input.files && input.files[0]) {
			handleFileUpload(input.files[0]);
		}
	}

	function handleDragOver(e: DragEvent) {
		e.preventDefault();
		isDragOver = true;
	}

	function handleDragLeave() {
		isDragOver = false;
	}

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		isDragOver = false;
		if (e.dataTransfer && e.dataTransfer.files.length > 0) {
			handleFileUpload(e.dataTransfer.files[0]);
		}
	}

	function handleClear() {
		textInput = '';
		result = null;
		error = null;
		fileName = '';
	}

	function downloadCSV() {
		if (!result) return;
		let csvContent = "data:text/csv;charset=utf-8,No,Teks,Status,Kata Terdeteksi\n";
		result.results.forEach((row, index) => {
			const cleanText = row.text.replace(/"/g, '""');
			const cleanToxic = row.detected_words.join(', ');
			csvContent += `${index + 1},"${cleanText}",${row.result},"${cleanToxic}"\n`;
		});
		const encodedUri = encodeURI(csvContent);
		const link = document.createElement("a");
		link.setAttribute("href", encodedUri);
		link.setAttribute("download", `detox_bulk_results_${Date.now()}.csv`);
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
	}
</script>

<svelte:head>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.min.js"></script>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/mammoth/1.6.0/mammoth.browser.min.js"></script>
</svelte:head>

<div class="container animate-fade-in">
	<div class="hero-section">
		<h1>Periksa banyak teks sekaligus</h1>
		<p class="subtitle">Unggah file teks untuk moderasi masal instan menggunakan engine automata</p>
	</div>

	<div class="bulk-layout">
		<!-- Drag & Drop Upload card (wireframe style) -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div 
			class="glass-card upload-zone" 
			class:drag-over={isDragOver}
			ondragover={handleDragOver}
			ondragleave={handleDragLeave}
			ondrop={handleDrop}
		>
			<input 
				type="file" 
				id="file-upload" 
				accept=".txt,.docx,.pdf" 
				class="file-input" 
				onchange={handleFileSelect} 
			/>
			<label for="file-upload" class="upload-label">
				<span class="upload-icon" style="display: flex; justify-content: center; margin-bottom: 8px;"><FileUp size={44} color="var(--color-accent)" /></span>
				<h3>{fileName || 'Seret file ke sini atau klik untuk pilih'}</h3>
				<p>Mendukung format .txt, .docx (Word), dan .pdf</p>
			</label>
		</div>

		<!-- Optional Textarea fallback so they can see/edit the content -->
		{#if textInput}
			<div class="glass-card panel-card input-preview-card animate-fade-in">
				<div class="panel-header">
					<h2>Pratinjau Isi File / Teks Masal</h2>
					<span class="info-label">{textInput.split('\n').filter(l => l.trim()).length} baris</span>
				</div>
				<textarea
					bind:value={textInput}
					placeholder="Isi file teks akan muncul di sini..."
					rows="6"
					disabled={loading}
				></textarea>
			</div>
		{/if}

		{#if error}
			<div class="error-msg text-center">{error}</div>
		{/if}

		<div class="actions-wrapper">
			<button onclick={handleClear} class="btn-secondary" disabled={loading || !textInput}>
				Reset
			</button>
			<button onclick={handleBulkAnalyze} class="btn-primary btn-large" disabled={loading || !textInput.trim()}>
				{#if loading}
					<span class="spinner"></span> Memproses...
				{:else}
					Analisis Semua
				{/if}
			</button>
		</div>

		<!-- Results Block -->
		{#if result}
			<!-- Ringkasan Hasil (from wireframe) -->
			<div class="results-header-section">
				<h2 class="results-title">Ringkasan Hasil</h2>
				<button onclick={downloadCSV} class="btn-secondary btn-small" style="display: flex; align-items: center; gap: 8px;">
					<Download size={14} color="var(--text-secondary)" /> Unduh hasil (.csv)
				</button>
			</div>
			
			<div class="stats-grid animate-fade-in">
				<div class="glass-card stat-card">
					<span class="stat-title">Total Teks</span>
					<span class="stat-value">{result.total}</span>
				</div>
				<div class="glass-card stat-card border-toxic">
					<span class="stat-title">Konten Toksik</span>
					<span class="stat-value text-toxic">{result.toxic_count}</span>
				</div>
				<div class="glass-card stat-card border-safe">
					<span class="stat-title">Konten Aman</span>
					<span class="stat-value text-safe">{result.safe_count}</span>
				</div>
				<div class="glass-card stat-card border-accent">
					<span class="stat-title">Rasio Toksisitas</span>
					<span class="stat-value text-accent">{Math.round((result.toxic_count / result.total) * 100)}%</span>
				</div>
			</div>

			<!-- Result Table (from wireframe) -->
			<div class="glass-card table-card animate-fade-in">
				<div class="table-wrapper">
					<table>
						<thead>
							<tr>
								<th style="width: 60px;">No</th>
								<th>Teks</th>
								<th style="width: 130px;">Status</th>
								<th>Kata Terdeteksi</th>
							</tr>
						</thead>
						<tbody>
							{#each result.results as row, idx}
								<tr>
									<td class="index-cell">{idx + 1}</td>
									<td>
										<div class="bulk-text-display">
											<p class="bulk-original">{row.text}</p>
											{#if row.text !== row.normalized}
												<p class="bulk-normalized">Baku: {row.normalized}</p>
											{/if}
										</div>
									</td>
									<td>
										<span class="badge {row.result === 'TOXIC' ? 'badge-toxic' : 'badge-safe'}">
											{row.result}
										</span>
									</td>
									<td>
										{#if row.detected_words.length > 0}
											<div class="mini-tags">
												{#each row.detected_words as word}
													<span class="mini-tag-toxic">{word}</span>
												{/each}
											</div>
										{:else}
											<span class="empty-text">-</span>
										{/if}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
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

	.bulk-layout {
		display: flex;
		flex-direction: column;
		gap: 24px;
		margin-bottom: 32px;
	}

	/* Upload Zone Style matching wireframe */
	.upload-zone {
		border: 2px dashed var(--card-border);
		border-radius: var(--radius-lg);
		padding: 48px 24px;
		text-align: center;
		cursor: pointer;
		position: relative;
		transition: var(--transition-smooth);
	}

	.upload-zone:hover, .upload-zone.drag-over {
		border-color: var(--color-accent);
		background: rgba(6, 182, 212, 0.04);
	}

	.file-input {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		opacity: 0;
		cursor: pointer;
	}

	.upload-label {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 12px;
		cursor: pointer;
	}

	.upload-icon {
		font-size: 2.8rem;
		opacity: 0.8;
	}

	.upload-label h3 {
		font-size: 1.2rem;
		font-weight: 600;
	}

	.upload-label p {
		font-size: 0.85rem;
		color: var(--text-secondary);
	}

	.input-preview-card {
		padding: 20px;
		min-height: auto;
	}

	.panel-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 12px;
		border-bottom: 1px solid var(--card-border);
		padding-bottom: 10px;
	}

	.panel-header h2 {
		font-size: 1.05rem;
		font-weight: 600;
	}

	.info-label {
		font-size: 0.78rem;
		color: var(--text-secondary);
		background: rgba(255, 255, 255, 0.05);
		padding: 2px 8px;
		border-radius: 9999px;
	}

	textarea {
		line-height: 1.6;
	}

	.error-msg {
		color: var(--color-toxic);
		font-size: 0.9rem;
	}

	.text-center {
		text-align: center;
	}

	.actions-wrapper {
		display: flex;
		justify-content: center;
		gap: 16px;
	}

	.btn-large {
		padding: 12px 36px;
		font-size: 1.05rem;
	}

	/* Results stats layout */
	.results-header-section {
		display: flex;
		justify-content: space-between;
		align-items: center;
		border-bottom: 1px solid var(--card-border);
		padding-bottom: 12px;
		margin-top: 16px;
	}

	.btn-small {
		padding: 6px 14px;
		font-size: 0.85rem;
		border-radius: 8px;
		border: 1px solid var(--card-border);
		background: rgba(255, 255, 255, 0.03);
		color: var(--text-primary);
		font-weight: 500;
	}

	.btn-small:hover {
		background: rgba(255, 255, 255, 0.08);
	}

	.results-title {
		font-size: 1.35rem;
		font-weight: 700;
	}

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 16px;
	}

	.stat-card {
		padding: 20px;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		text-align: center;
	}

	.stat-card.border-toxic {
		border-top: 4px solid var(--color-toxic);
	}

	.stat-card.border-safe {
		border-top: 4px solid var(--color-safe);
	}

	.stat-card.border-accent {
		border-top: 4px solid var(--color-accent);
	}

	.stat-title {
		font-size: 0.82rem;
		font-weight: 600;
		color: var(--text-secondary);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: 6px;
	}

	.stat-value {
		font-size: 1.85rem;
		font-weight: 800;
	}

	.text-toxic {
		color: var(--color-toxic);
	}

	.text-safe {
		color: var(--color-safe);
	}

	.text-accent {
		color: var(--color-accent);
	}

	/* Results Table Style */
	.table-card {
		padding: 16px;
	}

	.table-wrapper {
		overflow-x: auto;
		border-radius: var(--radius-md);
		border: 1px solid var(--card-border);
	}

	table {
		width: 100%;
		border-collapse: collapse;
		text-align: left;
		font-size: 0.92rem;
	}

	th, td {
		padding: 12px 16px;
		border-bottom: 1px solid var(--card-border);
	}

	th {
		background: rgba(0, 0, 0, 0.15);
		font-weight: 600;
		color: var(--text-secondary);
		font-size: 0.78rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	:root[data-theme='light'] th {
		background: rgba(0, 0, 0, 0.03);
	}

	tr:last-child td {
		border-bottom: none;
	}

	tr:hover {
		background: rgba(255, 255, 255, 0.01);
	}

	.index-cell {
		font-weight: 600;
		color: var(--text-secondary);
	}

	.bulk-text-display {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.bulk-original {
		font-weight: 500;
	}

	.bulk-normalized {
		font-size: 0.8rem;
		color: var(--text-secondary);
	}

	.mini-tags {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
	}

	.mini-tag-toxic {
		background: var(--color-toxic-light);
		color: var(--color-toxic);
		border: 1px solid rgba(244, 63, 94, 0.2);
		padding: 2px 8px;
		border-radius: 4px;
		font-size: 0.78rem;
		font-weight: 600;
	}

	.empty-text {
		color: var(--text-secondary);
		opacity: 0.6;
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

	@media (max-width: 768px) {
		.stats-grid {
			grid-template-columns: 1fr 1fr;
		}
	}
</style>
