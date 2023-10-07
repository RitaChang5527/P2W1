var fields = {
    number: {
        // css selector
        element: '#card-number',
        placeholder: '**** **** **** ****'
    },
    expirationDate: {
        // DOM object
        element: document.getElementById('card-expiration-date'),
        placeholder: 'MM / YY'
    },
    ccv: {
        element: '#card-ccv',
        placeholder: '後三碼'
    }
}


TPDirect.card.setup({
    fields: fields,
    styles: {
        // Style all elements
        'input': {
            'color': 'gray'
        },
        // Styling ccv field
        'input.ccv': {
            'font-size': '16px'
        },
        // Styling expiration-date field
        'input.expiration-date': {
            // 'font-size': '16px'
        },
        // Styling card-number field
        'input.card-number': {
            'font-size': '16px'
        },
        // style focus state
        ':focus': {
            'color': 'black'
        },
        // style valid state
        '.valid': {
            'color': 'green'
        },
        // style invalid state
        '.invalid': {
            'color': 'red'
        },
        // Media queries
        // Note that these apply to the iframe, not the root window.
        '@media screen and (max-width: 400px)': {
            'input': {
                'color': 'orange'
            }
        }
    },
    // 此設定會顯示卡號輸入正確後，會顯示前六後四碼信用卡卡號
    isMaskCreditCardNumber: true,
    maskCreditCardNumberRange: {
        beginIndex: 6, 
        endIndex: 11
    }
})

const submitButton = document.querySelector(".totalBtn");
submitButton.addEventListener("click", onSubmit);

let entry = {
    prime: "",
    order: { price: "", trip: { attraction: {} , date: "", time: "" }, contact: { name: "", email: "", phone: "" }},
};

async function onSubmit(event) {
    let token = localStorage.getItem("token");
    event.preventDefault();
    // 取得 TapPay Fields 的 status
    const tappayStatus = TPDirect.card.getTappayFieldsStatus();
    console.log(tappayStatus);
    // 確認是否可以 getPrime
    if (tappayStatus.canGetPrime === false) {
        alert("Can't get prime");
        return;
    }

  // Get prime
    TPDirect.card.getPrime(function (result) {
        if (result.status !== 0) {
        alert("get prime error " + result.msg);
        return;
        } else {
            const prime = result.card.prime;
            entry.prime = prime;
            const name = document.querySelector(".inputName").value;
            console.log(name);
            const email = document.querySelector(".inputEmail").value;
            console.log(email);
            const phone = document.querySelector(".inputPhone").value;
            console.log(phone);
            const price = document.querySelector(".price").innerText;
            console.log(price);
            const date = document.querySelector(".date").innerText;
            console.log(date);
            const time = document.querySelector(".time").innerText;
            console.log(time);
            entry.order.contact.name = name;
            console.log(entry.order.contact.name);
            entry.order.contact.email = email;
            console.log(entry.order.contact.email);
            entry.order.contact.phone = phone;
            console.log(entry.order.contact.phone);
            entry.order.price = price;
            console.log(entry.order.price);
            entry.order.trip.date = date;
            console.log(entry.order.date);
            entry.order.trip.time = time;
            console.log(entry.order.time);
        fetch("/api/booking", {
            method: "GET",
            headers: {
                Authorization: `Bearer ${token}`,
            },
            })
            .then(function (Response) {
                console.log(Response)
                return Response.json();
            })
            .then(function (data) {
                console.log(data);
                console.log(data.result.data.attraction);
                const attraction = data.result.data.attraction;
                console.log(attraction)
                entry.order.trip.attraction = attraction;
                console.log(entry.order.trip.attraction);
                fetch("/api/orders", {
                    method: "POST",
                    body: JSON.stringify(entry),
                    headers:({
                        Authorization: `Bearer ${token}`,
                        "content-Type": "application/json",
                    }),
                })
                .then(function (resp) {
                    console.log(resp)
                    return resp.json();
                })
                .then(function (data) {
                    console.log(data);
                    if (data.data.payment.status == 0) {
                        window.location.href = `/thankyou?number=${data.data.number}`;
                    } else {
                        alert("付款失敗!請重新輸入!");
                    }
                });
            })
            .catch(function (error) {
                console.error("Fetch Error:", error);
            });
        }
    });
}