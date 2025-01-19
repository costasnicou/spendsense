document.addEventListener('DOMContentLoaded', function () {
    const categoryField = document.getElementById('id_category');
    const subcategoryField = document.getElementById('id_subcategory');

    categoryField.addEventListener('change', function () {
        const category = categoryField.value;

        // Fetch subcategories dynamically
        fetch(`/load-subcategories/?category=${category}`)
            .then(response => response.json())
            .then(data => {
                subcategoryField.innerHTML = '';
                data.subcategories.forEach(function (subcategory) {
                    const option = document.createElement('option');
                    option.value = subcategory[0];
                    option.textContent = subcategory[1];
                    subcategoryField.appendChild(option);
                });
            });
    });
});