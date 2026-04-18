<template>
    <button class="btn">
        <slot></slot>
    </button>
</template>

<script>
export default{
    name: 'custom-button'
}
</script>

<style scoped>
.btn {
    font-size: 16px;
    color: #f3f6f4;
    padding: 10px 15px;
    background: none;
    background:#005b96;
    border: 1px solid #03396c;
    cursor: pointer;
    border-radius: 8px;
    transition: transform 0.15s ease, opacity 0.2s ease;
}
.btn:hover {
    opacity: 0.9;
}
</style>