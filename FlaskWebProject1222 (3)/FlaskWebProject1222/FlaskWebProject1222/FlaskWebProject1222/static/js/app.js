const app = Vue.createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            searchQuery: '',
            apis: []
        }
    },
    computed: {
        filteredApis() {
            if (!this.searchQuery) {
                return this.apis;
            }
            return this.apis.filter(api =>
                api.title.toLowerCase().includes(this.searchQuery.toLowerCase())
            );
        }
    },
    mounted() {
        fetch('/api/products')
            .then(response => response.json())
            .then(data => {
                this.apis = data;
            })
            .catch(error => console.error('Error fetching products:', error));
    }
});

app.mount('#app');

document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("add-item-modal");
    const closeModalButton = document.querySelector(".close-modal");
    const addItemButton = document.querySelector(".add-button");

    addItemButton.addEventListener("click", function () {
        modal.style.display = "flex";
    });

    closeModalButton.addEventListener("click", function () {
        modal.style.display = "none";
    });

    window.addEventListener("click", function (event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    });

    document.getElementById("add-api-form").addEventListener("submit", function (event) {
        event.preventDefault();

        const apiName = document.getElementById("api-name").value;
        const apiDescription = document.getElementById("api-description").value;
        const apiImage = document.getElementById("api-image").files[0];
        const apiBasicPrice = document.getElementById("api-basic-price").value;
        const apiAdvancedPrice = document.getElementById("api-advanced-price").value;
        const apiEnterprisePrice = document.getElementById("api-enterprise-price").value;
        const apiDocumentation = document.getElementById("api-documentation").files[0];

        const formData = new FormData();
        formData.append('api-name', apiName);
        formData.append('api-description', apiDescription);
        formData.append('api-image', apiImage);
        formData.append('api-basic-price', apiBasicPrice);
        formData.append('api-advanced-price', apiAdvancedPrice);
        formData.append('api-enterprise-price', apiEnterprisePrice);
        formData.append('api-documentation', apiDocumentation);

        fetch('/add-api', {
            method: 'POST',
            body: formData
        }).then(response => response.json())
            .then(data => {
                app.addApi(data);
                modal.style.display = "none";
            }).catch(error => console.error('Error:', error));

        modal.style.display = "none";
    });
});