<script lang="ts">
	import { onMount } from 'svelte';
	import { Rocket, Search, FolderOpen, Clock, Lightbulb, CheckCircle2, AlertOctagon, HelpCircle, ChevronDown, Plus, Trash2, BookOpen } from '@lucide/svelte';
	import { getLexicon, saveCustomLexicon } from '$lib/api';

	// Interactive FAQ state (runes style)
	let activeFaq = $state<number | null>(null);

	function toggleFaq(index: number) {
		activeFaq = activeFaq === index ? null : index;
	}

	let slangList = $state<{ slang: string; formal: string }[]>([]);
	let toxicList = $state<string[]>([]);
	
	let newSlang = $state('');
	let newFormal = $state('');
	let newToxic = $state('');

	let searchSlang = $state('');
	let searchToxic = $state('');

	let filteredSlangList = $derived(
		slangList.filter(item => 
			item.slang.toLowerCase().includes(searchSlang.toLowerCase()) || 
			item.formal.toLowerCase().includes(searchSlang.toLowerCase())
		)
	);

	let filteredToxicList = $derived(
		toxicList.filter(word => 
			word.toLowerCase().includes(searchToxic.toLowerCase())
		)
	);

	onMount(() => {
		loadLexicon();
	});

	function loadLexicon() {
		const { slang, toxic } = getLexicon();
		slangList = Object.entries(slang).map(([slang, formal]) => ({ slang, formal }));
		toxicList = [...toxic];
	}

	function addSlangRule() {
		const s = newSlang.trim().toLowerCase();
		const f = newFormal.trim().toLowerCase();
		if (!s || !f) return;

		const exists = slangList.find(item => item.slang === s);
		if (exists) {
			exists.formal = f;
		} else {
			slangList.push({ slang: s, formal: f });
		}

		newSlang = '';
		newFormal = '';
		saveChanges();
	}

	function removeSlangRule(slangKey: string) {
		slangList = slangList.filter(item => item.slang !== slangKey);
		saveChanges();
	}

	function addToxicWord() {
		const word = newToxic.trim().toLowerCase();
		if (!word) return;

		if (!toxicList.includes(word)) {
			toxicList.push(word);
		}

		newToxic = '';
		saveChanges();
	}

	function removeToxicWord(word: string) {
		toxicList = toxicList.filter(item => item !== word);
		saveChanges();
	}

	function saveChanges() {
		const slangMap: Record<string, string> = {};
		slangList.forEach(item => {
			slangMap[item.slang] = item.formal;
		});
		saveCustomLexicon(slangMap, toxicList);
	}

	const faqs = [
		{
			q: 'Apakah data saya disimpan?',
			a: 'Tidak. Semua proses analisis dilakukan secara realtime di browser Anda (atau melalui server lokal Anda). Kami tidak mengumpulkan atau menyimpan teks yang Anda analisis demi menjaga privasi penuh dan keamanan data Anda.'
		},
		{
			q: 'Kenapa kata kasar tertentu tidak terdeteksi?',
			a: 'Deteksi sistem menggunakan pencocokan leksikon kata kasar tertentu (terkait tugas FLA). Jika terdapat variasi kata kasar baru atau slang yang sangat tidak lazim, kemungkinan kata tersebut belum terdaftar di kamus slang (NFA) atau kamus toxic (DFA) kami.'
		},
		{
			q: 'Bagaimana ketentuan format file untuk Bulk Checker?',
			a: 'Format file yang didukung adalah berkas teks biasa (.txt). Sistem akan membaca isi file baris demi baris, di mana satu baris akan dianggap sebagai satu kalimat utuh untuk dianalisis secara terpisah.'
		}
	];
</script>

<div class="container animate-fade-in">
	<div class="hero-section">
		<h1>Panduan Penggunaan</h1>
		<p class="subtitle">Pelajari cara memaksimalkan fitur Detox untuk lingkungan digital yang lebih sehat</p>
	</div>

	<div class="guide-layout">
		<!-- Quick Start (from wireframe) -->
		<div class="glass-card guide-card">
			<h2 class="guide-title" style="display: flex; align-items: center; gap: 8px;"><Rocket size={20} color="#eab308" /> Quick Start</h2>
			<div class="quick-steps">
				<div class="quick-step">
					<div class="step-icon" style="display: flex; align-items: center;"><Search size={24} color="var(--color-accent)" /></div>
					<div class="step-info">
						<h3>Analisis Instan</h3>
						<p>Ketik satu kalimat atau kata pada kolom input di beranda dan klik tombol analisis.</p>
					</div>
				</div>
				<div class="quick-step">
					<div class="step-icon" style="display: flex; align-items: center;"><FolderOpen size={24} color="var(--color-accent)" /></div>
					<div class="step-info">
						<h3>Gunakan Bulk Checker</h3>
						<p>Unggah file dengan format .txt untuk memproses ratusan kalimat sekaligus tanpa hambatan.</p>
					</div>
				</div>
				<div class="quick-step">
					<div class="step-icon" style="display: flex; align-items: center;"><Clock size={24} color="var(--color-accent)" /></div>
					<div class="step-info">
						<h3>Pantau Riwayat</h3>
						<p>Lihat kembali hasil analisis sebelumnya beserta visualisasi langkah automata di menu Riwayat.</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Memahami Hasil (from wireframe) -->
		<div class="guide-title-section">
			<h2 style="display: flex; align-items: center; gap: 8px;"><Lightbulb size={22} color="#eab308" style="fill: rgba(234, 179, 8, 0.1);" /> Memahami Hasil</h2>
		</div>

		<div class="info-grid">
			<div class="info-card glass-card">
				<h3 class="text-safe" style="display: flex; align-items: center; gap: 8px;"><CheckCircle2 size={18} color="var(--color-safe)" /> Status Aman (Safe)</h3>
				<p class="status-desc">Teks tidak mengandung kata toksik yang terdaftar dalam database kami. Aman untuk dipublikasikan ke media sosial atau platform publik.</p>
				<div class="example-box">
					<span class="label">Contoh Kalimat Aman</span>
					<p class="val-box">"Mohon kirim berkas tugas hari ini ya"</p>
				</div>
			</div>

			<div class="info-card glass-card">
				<h3 class="text-toxic" style="display: flex; align-items: center; gap: 8px;"><AlertOctagon size={18} color="var(--color-toxic)" /> Status Toksik (Toxic)</h3>
				<p class="status-desc">Teks mengandung kata kasar atau toksik yang tidak diperbolehkan. Sistem mendeteksi kecocokan state toxic untuk menghindari ujaran kebencian.</p>
				<div class="example-box">
					<span class="label">Contoh Kalimat Toksik</span>
					<p class="val-box">"Bekerja saja bangsat, jangan banyak bacot lo"</p>
				</div>
			</div>
		</div>

		<!-- Pengelola Kamus Leksikon -->
		<div class="guide-title-section">
			<h2 style="display: flex; align-items: center; gap: 8px;"><BookOpen size={22} color="#eab308" /> Pengelola Kamus Leksikon & Slang</h2>
		</div>

		<div class="lexicon-grid">
			<!-- Kamus Slang (NFA) -->
			<div class="glass-card lexicon-card">
				<h3>Kamus Slang (Normalisasi NFA)</h3>
				<p class="section-desc">Aturan transliterasi dari kata gaul/slang menjadi kata baku.</p>

				<form onsubmit={(e) => { e.preventDefault(); addSlangRule(); }} class="lexicon-form">
					<input type="text" bind:value={newSlang} placeholder="Kata slang (cth: ajg)" required />
					<span class="arrow-indicator">➔</span>
					<input type="text" bind:value={newFormal} placeholder="Kata baku (cth: anjing)" required />
					<button type="submit" class="btn-primary btn-add">
						<Plus size={16} />
					</button>
				</form>

				<div class="search-wrapper" style="margin: 12px 0 8px;">
					<span class="search-icon-inside">
						<Search size={14} />
					</span>
					<input 
						type="text" 
						bind:value={searchSlang} 
						placeholder="Cari kata slang atau baku..." 
						class="search-input"
						style="padding: 8px 12px 8px 32px; font-size: 0.85rem; background: rgba(0, 0, 0, 0.1);"
					/>
				</div>

				<div class="lexicon-list-scroll">
					<div class="lexicon-list">
						{#each filteredSlangList as item}
							<div class="lexicon-item">
								<span class="slang-term">{item.slang}</span>
								<span class="arrow">➔</span>
								<span class="formal-term">{item.formal}</span>
								<button onclick={() => removeSlangRule(item.slang)} class="btn-delete" aria-label="Hapus">
									<Trash2 size={14} />
								</button>
							</div>
						{:else}
							<p style="font-size: 0.85rem; color: var(--text-secondary); text-align: center; padding: 16px 0;">Tidak ada slang yang cocok.</p>
						{/each}
					</div>
				</div>
			</div>

			<!-- Kamus Toxic (DFA) -->
			<div class="glass-card lexicon-card">
				<h3>Kamus Kata Toxic (Pencocokan DFA)</h3>
				<p class="section-desc">Kumpulan kosakata kasar yang akan ditandai sebagai TOXIC oleh DFA.</p>

				<form onsubmit={(e) => { e.preventDefault(); addToxicWord(); }} class="lexicon-form">
					<input type="text" bind:value={newToxic} placeholder="Kata kasar baru (cth: bego)" required />
					<button type="submit" class="btn-primary btn-add">
						<Plus size={16} />
					</button>
				</form>

				<div class="search-wrapper" style="margin: 12px 0 8px;">
					<span class="search-icon-inside">
						<Search size={14} />
					</span>
					<input 
						type="text" 
						bind:value={searchToxic} 
						placeholder="Cari kata toxic..." 
						class="search-input"
						style="padding: 8px 12px 8px 32px; font-size: 0.85rem; background: rgba(0, 0, 0, 0.1);"
					/>
				</div>

				<div class="lexicon-list-scroll">
					<div class="lexicon-list">
						{#each filteredToxicList as word}
							<div class="lexicon-item">
								<span class="toxic-term">{word}</span>
								<button onclick={() => removeToxicWord(word)} class="btn-delete" aria-label="Hapus">
									<Trash2 size={14} />
								</button>
							</div>
						{:else}
							<p style="font-size: 0.85rem; color: var(--text-secondary); text-align: center; padding: 16px 0;">Tidak ada kata toxic yang cocok.</p>
						{/each}
					</div>
				</div>
			</div>
		</div>

		<!-- FAQ (from wireframe) -->
		<div class="glass-card faq-card">
			<h2 class="guide-title text-center" style="display: flex; align-items: center; justify-content: center; gap: 8px;"><HelpCircle size={22} color="var(--color-accent)" /> FAQ & Tips</h2>
			<div class="faq-list">
				{#each faqs as faq, index}
					{@const isOpen = activeFaq === index}
					<div class="faq-item" class:open={isOpen}>
						<!-- svelte-ignore a11y_click_events_have_key_events -->
						<!-- svelte-ignore a11y_no_static_element_interactions -->
						<div class="faq-question" onclick={() => toggleFaq(index)}>
							<span>{faq.q}</span>
							<span class="chevron" class:rotated={isOpen} style="display: flex; align-items: center;"><ChevronDown size={16} /></span>
						</div>
						{#if isOpen}
							<div class="faq-answer animate-fade-in">
								<p>{faq.a}</p>
							</div>
						{/if}
					</div>
				{/each}
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

	.guide-layout {
		display: flex;
		flex-direction: column;
		gap: 24px;
		margin-bottom: 32px;
	}

	.guide-card {
		padding: 24px;
	}

	.guide-title {
		font-size: 1.35rem;
		font-weight: 700;
		margin-bottom: 20px;
	}

	.quick-steps {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 20px;
	}

	.quick-step {
		display: flex;
		align-items: flex-start;
		gap: 16px;
		background: rgba(0, 0, 0, 0.15);
		padding: 20px;
		border-radius: var(--radius-md);
		border: 1px solid var(--card-border);
	}

	:root[data-theme='light'] .quick-step {
		background: rgba(0, 0, 0, 0.02);
	}

	.step-icon {
		font-size: 1.8rem;
		line-height: 1;
	}

	.step-info h3 {
		font-size: 1.05rem;
		font-weight: 600;
		margin-bottom: 6px;
	}

	.step-info p {
		font-size: 0.85rem;
		color: var(--text-secondary);
		line-height: 1.5;
	}

	.guide-title-section {
		border-bottom: 1px solid var(--card-border);
		padding-bottom: 8px;
		margin-top: 8px;
	}

	.guide-title-section h2 {
		font-size: 1.35rem;
		font-weight: 700;
	}

	/* Memahami Hasil */
	.info-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 24px;
	}

	.info-card {
		padding: 24px;
		display: flex;
		flex-direction: column;
	}

	/* ponytail: removed side colored borders to avoid generic generated-AI aesthetics */

	.text-safe {
		color: var(--color-safe);
	}

	.text-toxic {
		color: var(--color-toxic);
	}

	.status-desc {
		font-size: 0.9rem;
		color: var(--text-secondary);
		margin-bottom: 16px;
		flex: 1;
	}

	.example-box {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.label {
		font-size: 0.72rem;
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
		font-size: 0.9rem;
		font-family: var(--font-sans);
		font-style: italic;
	}

	:root[data-theme='light'] .val-box {
		background: rgba(0, 0, 0, 0.03);
	}

	/* FAQ accordion styling */
	.faq-card {
		padding: 24px;
	}

	.text-center {
		text-align: center;
	}

	.faq-list {
		display: flex;
		flex-direction: column;
		gap: 12px;
		max-width: 700px;
		margin: 0 auto;
	}

	.faq-item {
		border: 1px solid var(--card-border);
		border-radius: var(--radius-md);
		overflow: hidden;
		transition: var(--transition-smooth);
	}

	.faq-item.open {
		border-color: var(--color-accent);
	}

	.faq-question {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 16px 20px;
		cursor: pointer;
		font-weight: 600;
		font-size: 0.95rem;
		user-select: none;
		background: rgba(255, 255, 255, 0.02);
	}

	:root[data-theme='light'] .faq-question {
		background: rgba(0, 0, 0, 0.01);
	}

	.faq-question:hover {
		background: rgba(255, 255, 255, 0.04);
	}

	:root[data-theme='light'] .faq-question:hover {
		background: rgba(0, 0, 0, 0.02);
	}

	.faq-answer {
		padding: 16px 20px;
		background: rgba(0, 0, 0, 0.15);
		border-top: 1px solid var(--card-border);
		font-size: 0.88rem;
		color: var(--text-secondary);
		line-height: 1.6;
		animation: slideDown 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
	}

	:root[data-theme='light'] .faq-answer {
		background: rgba(0, 0, 0, 0.01);
	}

	.chevron {
		font-size: 0.7rem;
		color: var(--text-secondary);
		transition: transform 0.3s ease;
	}

	.chevron.rotated {
		transform: rotate(180deg);
	}

	/* Lexicon manager styles */
	.lexicon-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 24px;
		margin-bottom: 32px;
	}

	.lexicon-card {
		padding: 24px;
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.lexicon-card h3 {
		font-size: 1.05rem;
		font-weight: 700;
		color: var(--color-accent);
	}

	.section-desc {
		font-size: 0.82rem;
		color: var(--text-secondary);
		margin-bottom: 6px;
	}

	.lexicon-form {
		display: flex;
		align-items: center;
		gap: 8px;
		margin-bottom: 12px;
	}

	.lexicon-form input {
		flex: 1;
		padding: 8px 12px;
		font-size: 0.88rem;
	}

	.arrow-indicator {
		color: var(--text-secondary);
		font-weight: 700;
	}

	.btn-add {
		padding: 8px 14px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: var(--radius-md);
		cursor: pointer;
	}

	.lexicon-list-scroll {
		max-height: 220px;
		overflow-y: auto;
		border: 1px solid var(--card-border);
		border-radius: var(--radius-md);
		background: rgba(0, 0, 0, 0.15);
		padding: 8px;
	}

	:root[data-theme='light'] .lexicon-list-scroll {
		background: rgba(0, 0, 0, 0.02);
	}

	.lexicon-list {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.lexicon-item {
		display: flex;
		align-items: center;
		background: rgba(255, 255, 255, 0.02);
		border: 1px solid var(--card-border);
		padding: 8px 12px;
		border-radius: 6px;
		font-size: 0.88rem;
		font-family: var(--font-sans);
		transition: var(--transition-smooth);
	}

	.lexicon-item:hover {
		background: rgba(255, 255, 255, 0.04);
	}

	.slang-term {
		font-weight: 700;
		color: var(--color-accent);
		font-family: var(--font-mono);
	}

	.arrow {
		margin: 0 8px;
		color: var(--text-secondary);
	}

	.formal-term {
		font-weight: 500;
		color: var(--text-primary);
	}

	.toxic-term {
		font-weight: 600;
		color: var(--color-toxic);
		font-family: var(--font-sans);
	}

	.btn-delete {
		margin-left: auto;
		background: transparent;
		color: var(--text-secondary);
		border: none;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 4px;
		border-radius: 4px;
		transition: var(--transition-smooth);
	}

	.btn-delete:hover {
		color: var(--color-toxic);
		background: var(--color-toxic-light);
	}

	@media (max-width: 768px) {
		.quick-steps, .info-grid, .lexicon-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
