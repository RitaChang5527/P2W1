const currentUrl = window.location.href;
const parts = currentUrl.split('/');
const attractionIdIndex = parts.indexOf('attraction');
const attractionId = attractionIdIndex !== -1 ? parts[attractionIdIndex + 1] : null;

//console.log('Id:', attractionId);

fetch(`/api/attraction/${attractionId}`)
  .then(response => {
    if (response.status === 200) {
        return response.json();
    } else {
        throw new Error('Failed to fetch attraction data');
        }
})
  .then(data => {
    //console.log('Data:', data);
    
    const nameElement = document.querySelector(".name");
    const positionElement = document.querySelector(".position");
    const descriptionElement = document.querySelector(".description");
    const addressElement = document.querySelector(".addressInfo");
    const transportElement = document.querySelector(".transportInfo");
    const imgElement = document.getElementById("imageElement");

    if (data.data.name) {
        nameElement.textContent = data.data.name;
    } else {
        console.error('Name data is missing');
    }
    
    if (data.data.category && data.data.mrt) {
        const positionText = `${data.data.category} at ${data.data.mrt}`;
        positionElement.textContent = positionText;
        //console.log(positionText);
    } else {
        console.error('Position data is missing');
    }

    if (data.data.description) {
        descriptionElement.textContent = data.data.description;
    } else {
        console.error('Description data is missing');
    }

    if (data.data.address) {
        addressElement.textContent = data.data.address;
    } else {
        console.error('Address data is missing');
    }

    if (data.data.transport) {
        transportElement.textContent = data.data.transport;
    } else {
        console.error('Transport data is missing');
    }

    if (data.data.images) {
        //console.log(data.data);
        //console.log(data.data.images);
        imgElement.src = data.data.images[0];
    } else {
        console.error('Img data is missing');
    }
});

//*time and fee
const morningOption = document.getElementById("morningOption");
const afternoonOption = document.getElementById("afternoonOption");
const moneyElement = document.querySelector(".money");


morningOption.src = "../static/CSS/attraction/img/TimeSelect.png";
afternoonOption.src = "../static/CSS/attraction/img/TimeUnselect.png";
moneyElement.textContent = "新台幣2000元";

morningOption.addEventListener("click", function () {
    morningOption.classList.toggle("selected");
    if (morningOption.classList.contains("selected")) {
        morningOption.src = "../static/CSS/attraction/img/TimeSelect.png";
        afternoonOption.src = "../static/CSS/attraction/img/TimeUnselect.png";
        moneyElement.textContent = "新台幣2000元";
    } else {
        morningOption.src = "../static/CSS/attraction/img/TimeSelect.png";
        afternoonOption.src = "../static/CSS/attraction/img/TimeUnselect.png";
        moneyElement.textContent = "新台幣2000元";
    }
});

afternoonOption.addEventListener("click", function () {
    afternoonOption.classList.toggle("selected");
    if (afternoonOption.classList.contains("selected")) {
        afternoonOption.src = "../static/CSS/attraction/img/TimeSelect.png";
        morningOption.src = "../static/CSS/attraction/img/TimeUnselect.png";
        moneyElement.textContent = "新台幣2500元";
    } else {
        afternoonOption.src = "../static/CSS/attraction/img/TimeSelect.png";
        morningOption.src = "../static/CSS/attraction/img/TimeUnselect.png"
        moneyElement.textContent = "新台幣2500元";
    }
});

//* images
fetch(`/api/attraction/${attractionId}`)
  .then(response => {
    if (response.status === 200) {
        return response.json();
    } else {
        throw new Error('Failed to fetch attraction data');
    }
})
  .then(data => {
    const imgElement = document.getElementById("imageElement");
    const nextButton = document.getElementById("nextButton");
    const prevButton = document.getElementById("prevButton");
    const dotContainer = document.getElementById("dotContainer");
    const images = data.data.images || [];
    let currentIndex = 0;

    function updateImage() {
        const imageUrl = images[currentIndex];
        imgElement.src = imageUrl;
    }

    nextButton.addEventListener("click", () => {
        console.log("右按钮");
        currentIndex = (currentIndex + 1) % images.length;
        updateImage();
        updateDots();
    });

    prevButton.addEventListener("click", () => {
        console.log("左按钮");
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        updateImage();
        updateDots();
    });

    const firstDot = document.querySelector(".dot");
    if (firstDot) {
        firstDot.classList.add("active");
    }

    function createDots(images) {
        for (let i = 0; i < images.length; i++) {
            const dot = document.createElement("div");
            dot.classList.add("dot");
            dotContainer.appendChild(dot);
            dot.addEventListener("click", () => {
                currentIndex = i;
                updateImage();
                updateDots();
            });
            if (i === 0) {
                dot.classList.add("active");
            }
        }
    }

    function updateDots() {
        const dots = document.querySelectorAll(".dot");
        dots.forEach((dot, index) => {
            if (index === currentIndex) {
                dot.classList.add("active");
            } else {
                dot.classList.remove("active");
            }
        });
    }

    createDots(images);
    scrollImage();
});



