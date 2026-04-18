<template>
    <div class="forbidden-view">
        <h1>403</h1>
        <p>У вас нет доступа к этой странице.</p>
    </div>
</template>

<script>
export default {
    name: "ForbiddenView"
}
</script>

<style scoped>
.forbidden-view {
    min-height: 100vh;
    padding: 24px;
    background: #f3f6f4;
}
</style>