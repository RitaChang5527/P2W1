
check();
const currentUrl = window.location.href;
const parts = currentUrl.split('/');
const attractionId = parts[4];
let url = "/api/attraction/" + attractionId;
fetch(url)
    .then(response => {
        console.log(url)
        if (response.status === 200) {
            console.log(url)
            return response.json();
        } else {
            throw new Error('Failed to fetch attraction data');
        }
    })
    .then(data => {
        console.log('Data:', data);
        const nameElement = document.querySelector(".name");
        nameElement.textContent = data.data.name;
        const positionElement = document.querySelector(".position");
        const positionText = `${data.data.category} at ${data.data.mrt}`;
        positionElement.textContent = positionText;
        const descriptionElement = document.querySelector(".description");
        descriptionElement.textContent = data.data.description;
        const addressElement = document.querySelector(".addressInfo");
        addressElement.textContent = data.data.address;
        const transportElement = document.querySelector(".transportInfo");
        transportElement.textContent = data.data.transport;
        const imgElement = document.getElementById("imageElement");
        imgElement.src = data.data.images[0];
    });


    async function check() {
        const token = localStorage.getItem("token");
        const response = await fetch("/api/user/auth", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
            });
            console.log(token);
            if (token !== null) { 
                console.log("123")
                const data = await response.json();
                console.log(data);
                document.querySelector(".sign").style.display = "none";
                document.querySelector(".item-login").style.display = "none";
                document.querySelector(".item-signout").style.display = "block";
            } else {
                console.log("333")
                document.querySelector(".item-login").style.display = "block";
                document.querySelector(".item-signout").style.display = "none";
            }
        } 



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
});

let PM = document.querySelector(".PM");
PM.addEventListener("click", function () {
    let price = document.querySelector(".money");
    price.innerText = "2500";
});
let AM = document.querySelector(".AM");
AM.addEventListener("click", function () {
    let price = document.querySelector(".money");
    price.innerText = "2000";
});

const order_btn = document.querySelector(".forBooking");
order_btn.addEventListener("click", function(event) {
    event.preventDefault();
    booking(); 
});

async function booking() {
    const token = localStorage.getItem("token");
    console.log(token)
    await fetch("/api/user/auth")
    if (!token) {
        document.querySelector(".sign").style.display = "block";
        document.querySelector(".loginBox").style.display = "block";
        document.querySelector(".signupBox").style.display = "none";
    }else{
        console.log("111")   
        const selectedDate = document.querySelector(".dateInput");
        let date = new Date()
        selectedDate.min = date.getFullYear().toString() + '-' +
        (date.getMonth() + 1).toString().padStart(2, 0) + '-' +
        date.getDate().toString().padStart(2, 0);

        const selectedTime = document.querySelector("input[name='time']:checked"); //value
        const selectedPrice = document.querySelector(".money").innerText;

        
        if (selectedTime.checked == false) {
            alert("請點選您要上半天還是下半天");
        } else if (date == "") {
            alert("請點選日期");
        }
        let url = `/api${location.pathname}`;
        const url_split = url.split("/");
        const attraction_id = url_split[3];

        fetch("/api/booking", {
            method: "POST",
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                attractionID: attraction_id,
                date: selectedDate.value=="" ? selectedDate.min : selectedDate.value,
                time: selectedTime.value,
                price:Number(selectedPrice) ,
            }),
        })
        .then((response) => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then((result) => {
            console.log(result);
            if (result.ok) {
                console.log("223");
                window.location.href = "/booking";
            } else {
                console.log("error")
            }
        });
    }
};
