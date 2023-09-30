
check();
const currentUrl = window.location.href;
const parts = currentUrl.split('/');
const attractionId = parts[4];
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

    async function check() {
        const token = localStorage.getItem("token");
    
        try {
            const response = await fetch("/api/user/auth", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
            });
            console.log(typeof token);
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
        } catch (error) {
            console.error("Error:", error);
        }
    }

//*time and fee
const morningOption = document.getElementById("morningOption");
const afternoonOption = document.getElementById("afternoonOption");
const moneyElement = document.querySelector(".money");


morningOption.src = "../static/CSS/attraction/img/TimeSelect.png";
afternoonOption.src = "../static/CSS/attraction/img/TimeUnselect.png";
moneyElement.textContent = "新台幣2000元";
morningOption.addEventListener("click", function () {
    toggleOption(true);
});

afternoonOption.addEventListener("click", function () {
    toggleOption(false);
});

function toggleOption(isMorning) {
    morningOption.classList.toggle("selected", isMorning);
    afternoonOption.classList.toggle("selected", !isMorning);

    if (isMorning) {
        morningOption.src = "../static/CSS/attraction/img/TimeSelect.png";
        afternoonOption.src = "../static/CSS/attraction/img/TimeUnselect.png";
        moneyElement.textContent = "新台幣2000元";
    } else {
        morningOption.src = "../static/CSS/attraction/img/TimeUnselect.png";
        afternoonOption.src = "../static/CSS/attraction/img/TimeSelect.png";
        moneyElement.textContent = "新台幣2500元";
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
        document.querySelector(".loginBox").style.display = "none";
        document.querySelector(".signupBox").style.display = "block";
    }else{
        console.log("111")   
        const selectedDate = document.querySelector(".dateInput");
        let date = new Date()
        selectedDate.min = date.getFullYear().toString() + '-' +
        (date.getMonth() + 1).toString().padStart(2, 0) + '-' +
        date.getDate().toString().padStart(2, 0);

        let selectedTime = "morning";
        let selectedPrice = 2000;
        console.log(selectedTime,selectedPrice) 
        document.getElementById("morningOption").addEventListener("click", function() {
            selectedTime = "morning";
            selectedPrice= 2000;
            console.log(selectedTime,selectedPrice) 
        });
        document.getElementById("afternoonOption").addEventListener("click", function() {
            console.log("112")
            selectedTime = "afternoon";
            selectedPrice= 2500;
            console.log(selectedTime,selectedPrice)
        });
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
                time: selectedTime,
                price: selectedPrice,
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
