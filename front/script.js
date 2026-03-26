function onFormSubmit(event) {

    event.preventDefault();

    if (validateForm(this)) {

        const formData = new FormData();
        formData.append('title', this.querySelector("#title").value);
        formData.append('text', this.querySelector("#text").value);

        let url = 'http://127.0.0.1:5000/news';

        return fetch(url, {
            method: 'post',
            body: formData
        })
            .then((response) => response.json())
            .then((data) => {
                return data;
            })
            .catch((error) => {
                console.error('Error:', error);
                throw error;
            });
    }

}

function validateForm(form) {

    let valid = true;

    const titleElement = form.querySelector("#title");
    const textElement = form.querySelector("#text");

    titleElement.classList.remove("invalid");
    titleElement.nextElementSibling.innerHTML = "";
    textElement.classList.remove("invalid");
    textElement.nextElementSibling.innerHTML = "";

    if (!titleElement.value) {
        titleElement.classList.add("invalid");
        titleElement.nextElementSibling.innerHTML = "This field is required";
        valid = false;
    }

    if (!textElement.value) {
        textElement.classList.add("invalid");
        textElement.nextElementSibling.innerHTML = "This field is required";
        valid = false;
    } else if (textElement.value.length < 300) {
        textElement.classList.add("invalid");
        textElement.nextElementSibling.innerHTML = "The news text must be at least 300 characters long";
        valid = false;
    }

    return valid;

};

document.getElementById("newsForm").addEventListener("submit", onFormSubmit);

const formElements = document.querySelectorAll("#newsForm .input-group-item");
formElements.forEach((item) => {
    item.addEventListener("change", (event) => item.classList.remove("invalid"));
})