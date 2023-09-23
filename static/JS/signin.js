//window.location.reload();

check() ;

//*點擊登入註冊
let sign = document.querySelector(".item-login");
sign.addEventListener("click", function () {
    document.querySelector(".sign").style.display = "block";
    document.querySelector(".loginBox").style.display = "block";
    document.querySelector(".signupBox").style.display = "none";
});
//*點擊關閉
let loginClose = document.querySelector(".close1");
const inputEmailL = document.getElementById("login_email");
const inputPasswordL = document.getElementById("login_password");
loginClose.addEventListener("click", function () {
    document.getElementById('message').innerText = "";
    inputEmailL.value="";
    inputPasswordL.value="";
    document.querySelector(".sign").style.display = "none";
});
let signupClose = document.querySelector(".close2");
const inputNameS = document.getElementById("signup_name");
const inputEmailS = document.getElementById("signup_email");
const inputPasswordS = document.getElementById("signup_password");
signupClose.addEventListener("click", function () {
    document.getElementById('message2').innerText = "";
    inputNameS.value="";
    inputEmailS.value="";
    inputPasswordS.value="";
    document.querySelector(".sign").style.display = "none";
});

//*點此註冊    
let switchToSignup = document.querySelector(".notice1");
const inputEmailL1 = document.getElementById("login_email");
const inputPasswordL1 = document.getElementById("login_password");
switchToSignup.addEventListener("click", function () {
    document.getElementById('message').innerText = "";
    inputEmailL1.value="";
    inputPasswordL1.value="";
    document.querySelector(".loginBox").style.display = "none";
    document.querySelector(".signupBox").style.display = "block";
});
//*點擊登入
let switchToLogin = document.querySelector(".notice2");
const inputNameS1 = document.getElementById("signup_name");
const inputEmailS1 = document.getElementById("signup_email");
const inputPasswordS1 = document.getElementById("signup_password");
switchToLogin.addEventListener("click", function () {
    document.getElementById('message2').innerText = "";
    inputNameS1.value="";
    inputEmailS1.value="";
    inputPasswordS1.value="";
    document.querySelector(".loginBox").style.display = "block";
    document.querySelector(".signupBox").style.display = "none";
});




//signupBtn
const signupBtn = document.querySelector(".signupBtn");
signupBtn.addEventListener("click",signup);
//*signUP
function signup() {
    const signupName = document.getElementById("signup_name").value;
    const signupEmail = document.getElementById("signup_email").value;
    const signupPassword = document.getElementById("signup_password").value;
    
    if (!signupName || !signupEmail || !signupPassword) {
        document.getElementById('message2').innerText = "請輸入註冊資料";
        return; 
    }
    let entry = {
        name: signupName,
        email: signupEmail,
        password: signupPassword,
    }; 
    let url = "/api/user";
    fetch(url, {
        method: "POST",
        body: JSON.stringify(entry), 
        headers: {
            "Content-Type": "application/json",
        }
    })
    .then(function (response) {
        console.log(response)
        return response.json();
        
    })
    .then(function (data) {
        if (Boolean(data["ok"])) {
            console.log("Registration successful. Showing success message.");
            document.getElementById('message2').innerText = "帳號註冊成功，請點選登入";

        }else if (Boolean(data["error"])) {
            document.getElementById('message2').innerText = "註冊失敗，email已被註冊，請重新輸入";
        }
    })
}

//loginBtn
const loginBtn = document.querySelector(".loginBtn");
loginBtn.addEventListener("click", login);
//處理login
async function login() {
    const url = "/api/user/auth";
    const email = document.getElementById("login_email").value;
    const password = document.getElementById("login_password").value;

        
    if ( !email || !password) {
        document.getElementById('message').innerText = "請輸入帳號密碼";
        return; 
    }

    try {
        console.log("input:", JSON.stringify({
            email: email,
            password: password
        }));
        
        const response = await fetch(url, {
            method: "PUT",
            body: JSON.stringify({
                email: email,
                password: password
            }),
            headers: {
                "Content-Type": "application/json"
            },
        });
        if (response.ok) {
            //data: resultData;
            const data = await response.json();
            console.log("data: " + data["error"]);
            if (Boolean(data["error"])) {
                console.log("rsp_e");
                document.getElementById('message').innerText = "登入錯誤";
                console.log("rsp_2");
            }else {
                check();
            }
        } else {
            const token = data.token;
            console.log(token)
            document.cookie = `token=${token}; path=/; expires=${checkExpiration()}`;
            throw new Error("fail");
        }
    } catch (error) {
        console.log("error", error);
    }
}


function checkExpiration() {
    const Date = new Date();
    expirationDate.setDate(Date.getDate() + 7);
    return expirationDate.toUTCString();
}

//signout
const signout = document.querySelector(".item-signout");
signout.addEventListener("click", function () {
    fetch("/api/user/auth", {
        method: "DELETE",
    })
    .then(function (response) {
        return response.json();
    })
    .then(function (data) {
        if (data.ok == true) {
            window.location.href = "/";
            document.querySelector(".item-login").style.display = "block";
            document.querySelector(".item-signout").style.display = "none";
        }
    });
});

async function check() {
    await fetch("/api/user/auth")
    .then(function (response) {
        console.log(response)
        return response.json();
        
    })
    .then(function (data) {
        console.log(data)
        if (data.data !== null) {
            document.querySelector(".sign").style.display = "none";
            document.querySelector(".item-login").style.display = "none";
            document.querySelector(".item-signout").style.display = "block";
        }else{
            document.querySelector(".item-login").style.display = "block";
            document.querySelector(".item-signout").style.display = "none";
        }
    });
}