<script lang="ts">
	import { onMount } from 'svelte';
	import '../app.css';

	let { children } = $props();
	let theme = $state('dark');
	let activePath = $state('/');
	let logoLoaded = $state(true);

	onMount(() => {
		theme = localStorage.getItem('theme') || 'dark';
		document.documentElement.setAttribute('data-theme', theme);
		
		// Simple routing highlight check
		activePath = window.location.pathname;
	});

	function toggleTheme() {
		theme = theme === 'dark' ? 'light' : 'dark';
		localStorage.setItem('theme', theme);
		document.documentElement.setAttribute('data-theme', theme);
	}

	function handleNav(path: string) {
		activePath = path;
	}
</script>

<svelte:head>
	<link rel="icon" href="/logo.ico?v=1" />
	<title>Detox - Web-Based Automata Intelligence</title>
</svelte:head>

<div class="app-layout">
	<!-- Top Navigation -->
	<header class="navbar-wrapper">
		<div class="navbar-container glass-card">
			<a href="/" onclick={() => handleNav('/')} class="logo">
				{#if logoLoaded}
					<img src="/logo.webp" alt="Detox" class="logo-img" onerror={() => logoLoaded = false} />
				{:else}
					<span class="logo-icon">✓</span>
					<span class="logo-text">Detox</span>
				{/if}
			</a>
			
			<nav class="nav-links">
				<a href="/" onclick={() => handleNav('/')} class="nav-item" class:active={activePath === '/'}>
					Analyzer
				</a>
				<a href="/bulk" onclick={() => handleNav('/bulk')} class="nav-item" class:active={activePath === '/bulk'}>
					Bulk Checker
				</a>
				<a href="/riwayat" onclick={() => handleNav('/riwayat')} class="nav-item" class:active={activePath === '/riwayat'}>
					Riwayat
				</a>
				<a href="/panduan" onclick={() => handleNav('/panduan')} class="nav-item" class:active={activePath === '/panduan'}>
					Panduan
				</a>
			</nav>

			<button onclick={toggleTheme} class="theme-toggle" aria-label="Toggle Theme">
				{#if theme === 'dark'}
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
				{:else}
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
				{/if}
			</button>
		</div>
	</header>

	<!-- Main Content Area -->
	<main class="main-content">
		{@render children()}
	</main>

	<!-- Bottom Footer -->
	<footer class="footer-wrapper">
		<div class="footer-container">
			<p>© 2026 Group Greenflag · President University Pekanbaru</p>
			<p class="sub-text">Formal Language and Automata (FLA) · Lecturer: Shella Eldwina Fitri S.T., M.Eng</p>
		</div>
	</footer>
</div>

<style>
	.app-layout {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

	.navbar-wrapper {
		position: sticky;
		top: 0;
		z-index: 50;
		padding: 16px 16px 8px;
		max-width: 1000px;
		width: 100%;
		margin: 0 auto;
	}

	.navbar-container {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 12px 24px;
		border-radius: 9999px; /* Rounded pill style navbar */
	}

	.logo {
		display: flex;
		align-items: center;
		gap: 8px;
		font-weight: 800;
		font-size: 1.35rem;
		letter-spacing: -0.02em;
		color: var(--color-accent);
	}

	.logo-icon {
		background: var(--color-accent-light);
		color: var(--color-accent);
		width: 28px;
		height: 28px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.95rem;
	}

	.logo-img {
		height: 90px;
		width: auto;
		display: block;
		margin: -25px 0;
	}

	.nav-links {
		display: flex;
		gap: 16px;
	}

	.nav-item {
		font-size: 0.95rem;
		font-weight: 500;
		padding: 6px 16px;
		border-radius: 9999px;
		color: var(--text-secondary);
		transition: var(--transition-smooth);
	}

	.nav-item:hover, .nav-item.active {
		color: var(--text-primary);
		background: rgba(255, 255, 255, 0.06);
	}

	:root[data-theme='light'] .nav-item:hover, :root[data-theme='light'] .nav-item.active {
		background: rgba(0, 0, 0, 0.05);
	}

	.theme-toggle {
		background: rgba(255, 255, 255, 0.06);
		color: var(--text-primary);
		border: 1px solid var(--card-border);
		width: 38px;
		height: 38px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: var(--transition-smooth);
	}

	:root[data-theme='light'] .theme-toggle {
		background: rgba(0, 0, 0, 0.03);
	}

	.theme-toggle:hover {
		transform: scale(1.05);
		background: rgba(255, 255, 255, 0.12);
	}

	:root[data-theme='light'] .theme-toggle:hover {
		background: rgba(0, 0, 0, 0.08);
	}

	.main-content {
		flex: 1;
		display: flex;
		flex-direction: column;
	}

	.footer-wrapper {
		border-top: 1px solid var(--card-border);
		padding: 24px 16px;
		text-align: center;
		font-size: 0.85rem;
		color: var(--text-secondary);
		background: rgba(0, 0, 0, 0.1);
	}

	.footer-container {
		max-width: 1000px;
		margin: 0 auto;
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.sub-text {
		font-size: 0.75rem;
		opacity: 0.8;
	}

	@media (max-width: 640px) {
		.navbar-container {
			flex-direction: column;
			gap: 12px;
			border-radius: var(--radius-lg);
			padding: 16px;
		}

		.nav-links {
			width: 100%;
			justify-content: center;
		}

		.nav-item {
			padding: 6px 12px;
			font-size: 0.85rem;
		}
	}
</style>
