document.querySelector(".UnBooking").style.display = "none";


getData();

async function getData() {
    let token = localStorage.getItem("token");
    try {
        const userResponse = await fetch("/api/user/auth", {
            method: "GET",
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        const userData = await userResponse.json();
        if (userData.data == null) {
            window.location.href = "/";
        } else {
            const id = userData.data[0];
            const name = userData.data[1];
            const email = userData.data[2];
            document.querySelector(".signinName").innerText = name;

            const bookingResponse = await fetch("/api/booking", {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            const bookingData = await bookingResponse.json();
            console.log(bookingData);
            if (bookingData.error == true) {
                document.querySelector(".Booking").style.display = "none";
                document.querySelector(".UnBooking").style.display = "block";
                document.querySelector("footer").style.paddingBottom = "100%";
            } else {
                console.log(bookingData);
                console.log(bookingData.result.data.date);
                console.log("123");
                const attraction = bookingData.result.data.attraction;
                document.querySelector(".item_img").src = attraction.image;
                document.querySelector(".titleAttraction").innerText = attraction.name;
                
                changeDate=bookingData.result.data.date;
                date= new Date(changeDate);
                formattedDate= date.getFullYear().toString() + '-' +
                            (date.getMonth() + 1).toString().padStart(2, 0) + '-' +
                            date.getDate().toString().padStart(2, 0);
                document.querySelector(".date").innerText = formattedDate;

                changeTime = bookingData.result.data.time;
                console.log(changeTime)
                if ( changeTime === "上半天" ){
                    document.querySelector(".time").innerText = "早上9點到中午12點";
                }else{
                    document.querySelector(".time").innerText = "中午12點到下午4點";
                }
                // document.querySelector(".date").innerText =  bookingData.result.data.date;
                // document.querySelector(".time").innerText =  bookingData.result.data.time;
                document.querySelector(".price").innerText =  bookingData.result.data.price;
                document.querySelector(".address").innerText = attraction.address;


                const inputName = document.querySelector(".inputName");
                inputName.value = userData.data[1]
                const inputEmail = document.querySelector(".inputEmail");
                inputEmail.value = userData.data[2]
                document.querySelector(".totalPrice").innerText ="新台幣"+ bookingData.result.data.price +"元";

                document.querySelector(".deleteBtn").addEventListener("click", deleteOrder);
                async function deleteOrder() {
                    console.log("touch");
                    const entry = {
                        users_id : id,
                        attractionID: bookingData.result.data.attraction.id,
                        address: bookingData.result.data.attraction.address,
                        date: bookingData.result.data.date,
                        price: bookingData.result.data.price,
                        time: bookingData.result.data.time
                    };

                    const deleteResponse = await fetch("/api/booking", {
                        method: "DELETE",
                        body: JSON.stringify(entry),
                        headers: {
                            Authorization: `Bearer ${token}`,
                            "Content-Type": "application/json",
                        },
                    });

                    const deleteData = await deleteResponse.json();

                    if (deleteData.ok == true) {
                        alert("刪除預定行程成功！");
                        window.location.href = "/booking";
                    } else {
                        alert(deleteData.message);
                    }
                }
            }
        }
    } catch (error) {
        console.error(error);
    }
}


