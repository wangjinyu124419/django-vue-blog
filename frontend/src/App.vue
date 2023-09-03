<template>
    <div v-for="article in info" v-bind:key="article.url" id="articles">
        <div>
            <span
                  v-for="tag in article.tags"
                  v-bind:key="tag"
                  class="tag"
            >
                {{ tag.name }}
            </span>
        </div>
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
                .get('/api/article/' )
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