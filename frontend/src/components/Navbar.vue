<template>
    <div class="navbar">
        <h2 class="logo" @click="$router.push('/')">Система ВАУР</h2>
        <div class="navbar__btns">
            <custom-button @click="$router.push('/works')" style="margin-left: 20px;">Мои работы</custom-button>
            <custom-button @click="$router.push('/')" style="margin-left: 20px;">Мои заявки</custom-button>
        </div>
    </div>
</template>

<script>
export default{

}
</script>

<style scoped>
.navbar {
    height: 100px;
    background-color:#6497b1;
    box-shadow: 2px 2px 4px gray;
    display: flex;
    align-items: center;
    padding: 0 15px;
}
.navbar__btns{
    margin-left: auto;
}
.logo {
    font-size: 36px;
    cursor: pointer;
    color: #011f4b;
}
</style>