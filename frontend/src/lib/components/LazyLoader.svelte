<script>
	import { onMount } from 'svelte';
	
	export let component;
	export let props = {};
	export let loadingText = '加载中...';
	export let errorText = '加载失败';
	
	let loadedComponent = null;
	let loading = true;
	let error = null;
	
	onMount(async () => {
		try {
			const module = await component();
			loadedComponent = module.default || module;
			loading = false;
		} catch (err) {
			error = err;
			loading = false;
			console.error('组件加载失败:', err);
		}
	});
</script>

{#if loading}
	<div class="flex items-center justify-center h-32 bg-gray-50 rounded-lg">
		<div class="text-center">
			<div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto mb-2"></div>
			<p class="text-gray-500 text-sm">{loadingText}</p>
		</div>
	</div>
{:else if error}
	<div class="flex items-center justify-center h-32 bg-red-50 rounded-lg">
		<div class="text-center">
			<p class="text-red-500 text-sm">{errorText}</p>
			<button 
				class="mt-2 px-3 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600"
				on:click={() => window.location.reload()}
			>
				重新加载
			</button>
		</div>
	</div>
{:else if loadedComponent}
	<svelte:component this={loadedComponent} {...props} />
{/if}