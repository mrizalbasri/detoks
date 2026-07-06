<script lang="ts">
	import { onDestroy, untrack } from 'svelte';
	import { Play, Pause, RotateCcw, ChevronRight, ChevronLeft } from '@lucide/svelte';

	// Svelte 5 Runes for props
	let { dfaPath = '', normalizedText = '' } = $props();

	// Parse states from the string path
	let states = $derived(
		dfaPath
			? dfaPath.split(' → ').map((s: string) => s.trim())
			: []
	);

	let activeIndex = $state(0);
	let isPlaying = $state(true);
	let speed = $state(800); // ms per step
	let timer: any = null;

	// Reset visualization state when path changes
	$effect(() => {
		const path = dfaPath; // Track dfaPath
		untrack(() => {
			activeIndex = 0;
			if (isPlaying) {
				startPlayback();
			} else {
				stopPlayback();
			}
		});
	});

	function startPlayback() {
		stopPlayback();
		isPlaying = true;
		timer = setInterval(() => {
			if (activeIndex < states.length - 1) {
				activeIndex++;
			} else {
				stopPlayback();
			}
		}, speed);
	}

	function stopPlayback() {
		isPlaying = false;
		if (timer) {
			clearInterval(timer);
			timer = null;
		}
	}

	function togglePlay() {
		if (isPlaying) {
			stopPlayback();
		} else {
			if (activeIndex >= states.length - 1) {
				activeIndex = 0;
			}
			startPlayback();
		}
	}

	function resetPlayback() {
		stopPlayback();
		activeIndex = 0;
		startPlayback();
	}

	function stepForward() {
		stopPlayback();
		if (activeIndex < states.length - 1) {
			activeIndex++;
		}
	}

	function stepBackward() {
		stopPlayback();
		if (activeIndex > 0) {
			activeIndex--;
		}
	}

	onDestroy(() => {
		stopPlayback();
	});

	// Constants for SVG positioning
	const nodeRadius = 24;
	const nodeSpacing = 110;
	const paddingY = 40;
	const paddingX = 40;

	let svgWidth = $derived(Math.max(400, states.length * nodeSpacing + paddingX * 2));
	let svgHeight = paddingY * 2;
</script>

<div class="visualizer-card animate-fade-in">
	<div class="visualizer-controls">
		<div class="controls-left">
			<button 
				onclick={togglePlay} 
				class="control-btn main-play-btn" 
				aria-label={isPlaying ? 'Pause simulation' : 'Start simulation'}
			>
				{#if isPlaying}
					<Pause size={16} />
				{:else}
					<Play size={16} />
				{/if}
			</button>
			
			<button onclick={stepBackward} class="control-btn" disabled={activeIndex === 0} aria-label="Step backward">
				<ChevronLeft size={16} />
			</button>
			
			<button onclick={stepForward} class="control-btn" disabled={activeIndex === states.length - 1} aria-label="Step forward">
				<ChevronRight size={16} />
			</button>

			<button onclick={resetPlayback} class="control-btn" aria-label="Reset simulation">
				<RotateCcw size={15} />
			</button>
		</div>

		<div class="controls-right">
			<span class="step-counter">Langkah: {activeIndex + 1}/{states.length}</span>
			<label class="speed-slider-label">
				<span>Tempo:</span>
				<input 
					type="range" 
					min="300" 
					max="2000" 
					step="100" 
					bind:value={speed} 
					onchange={() => { if (isPlaying) startPlayback(); }}
					class="speed-slider"
				/>
				<span class="speed-value">{speed}ms</span>
			</label>
		</div>
	</div>

	<!-- Scrollable Container for SVG -->
	<div class="dfa-path-scroll visualizer-canvas-wrapper">
		<svg width={svgWidth} height={svgHeight} class="automata-svg">
			<defs>
				<!-- Arrow marker definitions -->
				<marker 
					id="arrow-inactive" 
					viewBox="0 0 10 10" 
					refX="8" 
					refY="5" 
					markerWidth="6" 
					markerHeight="6" 
					orient="auto-start-reverse"
				>
					<path d="M 0 1 L 10 5 L 0 9 z" fill="var(--text-secondary)" opacity="0.3" />
				</marker>
				<marker 
					id="arrow-active" 
					viewBox="0 0 10 10" 
					refX="8" 
					refY="5" 
					markerWidth="6" 
					markerHeight="6" 
					orient="auto-start-reverse"
				>
					<path d="M 0 1 L 10 5 L 0 9 z" fill="var(--color-accent)" />
				</marker>
				
				<!-- Glowing filters -->
				<filter id="glow-cyan" x="-20%" y="-20%" width="140%" height="140%">
					<feGaussianBlur stdDeviation="5" result="blur" />
					<feComposite in="SourceGraphic" in2="blur" operator="over" />
				</filter>
				<filter id="glow-rose" x="-20%" y="-20%" width="140%" height="140%">
					<feGaussianBlur stdDeviation="6" result="blur" />
					<feComposite in="SourceGraphic" in2="blur" operator="over" />
				</filter>
				<filter id="glow-emerald" x="-20%" y="-20%" width="140%" height="140%">
					<feGaussianBlur stdDeviation="6" result="blur" />
					<feComposite in="SourceGraphic" in2="blur" operator="over" />
				</filter>
			</defs>

			<!-- Draw transition lines first so they sit behind nodes -->
			{#each states as state, idx}
				{#if idx < states.length - 1}
					{@const x1 = paddingX + idx * nodeSpacing + nodeRadius}
					{@const y1 = paddingY}
					{@const x2 = paddingX + (idx + 1) * nodeSpacing - nodeRadius}
					{@const y2 = paddingY}
					{@const isLineActive = activeIndex > idx}
					<line 
						{x1} {y1} {x2} {y2} 
						class="transition-line" 
						class:active={isLineActive}
						stroke={isLineActive ? "var(--color-accent)" : "var(--text-secondary)"}
						stroke-dasharray={isLineActive ? "none" : "4,4"}
						stroke-width={isLineActive ? 3.5 : 1.5}
						stroke-opacity={isLineActive ? 1.0 : 0.25}
						marker-end={isLineActive ? "url(#arrow-active)" : "url(#arrow-inactive)"}
					/>
				{/if}
			{/each}

			<!-- Draw nodes on top -->
			{#each states as state, idx}
				{@const cx = paddingX + idx * nodeSpacing}
				{@const cy = paddingY}
				
				<!-- Node flags -->
				{@const isCurrent = activeIndex === idx}
				{@const isVisited = activeIndex >= idx}
				{@const isToxic = state.toUpperCase().includes('TOXIC')}
				{@const isSafe = state.toUpperCase().includes('SAFE')}
				
				<!-- Node Class & Glow styles -->
				{@const fillClass = isCurrent 
					? (isToxic ? 'node-current-toxic' : (isSafe ? 'node-current-safe' : 'node-current-accent')) 
					: (isVisited ? 'node-visited' : 'node-unvisited')}
				
				<g class="node-group">
					<!-- Pulsing glow behind active node -->
					{#if isCurrent}
						<circle 
							{cx} {cy} 
							r={nodeRadius + 4} 
							fill="none" 
							stroke={isToxic ? "var(--color-toxic)" : (isSafe ? "var(--color-safe)" : "var(--color-accent)")}
							stroke-width="2.5"
							opacity="0.8"
							filter={isToxic ? "url(#glow-rose)" : (isSafe ? "url(#glow-emerald)" : "url(#glow-cyan)")}
							class={isToxic ? 'pulsing-node-toxic' : (isSafe ? 'pulsing-node-safe' : 'pulsing-node-accent')}
						/>
					{/if}

					<!-- Main circle -->
					<circle 
						{cx} {cy} 
						r={nodeRadius} 
						class="node-circle {fillClass}"
						stroke={isCurrent ? (isToxic ? "var(--color-toxic)" : (isSafe ? "var(--color-safe)" : "var(--color-accent)")) : (isVisited ? "var(--text-primary)" : "var(--text-secondary)")}
						stroke-width={isCurrent ? 3 : 1.5}
						stroke-opacity={isVisited ? 1.0 : 0.3}
					/>

					<!-- Label inside node -->
					<text 
						x={cx} 
						y={cy + 5} 
						text-anchor="middle" 
						class="node-text"
						class:text-active={isVisited}
						fill={isVisited ? "var(--text-primary)" : "var(--text-secondary)"}
						opacity={isVisited ? 1.0 : 0.4}
					>
						{state}
					</text>
				</g>
			{/each}
		</svg>
	</div>
</div>

<style>
	.visualizer-card {
		background: rgba(0, 0, 0, 0.15);
		border: 1px solid var(--card-border);
		border-radius: var(--radius-md);
		overflow: hidden;
		padding: 12px;
		display: flex;
		flex-direction: column;
		gap: 12px;
		margin-top: 8px;
	}

	:root[data-theme='light'] .visualizer-card {
		background: rgba(255, 255, 255, 0.35);
	}

	.visualizer-controls {
		display: flex;
		justify-content: space-between;
		align-items: center;
		flex-wrap: wrap;
		gap: 12px;
		padding-bottom: 8px;
		border-bottom: 1px solid var(--card-border);
	}

	.controls-left {
		display: flex;
		align-items: center;
		gap: 6px;
	}

	.control-btn {
		width: 32px;
		height: 32px;
		border-radius: var(--radius-md);
		background: rgba(255, 255, 255, 0.05);
		color: var(--text-primary);
		border: 1px solid var(--card-border);
		display: flex;
		align-items: center;
		justify-content: center;
		transition: var(--transition-smooth);
	}

	:root[data-theme='light'] .control-btn {
		background: rgba(0, 0, 0, 0.03);
	}

	.control-btn:hover:not(:disabled) {
		background: rgba(255, 255, 255, 0.12);
		transform: scale(1.05);
	}

	:root[data-theme='light'] .control-btn:hover:not(:disabled) {
		background: rgba(0, 0, 0, 0.08);
	}

	.control-btn:disabled {
		opacity: 0.35;
		cursor: not-allowed;
	}

	.control-btn.main-play-btn {
		background: var(--color-accent) !important;
		color: #ffffff !important;
		border: none;
	}

	.control-btn.main-play-btn:hover:not(:disabled) {
		background: var(--color-accent-hover) !important;
	}

	.controls-right {
		display: flex;
		align-items: center;
		gap: 16px;
		font-size: 0.8rem;
		color: var(--text-secondary);
	}

	.step-counter {
		font-family: var(--font-mono);
		font-weight: 500;
		background: rgba(255, 255, 255, 0.05);
		padding: 4px 8px;
		border-radius: var(--radius-md);
	}

	:root[data-theme='light'] .step-counter {
		background: rgba(0, 0, 0, 0.03);
	}

	.speed-slider-label {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.speed-slider {
		width: 80px;
		cursor: pointer;
		height: 4px;
		background: rgba(255, 255, 255, 0.1);
		border-radius: 999px;
		outline: none;
	}

	.speed-value {
		font-family: var(--font-mono);
		width: 42px;
		text-align: right;
	}

	.visualizer-canvas-wrapper {
		width: 100%;
		overflow-x: auto;
		background: rgba(0, 0, 0, 0.2);
		border-radius: var(--radius-md);
		padding: 4px 0;
	}

	:root[data-theme='light'] .visualizer-canvas-wrapper {
		background: rgba(255, 255, 255, 0.45);
	}

	.automata-svg {
		display: block;
		margin: 0 auto;
	}

	/* Node Circle Styles */
	.node-circle {
		fill: #111827;
		r: 24px;
		transition: fill 0.3s ease, stroke 0.3s ease, r 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
	}

	:root[data-theme='light'] .node-circle {
		fill: #f3f4f6;
	}

	.node-unvisited {
		fill-opacity: 0.2;
	}

	.node-visited {
		fill-opacity: 0.85;
	}

	.node-current-accent {
		fill: var(--color-accent-light) !important;
		fill-opacity: 1;
		r: 28px;
	}

	.node-current-toxic {
		fill: var(--color-toxic-light) !important;
		fill-opacity: 1;
		r: 28px;
	}

	.node-current-safe {
		fill: var(--color-safe-light) !important;
		fill-opacity: 1;
		r: 28px;
	}

	.node-text {
		font-family: var(--font-mono);
		font-size: 0.78rem;
		font-weight: 700;
		pointer-events: none;
		transition: fill 0.3s ease, opacity 0.3s ease;
	}

	.text-active {
		font-weight: 800;
	}

	.transition-line {
		transition: stroke 0.3s ease, stroke-width 0.3s ease, stroke-opacity 0.3s ease;
	}

	.transition-line.active {
		stroke-dasharray: 6, 4;
		animation: flowLine 1.2s linear infinite;
	}

	@keyframes flowLine {
		from {
			stroke-dashoffset: 20;
		}
		to {
			stroke-dashoffset: 0;
		}
	}


</style>
