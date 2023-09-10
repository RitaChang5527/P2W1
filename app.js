const mrtsContainer = document.getElementById("mrts");
const LBtn = document.getElementById("list-Lbtn");
const RBtn = document.getElementById("list-Rbtn");


let mrtsData = [];
let startIndex = 0;
let numVisibleMrts = 14; 
let scrollAmount = 10; 

function updateNumVisibleMrts() {
	if (window.innerWidth <= 360) {
		numVisibleMrts = 4;
		scrollAmount = 4; // Adjust for screens with width 360px or less
	} else if (window.innerWidth > 360 && window.innerWidth <= 600) {
		numVisibleMrts = 6;
		scrollAmount = 6; 
	} else if (window.innerWidth <= 1200) {
		numVisibleMrts = 8; 
		scrollAmount = 8;
	} else {
		numVisibleMrts = 14;
		scrollAmount = 10; 
	}
	renderMrts(); 
}

window.addEventListener("resize", updateNumVisibleMrts);

LBtn.addEventListener("click", function () {
    console.log("左按钮");
    scrollLeft();
});
RBtn.addEventListener("click", function () {
    console.log("右按钮");
    scrollRight();
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
		
        renderMrts();
    })
    .catch(error => {
        console.error('Error:', error);
    });

	renderMrts();

	function scrollLeft() {
		if (startIndex >= 1) { 
			startIndex -= scrollAmount;
			renderMrts();
		}
	}
	
	function scrollRight() {
		if (startIndex + numVisibleMrts < mrtsData.length - 1) {
			startIndex += scrollAmount;
			renderMrts();
		}
	}
	
	function renderMrts() {
		const visibleMrts = mrtsData.slice(startIndex, startIndex + numVisibleMrts);
		const mrtsHTML = visibleMrts.map(mrt => {
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
		})
		.catch(error => {
			console.error('Error:', error);
		});
}

let isLoading = false;
let isSearching = false;
let searchKeyword = '';

let scrollListener = handleScroll;
const searchBar = document.getElementById("search");
searchBar.addEventListener("input", function () {
    const searchText = searchBar.value.trim().toLowerCase();

    // 在搜索时更新搜索关键字
    searchKeyword = searchText;

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
        })
        .catch(error => {
            console.error('Error:', error);
        });
});

function renderAttractions(attractions) {
    const attractionsContainer = document.getElementById("attractions");
    if (attractions.length > 0) {
        const attractionsHTML = attractions.map(attraction => {
            return `
			<div class="attraction_box">
			<div class="img">
				<img src="${attraction.images[0]}" alt="${attraction.name}" />
				<div class="name">${attraction.name}</div>
			</div>
			<div class="describe">
				<div class="mrt">${attraction.mrt}</div>
				<div class="category">${attraction.category}</div>
			</div>
		</div>
            `;
        }).join('');

        attractionsContainer.innerHTML = attractionsHTML;
    } else {
        attractionsContainer.innerHTML = '<p>No results found.</p>';
    }
}

const container = document.getElementById("attractions");

fetch('/api/attractions')
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
		let { name: attraction_name, category: attraction_category, mrt: attraction_mrt, images: [attraction_image] } = item;
		//* 建box每個景點的<div>
		let attractionContainer = document.createElement("div");
		attractionContainer.classList.add("attraction_box"); //*加class
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

function appendAttractions(newAttractions) {
    const attractionsContainer = document.getElementById("attractions");
    const attractionsHTML = newAttractions.map(attraction => {
        return `
            <div class="attraction_box">
                <div class="img">
                    <img src="${attraction.images[0]}" alt="${attraction.name}" />
                    <div class="name">${attraction.name}</div>
                </div>
                <div class="describe">
                    <div class="mrt">${attraction.mrt}</div>
                    <div class="category">${attraction.category}</div>
                </div>
            </div>
        `;
    }).join('');
    
    attractionsContainer.innerHTML += attractionsHTML;
	addEmpty(attractionsContainer.querySelectorAll(".attraction_box"));
}

let nextPage = 1; 

function loadNextPage(searchText) {
    if (!isLoading) {
        isLoading = true;

        fetch(`/api/attractions?page=0&keyword=${searchText}`)
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
            })
            .catch(error => {
                console.error('Error:', error);
                isLoading = false;
            });
    }
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