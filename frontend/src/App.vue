<template>
    <div v-for="article in info.results" v-bind:key="article.url" id="articles">
        <div class="article-title">
            {{ article.title }}
        </div>
    </div>
</template>

<script>
    import axios from 'axios';

    export default {
        name: 'App',
        data: function () {
            return {
                info: ''
            }
        },
        mounted() {
            axios
                .get('http://127.0.0.1:8000/article', {
    headers: {
   Referer: 'http://localhost:8080/'
 }
})
                .then(response => (this.info = response.data))
        }
    }
</script>

<style>
    #articles {
        padding: 10px;
    }

    .article-title {
        font-size: large;
        font-weight: bolder;
        color: black;
        text-decoration: none;
        padding: 5px 0 5px 0;
    }
</style>