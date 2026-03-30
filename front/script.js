// ------------------------------
// GET NEWS
//-------------------------------
function showNewsButton(show) {
    if (show) {
        document.getElementById("showNews").classList.add("show");
    } else {
        document.getElementById("showNews").classList.remove("show");
    }
}

function getNews() {

    let url = 'http://127.0.0.1:5000/news';

    fetch(url, {
        method: 'get'
    })
        .then(async (response) => {
            const data = await response.json();
            if (!response.ok)
                throw new Error(data.message || "Request failed");
            return data;
        })
        .then((data) => {
            const news = data.news;
            const tbody = document.querySelector("table tbody");
            tbody.innerHTML = "";
            if (news && news.length > 0 && news[0].id) {
                news.forEach((news) => {
                    const tr = document.createElement("tr");
                    tr.innerHTML += `<td><div class="cell-clamp">${news.title}</div></td>`
                    tr.innerHTML += `<td><div class="cell-clamp">${news.text}</div></td>`
                    const label = Number(news.label) ? "Real" : "Fake";
                    tr.innerHTML += `<td class="label label-${label.toLowerCase()}"><div class="cell-clamp">${label}</div></td>`
                    tr.innerHTML += `<td class="delete-news"><div class="cell-clamp"><button data-id="${news.id}"><img src="img/trash-icon.png"></button></div></td>`
                    tbody.appendChild(tr);
                });
                bindDeleteNewsEvents();
                showNewsButton(true);
            } else {
                const tr = document.createElement("tr");
                tr.innerHTML += `<td colspan="4">No news registered in the database</td>`;
                tbody.appendChild(tr);
                showNewsButton(false);
            }
        })
        .catch((error) => {
            alert(error);
            throw error;
        });

}

getNews();

function deleteNews(event) {

    if (!window.confirm("Are you sure you want to delete this news?"))
        return;

    const newsId = this.dataset.id;

    let url = 'http://127.0.0.1:5000/news/' + newsId;

    fetch(url, {
        method: 'delete'
    })
        .then(async (response) => {
            const data = await response.json();
            if (!response.ok)
                throw new Error(data.message || "Request failed");
            return data;
        })
        .then((data) => {
            alert(data.message);
            getNews();
        })
        .catch((error) => {
            alert(error);
            throw error;
        });

}

function bindDeleteNewsEvents() {
    const deleteNewsButtons = document.querySelectorAll(".delete-news button");
    deleteNewsButtons.forEach((item) => {
        item.addEventListener("click", deleteNews);
    });
}

// ------------------------------
// FORM
//-------------------------------

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
            .then(async (response) => {
                const data = await response.json();
                if (!response.ok)
                    throw new Error(data.message || "Request failed");
                return data;
            })
            .then((data) => {

                const news = data;

                const image = document.createElement("img");
                image.classList.add("label-image")

                let imageClass = Number(news.label) ? "real" : "fake";
                image.classList.add(imageClass)

                let imageName = Number(news.label) ? "real-news-stamp.png" : "fake-news-stamp.png";
                image.src = "img/" + imageName;

                document.querySelector("main").appendChild(image);

                setTimeout(() => {
                    image.classList.add("show");
                    setTimeout(() => { getNews(); }, 300);
                }, 100);
                setTimeout(() => {
                    image.classList.add("hide")
                    setTimeout(() => image.remove(), 700);
                }, 2000);

                document.querySelectorAll("#newsForm .input-group-item").forEach(item => item.value = "");
                document.querySelector("body").classList.add("full");

                return data;

            })
            .catch((error) => {
                alert(error);
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

// ------------------------------
// SHOW/CLOSE NEWS
//-------------------------------

document.getElementById("showNews").addEventListener("click", () => document.querySelector("body").classList.add("full"));
document.getElementById("closeNews").addEventListener("click", () => document.querySelector("body").classList.remove("full"));