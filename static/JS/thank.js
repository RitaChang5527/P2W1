let token = localStorage.getItem("token");
fetch("/api/orders", {
    method: "GET",
    headers:({
        Authorization: `Bearer ${token}`,
    }),
})
.then(function (resp) {
    console.log(resp)
    return resp.json();
})
.then(function (data) {
    console.log(data);
    const orderId = data.data.number;
    document.querySelector(".order_number").innerHTML = orderId;
});