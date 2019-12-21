function checkname() {
    var name = document.getElementById("name-txt");
    var sign = document.getElementById("sign-name");
    var reName = document.getElementById("re-name");
    if (name.value.length == 0) {
        reName.style.visibility = 'visible';
        sign.style.backgroundImage = "url(../img/cross.png)";
        document.getElementsByClassName("input-wrap")[0].style.borderColor = 'rgba(255, 0, 0, 0.9)';
        return false;
    } else {
        reName.style.visibility = 'hidden';
        sign.style.backgroundImage = "url(../img/tick.png)";
        document.getElementsByClassName("input-wrap")[0].style.borderColor = 'rgb(200, 200, 200, 0.9)';
        return true;
    }
}

function checkpw1() {
    var pw1 = document.getElementById("pw1");
    var sign = document.getElementById("sign-pw1");
    var rePw1 = document.getElementById("re-pw1");
    if (pw1.value.length < 6) {
        rePw1.style.visibility = 'visible';
        sign.style.backgroundImage = "url(../img/cross.png)";
        document.getElementsByClassName("input-wrap")[1].style.borderColor = 'rgba(255, 0, 0, 0.9)';
        return false;
    } else {
        rePw1.style.visibility = "hidden";
        sign.style.backgroundImage = "url(../img/tick.png)";
        document.getElementsByClassName("input-wrap")[1].style.borderColor = 'rgb(200, 200, 200, 0.9)';
        return true;
    }
}

function checkpw2() {
    var pw1 = document.getElementById("pw1");
    var pw2 = document.getElementById("pw2");
    var sign = document.getElementById("sign-pw2");
    var rePw2 = document.getElementById("re-pw2");
    if (pw1.value != pw2.value) {
        rePw2.style.visibility = 'visible';
        sign.style.backgroundImage = "url(../img/cross.png)";
        document.getElementsByClassName("input-wrap")[2].style.borderColor = 'rgba(255, 0, 0, 0.9)';
        return false;
    } else {
        rePw2.style.visibility = 'hidden';
        sign.style.backgroundImage = "url(../img/tick.png)";
        document.getElementsByClassName("input-wrap")[2].style.borderColor = 'rgb(200, 200, 200, 0.9)';
        return true;
    }
}

function checkinfo() {
    return checkname() && checkpw1() && checkpw2();
}