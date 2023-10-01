const mrtsContainer = document.getElementById("mrts");
const LBtn = document.getElementById("list-Lbtn");
const RBtn = document.getElementById("list-Rbtn");
let mrtsData = [];
let startIndex = 0;
let numVisibleMrts = 33; 
let scrollAmount = 4; 
let itemWidth = 100;

window.addEventListener("resize", renderMrts);

LBtn.addEventListener("click", function () {
    console.log("左按钮");
    const scrollDistance = -scrollAmount * itemWidth;
    console.log(scrollDistance);

    mrtsContainer.scrollBy({
        left: -scrollAmount * itemWidth,
        behavior: "smooth"
    });
    
});

RBtn.addEventListener("click", function () {
    console.log("右按钮"); 

    const scrollDistance = scrollAmount * itemWidth;
    console.log(scrollDistance);

    mrtsContainer.scrollBy({
        left: scrollDistance,
        behavior: "smooth"
    });
});

fetch('/api/mrts')
    .then(response => {
        if (response.status === 200) {
            return response.json();
        } else {
            throw new Error('Failed to fetch data');
        }
    })
    .then(data => {
        mrtsData = data.data;
        //console.log("mrt:",mrtsData)
        renderMrts();
    })
    .catch(error => {
        console.error('Error:', error);
    });

renderMrts();

function renderMrts() {
    const visibleMrts = mrtsData.slice(startIndex, startIndex + numVisibleMrts);
    const mrtsHTML = visibleMrts.map(mrt => {
        //console.log(visibleMrts)
        return `<div class="mrt-item">${mrt}</div>`;
    }).join('');
    mrtsContainer.innerHTML = mrtsHTML;

    const mrtItems = document.querySelectorAll(".mrt-item");
    mrtItems.forEach(item => {
        item.addEventListener("click", function () {
            const selectedMrt = item.textContent;
            const searchInput = document.getElementById("search");
            searchInput.value = selectedMrt;
            searchAttractions(selectedMrt);
        });
    });
}


function searchAttractions(searchText) {
	fetch(`/api/attractions?page=0&keyword=${searchText}`)
		.then(response => {
			if (response.status === 200) {
				return response.json();
			} else {
				throw new Error('Failed to fetch data');
			}
		})
		.then(data => {
			const attractions = data.data;
			renderAttractions(attractions);
			addEmpty(attractions);
            nextPage = data.nextPage;
            keyword = searchText; 
		})
		.catch(error => {
			console.error('Error:', error);
		});
}

let scrollListener = handleScroll;

const searchBar = document.getElementById("search");
searchBar.addEventListener("input", function () {
    const searchText = searchBar.value.trim().toLowerCase();

    fetch(`/api/attractions?page=0&keyword=${searchText}`)
        .then(response => {
            if (response.status === 200) {
                return response.json();
            } else {
                throw new Error('Failed to fetch data');
            }
        })
        .then(data => {
            const attractions = data.data;
            renderAttractions(attractions);
            nextPage = data.nextPage;
            keyword = searchText; 
            console.log("[input] cur next page : " + nextPage + ", data next page : " + data.nextPage);

        })
        .catch(error => {
            console.error('Error:', error);
        });
});

function renderAttractions(attractions) {
    const attractionsContainer = document.getElementById("attractions");
    attractionsContainer.innerHTML = ""; 

    if (attractions.length > 0) {
        attractions.forEach(attraction => {
            const attractionBox = document.createElement("div");
            attractionBox.classList.add("attraction_box");

            attractionBox.setAttribute("data-attractionID", `${attraction.id}`);

            const imgDiv = document.createElement("div");
            imgDiv.classList.add("img");

            const img = document.createElement("img");
            img.src = attraction.images[0];
            img.alt = attraction.name;

            const nameDiv = document.createElement("div");
            nameDiv.classList.add("name");
            nameDiv.innerText = attraction.name;

            imgDiv.appendChild(img);
            imgDiv.appendChild(nameDiv);

            const describeDiv = document.createElement("div");
            describeDiv.classList.add("describe");

            const mrtDiv = document.createElement("div");
            mrtDiv.classList.add("mrt");
            mrtDiv.innerText = attraction.mrt; 

            const categoryDiv = document.createElement("div");
            categoryDiv.classList.add("category");
            categoryDiv.innerText = attraction.category; 

            describeDiv.appendChild(mrtDiv);
            describeDiv.appendChild(categoryDiv);

            attractionBox.appendChild(imgDiv);
            attractionBox.appendChild(describeDiv);

            attractionsContainer.appendChild(attractionBox);
        });
        
    } else {
        attractionsContainer.innerHTML = '<p>No results found.</p>';
    }
}



const container = document.getElementById("attractions");

fetch('/api/attractions?page=0')
    .then(response => {
        if (response.status === 200) {
            return response.json();
        } else {
            throw new Error('Failed to fetch data');
        }
    })
    .then(data => {
        createAttraction(data.data);
    })
    .catch(error => {
        console.error('Error:', error);
    });


function createAttraction(data) {
	data.forEach((item) => {
		let {id, name: attraction_name, category: attraction_category, mrt: attraction_mrt, images: [attraction_image] } = item;
		
        //* 建box每個景點的<div>
		let attractionContainer = document.createElement("div");
		attractionContainer.classList.add("attraction_box"); //*加class

        //* 加ID
        attractionContainer.setAttribute("data-attractionID", id);
		//* 圖片
		let img = document.createElement("img");
		img.src = attraction_image;
		//* 景點名稱
		let nameDiv = document.createElement("div");
		nameDiv.textContent = attraction_name;
		nameDiv.classList.add("name");
		//* 捷運站
		let attractionMrtDiv = document.createElement("div");
		attractionMrtDiv.textContent = attraction_mrt;
		attractionMrtDiv.classList.add("mrt");
		//* category
		let categoryDiv = document.createElement("div");
		categoryDiv.textContent = attraction_category;
		categoryDiv.classList.add("category");
		//* 描述
		let describeContainer = document.createElement("div");
		describeContainer.classList.add("describe");

		describeContainer.appendChild(attractionMrtDiv);
		describeContainer.appendChild(categoryDiv);

		let infoContainer = document.createElement("div");
		infoContainer.classList.add("img");

		infoContainer.appendChild(img);
		infoContainer.appendChild(nameDiv);

		attractionContainer.appendChild(infoContainer);
		attractionContainer.appendChild(describeContainer);

		container.appendChild(attractionContainer);
	});
}

document.addEventListener("DOMContentLoaded", function () {
    const parentElement = document.querySelector("#attractions");

    parentElement.addEventListener("click", (event) => {
        const attractionBox = event.target.closest(".attraction_box");
        if (attractionBox) {
            const attractionId = attractionBox.getAttribute("data-attractionid");
            if (attractionId) {
                window.location.href = `/attraction/${attractionId}`;
            }
        }
    });
});

window.addEventListener('scroll', handleScroll);

let nextPage = 1; 
let keyword = null;
let isLoading = false;

function loadNextPage() {
    console.log("[load] cur next page : " + nextPage); 
    if (!isLoading && nextPage!==null) {
        isLoading = true;
        let url;
        if(keyword===null) {
            url = `/api/attractions?page=${nextPage}`;
        }
        else{
            url = `/api/attractions?page=${nextPage}&keyword=${keyword}`;
        }
        fetch(url)
            .then(response => {
                if (response.status === 200) {
                    return response.json();
                } else {
                    throw new Error('Failed to fetch data');
                }
            })
            .then(data => {
                appendAttractions(data.data);
                nextPage = data.nextPage;
                isLoading = false;
                console.log("[load] cur next page : " + nextPage); 
            })
            .catch(error => {
                console.error('Error:', error);
                isLoading = false;
            });
    }
}

function appendAttractions(newAttractions) {
    const attractionsContainer = document.getElementById("attractions");
    
    newAttractions.forEach(attraction => {
        const attractionBox = document.createElement("div");
        attractionBox.classList.add("attraction_box");

        attractionBox.setAttribute("data-attractionID", attraction.id);
        
        const imgDiv = document.createElement("div");
        imgDiv.classList.add("img");
        
        const img = document.createElement("img");
        img.src = attraction.images[0];
        img.alt = attraction.name;
        
        const nameDiv = document.createElement("div");
        nameDiv.classList.add("name");
        nameDiv.innerText = attraction.name;
        
        imgDiv.appendChild(img);
        imgDiv.appendChild(nameDiv);
        
        const describeDiv = document.createElement("div");
        describeDiv.classList.add("describe");
        
        const mrtDiv = document.createElement("div");
        mrtDiv.classList.add("mrt");
        mrtDiv.innerText = attraction.mrt;
        
        const categoryDiv = document.createElement("div");
        categoryDiv.classList.add("category");
        categoryDiv.innerText = attraction.category;
        
        describeDiv.appendChild(mrtDiv);
        describeDiv.appendChild(categoryDiv);
        
        attractionBox.appendChild(imgDiv);
        attractionBox.appendChild(describeDiv);
        
        attractionsContainer.appendChild(attractionBox);
    });
    addEmpty(attractionsContainer.querySelectorAll(".attraction_box"));
}


function handleScroll() {
    const scrollY = window.scrollY;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;

    if (scrollY + windowHeight >= documentHeight - 100) {
        loadNextPage();
    }
}

//*CSS
function addEmpty(attractions) {
    const attractionsContainer = document.getElementById("attractions");
    const elementsInLastRow = attractions.length % 4;
    const placeholdersNeeded = elementsInLastRow === 0 ? 0 : 4 - elementsInLastRow;

    for (let i = 0; i < placeholdersNeeded; i++) {
        attractionsContainer.innerHTML += `
            <div class="empty"></div>
        `;
    }
}

