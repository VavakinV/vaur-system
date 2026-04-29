<template>
    <button class="btn" v-bind="$attrs">
        <slot></slot>
    </button>
</template>

<script>
export default {
    name: 'custom-button',
    inheritAttrs: false 
}
</script>

<style scoped>
.btn {
    font-size: 16px;
    font-weight: 400;
    color: #f3f6f4;
    
    padding: 10px 20px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    
    background: #005b96;
    border: 1px solid #03396c;
    border-radius: 8px;

    cursor: pointer;
    user-select: none;
    outline: none;
    
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: 
        background-color 0.2s ease, 
        transform 0.1s ease, 
        opacity 0.2s ease, 
        box-shadow 0.2s ease;
}

.btn:hover:not(:disabled) {
    opacity: 0.95;
    background-color: #01548a;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn:active:not(:disabled) {
    transform: scale(0.96);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.btn:focus-visible {
    box-shadow: 0 0 0 3px rgba(100, 151, 177, 0.5);
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    filter: grayscale(0.3);
    box-shadow: none;
}
</style>