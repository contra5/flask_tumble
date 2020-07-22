var split_url = document.location.pathname.split('/')

if (split_url[2] == "post") {
    var post_num = Number(document.location.pathname.split('/')[3])
    function next_url() {
        return "/" + site_name + "/post/" + (post_num + 1);
    }

    function prev_url() {
        return "/" + site_name + "/post/" + (post_num - 1);
    }
} else {
    var post_num = Number(document.location.pathname.split('/')[4])
    var tag = document.location.pathname.split('/')[3]

    function next_url() {
        return "/" + site_name + "/tag/" + tag + "/" + (post_num + 1);
    }

    function prev_url() {
        return "/" + site_name + "/tag/" + tag + "/" + (post_num - 1);
    }

}

var site_name = document.location.pathname.split('/')[1]



if (isNaN(post_num)) {
    post_num = 1;
}



$(document).keydown(function (e) {
    if (e.keyCode == 39) {
        window.location = next_url();
    } else if (e.keyCode == 37) {
        window.location = prev_url();
    }
});

document.getElementById("nextBtn").onclick = function () {
    location.href = next_url();
};

document.getElementById("prevBtn").onclick = function () {
    location.href = prev_url();
};

document.getElementById("homeBtn").onclick = function () {
    location.href = "/";
};

document.getElementById("rawBtn").onclick = function () {
    location.href = "/" + site_name + "/post_raw/" + true_post_num;
};

document.getElementById("lstBtn").onclick = function () {
    location.href = "/" + site_name + "/list";
};

document.getElementById("taglstBtn").onclick = function () {
    location.href = "/" + site_name + "/tag_list";
};

